import json
import pytest
from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from pydantic import ValidationError

from backend.app.main import app
from backend.app.schemas import (
    PlanRequest,
    DeconstructRequest,
    MasterEventPlan,
    BOQItem,
    PriorityTier,
    MilestonePhase,
)
from backend.app.services.timeline import build_milestones, get_backwards_date
from backend.app.agents.copilot import (
    execute_scale_budget,
    chat_copilot,
)
from backend.app.fixtures.sample_plans import create_preset_meadow_wedding

client = TestClient(app)


def test_timeline_backwards_calculation():
    """
    Unit test: test_timeline_backwards_calculation
    Verifies date arithmetic for 3 months, 3 weeks, and leap years.
    """
    # 1. Leap year arithmetic: 2028-03-01 minus 14 days must yield 2028-02-16
    leap_date = get_backwards_date("2028-03-01", 14)
    assert leap_date == "2028-02-16"

    # 2. Event scheduled 3 months away (~90 days)
    three_months_date = (date.today() + timedelta(days=90)).strftime("%Y-%m-%d")
    ms_3m = build_milestones(three_months_date, "wedding", "Maharashtrian")
    assert len(ms_3m) == 6
    # T-6 Months (-180d) falls in the past -> must be compressed into "Do Immediately"
    do_immediately_phases = [m for m in ms_3m if m.phase == MilestonePhase.DO_IMMEDIATELY]
    assert len(do_immediately_phases) >= 1
    # Ensure no past dates are emitted
    today_str = date.today().strftime("%Y-%m-%d")
    for m in ms_3m:
        assert m.due_date >= today_str

    # 3. Short horizon: Event scheduled 3 weeks away (21 days)
    three_weeks_date = (date.today() + timedelta(days=21)).strftime("%Y-%m-%d")
    ms_3w = build_milestones(three_weeks_date, "birthday")
    assert len(ms_3w) == 6
    # T-6, T-3, T-1 all fall in past -> must be compressed into "Do Immediately"
    compressed = [m for m in ms_3w if m.phase == MilestonePhase.DO_IMMEDIATELY]
    assert len(compressed) >= 3
    for m in ms_3w:
        assert m.due_date >= today_str


def test_budget_scaling():
    """
    Unit test: test_budget_scaling
    Verifies scale_budget(-20) reduces non-critical items and leaves Tier-1 intact.
    """
    plan = create_preset_meadow_wedding()
    original_total = plan.current_estimated_total

    # Identify items by tier before scaling
    critical_before = {it.item_id: (it.estimated_rate_inr, it.total_cost_inr) for it in plan.boq if it.priority == PriorityTier.CRITICAL}
    operational_before = {it.item_id: (it.estimated_rate_inr, it.total_cost_inr) for it in plan.boq if it.priority != PriorityTier.CRITICAL}

    assert len(critical_before) > 0
    assert len(operational_before) > 0

    # Scale budget down 20%
    scaled_plan, diff = execute_scale_budget(plan, -20.0)

    # 1. Tier-1 Critical items remain 100% locked
    for it in scaled_plan.boq:
        if it.priority == PriorityTier.CRITICAL:
            orig_rate, orig_total = critical_before[it.item_id]
            assert it.estimated_rate_inr == orig_rate
            assert it.total_cost_inr == orig_total

    # 2. Non-critical items (Operational & Discretionary) are reduced by 20%
    for it in scaled_plan.boq:
        if it.priority != PriorityTier.CRITICAL:
            orig_rate, orig_total = operational_before[it.item_id]
            assert it.estimated_rate_inr == round(orig_rate * 0.8, 2)
            assert it.total_cost_inr == round(orig_total * 0.8, 2)
            assert it.status == "MODIFIED"

    # 3. Invariants: total matches exact sum and diff payload generated
    expected_sum = round(sum(it.total_cost_inr for it in scaled_plan.boq if it.status != "DROPPED"), 2)
    assert scaled_plan.current_estimated_total == expected_sum
    assert scaled_plan.current_estimated_total < original_total

    assert diff is not None
    assert diff.budget_delta_inr < 0
    assert len(diff.boq_diffs) == len(plan.boq)


def test_validation_boundaries():
    """
    Unit test: test_validation_boundaries
    Verifies rejection of ₹0 budgets, negative guests, and past dates.
    """
    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

    # 1. Valid request baseline
    valid_req = PlanRequest(
        city="Pune",
        headcount=200,
        budget=1500000.0,
        event_date=tomorrow,
        event_type="wedding"
    )
    assert valid_req.city == "Pune"
    assert valid_req.budget == 1500000.0

    # 2. Rejection of ₹0 budget
    with pytest.raises(ValidationError):
        PlanRequest(city="Pune", headcount=200, budget=0.0, event_date=tomorrow)

    # 3. Rejection of negative budget
    with pytest.raises(ValidationError):
        PlanRequest(city="Pune", headcount=200, budget=-50000.0, event_date=tomorrow)

    # 4. Rejection of negative / zero guests
    with pytest.raises(ValidationError):
        PlanRequest(city="Pune", headcount=0, budget=500000.0, event_date=tomorrow)
    with pytest.raises(ValidationError):
        PlanRequest(city="Pune", headcount=-50, budget=500000.0, event_date=tomorrow)

    # 5. Rejection of past dates
    with pytest.raises(ValidationError):
        PlanRequest(city="Pune", headcount=100, budget=500000.0, event_date=yesterday)
    with pytest.raises(ValidationError):
        PlanRequest(city="Pune", headcount=100, budget=500000.0, event_date="2020-01-01")

    # 6. Rejection of excess budget (> 5 Crores)
    with pytest.raises(ValidationError):
        PlanRequest(city="Pune", headcount=100, budget=60000000.0, event_date=tomorrow)

    # 7. Rejection of excess headcount (> 10,000)
    with pytest.raises(ValidationError):
        PlanRequest(city="Pune", headcount=15000, budget=1000000.0, event_date=tomorrow)


def test_no_implicit_preset_fallback_and_503_error():
    """
    CR-06: Verifies that unrecognized presets or custom requests never silently
    fall back to canned presets, and raise HTTP 503 GENERATION_FAILED when Gemini fails.
    """
    # 1. Recognized preset returns 200
    res_preset = client.post("/api/v1/aura/deconstruct", json={
        "moodboard_preset": "meadow_wedding",
        "headcount": 300,
        "city": "Pune",
        "budget": 1500000.0,
        "event_type": "wedding"
    })
    assert res_preset.status_code == 200
    plan = res_preset.json()
    assert plan["event_type"] == "wedding"

    # 2. Unrecognized preset / custom parameters without Gemini API connectivity
    # Must NOT return canned meadow_wedding; must return HTTP 503 GENERATION_FAILED
    res_custom = client.post("/api/v1/aura/deconstruct", json={
        "moodboard_preset": "unrecognized_custom_preset_123",
        "headcount": 150,
        "city": "Nashik",
        "budget": 800000.0,
        "event_type": "wedding"
    })
    assert res_custom.status_code == 503
    err = res_custom.json()
    assert err["code"] == "GENERATION_FAILED"
    assert "Failed to generate event plan via Gemini" in err["message"]


@pytest.mark.asyncio
async def test_copilot_tool_budget_cut_endpoint():
    """
    CR-11: Verifies conversational copilot handles budget cut prompt by
    scaling non-critical items and returning a diff payload.
    """
    plan = create_preset_meadow_wedding()
    payload = {
        "event_plan": plan.model_dump(),
        "user_prompt": "Cut budget by 20% across all flexible items"
    }
    response = client.post("/api/v1/aura/chat-copilot", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "copilot_reply" in data
    assert "diff" in data and data["diff"] is not None
    diff = data["diff"]
    assert diff["budget_delta_inr"] < 0
    assert data["updated_plan"]["current_estimated_total"] < plan.current_estimated_total


@pytest.mark.asyncio
async def test_copilot_language_awareness_marathi_hindi():
    """
    CR-11: Verifies Co-Pilot responds in matching language for Hindi & Marathi prompts.
    """
    plan = create_preset_meadow_wedding()

    # Marathi
    res_mr = await chat_copilot(
        event_plan=plan,
        user_prompt="मेनू पूर्णपणे शाकाहारी करा आणि पुरणपोळी जोडा"
    )
    assert any(word in res_mr["copilot_reply"] for word in ["शाकाहारी", "पुरणपोळी", "मोदक", "बदलण्यात"])

    # Hindi
    res_hi = await chat_copilot(
        event_plan=plan,
        user_prompt="मेनू को शाकाहारी करो और थाली में बदलाव करो"
    )
    assert any(word in res_hi["copilot_reply"] for word in ["शाकाहारी", "पूरन पोली", "थाली", "परिवर्तित"])


@pytest.mark.asyncio
async def test_mocked_gemini_custom_plan_generation():
    """
    CR-08: Verifies asynchronous Gemini plan generation with schema validation
    when processing a custom input (Marathi wedding in Nashik for ₹12L).
    """
    from backend.app.schemas import EventIdea, ScheduleBlock
    from backend.app.llm.client import generate_event_plan

    fake_plan_data = {
        "event_id": "evt_nashik_001",
        "event_type": "wedding",
        "title": "Authentic Marathi Wedding in Nashik",
        "location_city": "Nashik",
        "currency": "INR",
        "total_budget_limit": 1200000.0,
        "current_estimated_total": 1150000.0,
        "event_date": "2027-02-15",
        "culture_region": "Maharashtrian",
        "theme": "Traditional Peshwai & Marigold",
        "ideas": [
            {"title": "Live Tutari & Dhol Tasha Ingress", "rationale": "Authentic royal arrival", "estimated_cost": 35000.0},
            {"title": "Puran Poli & Modak Culinary Stage", "rationale": "Pure-ghee traditional banquet", "estimated_cost": 450000.0}
        ],
        "boq": [
            {
                "item_id": "boq_n01", "category": "Catering", "name": "Peshwai Maharashtrian Feast",
                "specification": "Puran Poli, Katachi Amti, Kothimbir Vadi, Ukdiche Modak for 300 pax",
                "quantity": 300.0, "unit": "pax", "estimated_rate_inr": 1500.0, "total_cost_inr": 450000.0,
                "priority": "Critical", "status": "ACTIVE"
            },
            {
                "item_id": "boq_n02", "category": "Rituals", "name": "Mandap & Antarpat Setup",
                "specification": "Authentic wooden mandap with yellow marigold garlands and handwoven Antarpat",
                "quantity": 1.0, "unit": "lot", "estimated_rate_inr": 180000.0, "total_cost_inr": 180000.0,
                "priority": "Critical", "status": "ACTIVE"
            }
        ],
        "schedule": [
            {
                "block_id": "sch_n01", "phase": "Arrival & Seemant Pujan", "start_time_iso": "09:00",
                "end_time_iso": "10:30", "activity": "Welcoming groom side with brass thalis",
                "responsible_party": "Family Leads", "is_outdoor": False
            }
        ],
        "planning_milestones": [],
        "vendor_checklist": []
    }

    mock_resp = MagicMock()
    mock_resp.text = json.dumps(fake_plan_data)

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_resp)

    req = PlanRequest(
        event_type="wedding",
        event_date="2027-02-15",
        city="Nashik",
        headcount=300,
        budget=1200000.0,
        culture_region="Maharashtrian",
        theme="Traditional Peshwai & Marigold",
    )

    with patch("backend.app.llm.client.get_genai_client", return_value=mock_client):
        plan = await generate_event_plan(req)

        assert plan.location_city == "Nashik"
        assert plan.event_type == "wedding"
        assert plan.culture_region == "Maharashtrian"
        assert plan.total_budget_limit == 1200000.0
        assert plan.current_estimated_total <= plan.total_budget_limit
        assert len(plan.boq) == 2
        # Check that dynamic backwards milestones were generated
        assert len(plan.planning_milestones) == 6
        assert any("sakhar" in m.title.lower() or "puran poli" in m.title.lower() for m in plan.planning_milestones)
        # Check idea structure
        assert len(plan.ideas) == 2
        assert plan.ideas[0].title == "Live Tutari & Dhol Tasha Ingress"

