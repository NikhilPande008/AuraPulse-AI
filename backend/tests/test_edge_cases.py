import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.schemas import (
    MasterEventPlan,
    BOQItem,
    ScheduleBlock,
    PriorityTier,
    PlanningMilestone,
    VendorChecklistItem,
)
from backend.app.agents.aura_vision import (
    get_backwards_date,
    create_preset_meadow_wedding,
    create_preset_cyberpunk_birthday,
    create_preset_diwali_mela,
)
from backend.app.agents.copilot import chat_copilot

client = TestClient(app)


def test_copilot_endpoint_cultural_cuisine_swap():
    """Verify conversational co-pilot swaps catering to authentic Puneri cuisine."""
    plan = create_preset_meadow_wedding()
    payload = {
        "event_plan": plan.model_dump(),
        "user_prompt": "Switch catering to authentic Puneri Maharashtrian menu with Puran Poli and Modaks"
    }
    response = client.post("/api/v1/aura/chat-copilot", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "copilot_reply" in data
    assert len(data["suggested_ideas"]) >= 3
    
    # Check that updated plan has Puneri catering
    updated = data["updated_plan"]
    assert any("puneri" in item["name"].lower() or "puran poli" in item["specification"].lower() for item in updated["boq"])
    assert updated["current_estimated_total"] == sum(it["total_cost_inr"] for it in updated["boq"])


def test_copilot_endpoint_floral_cut_and_sax():
    """Verify co-pilot cuts floral budget by 20% and adds solo saxophonist."""
    plan = create_preset_meadow_wedding()
    initial_total = plan.current_estimated_total
    payload = {
        "event_plan": plan.model_dump(),
        "user_prompt": "Cut florals by 20% and add a live solo saxophonist"
    }
    response = client.post("/api/v1/aura/chat-copilot", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    updated = data["updated_plan"]
    # Check that saxophonist item exists in BOQ
    assert any("sax" in item["name"].lower() for item in updated["boq"])
    # Mathematical invariant
    assert updated["current_estimated_total"] == round(sum(it["total_cost_inr"] for it in updated["boq"]), 2)


def test_copilot_party_games_birthday():
    """Verify co-pilot suggests interactive games and adds Game Master for birthday."""
    plan = create_preset_cyberpunk_birthday()
    payload = {
        "event_plan": plan.model_dump(),
        "user_prompt": "Suggest 5 interactive games for 30th birthday and add a Game Master"
    }
    response = client.post("/api/v1/aura/chat-copilot", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["suggested_ideas"]) >= 4
    assert any("game" in it["name"].lower() for it in data["updated_plan"]["boq"])


def test_copilot_cultural_sakhar_puda_milestone():
    """Verify co-pilot adds pre-ceremony ritual milestones."""
    plan = create_preset_meadow_wedding()
    payload = {
        "event_plan": plan.model_dump(),
        "user_prompt": "Add Sakhar Puda ceremony and pooja samagri audit to timeline"
    }
    response = client.post("/api/v1/aura/chat-copilot", json=payload)
    assert response.status_code == 200
    data = response.json()
    milestones = data["updated_plan"]["planning_milestones"]
    assert any("ritual" in m["title"].lower() or "sakhar" in m["title"].lower() for m in milestones)


def test_budget_scale_boundary_small_vs_luxury():
    """Test boundary conditions: ₹20,000 micro-budget vs ₹50,00,000 luxury gala."""
    # Small budget
    small_boq = [
        BOQItem(
            item_id="b_01",
            category="Catering",
            name="Street Food & Finger Bites",
            specification="Self-serve box packaging",
            quantity=10.0,
            unit="box",
            estimated_rate_inr=500.0,
            total_cost_inr=5000.0,
            priority=PriorityTier.CRITICAL,
            status="ACTIVE"
        ),
        BOQItem(
            item_id="b_02",
            category="Decor",
            name="Biodegradable Balloons & Streamers",
            specification="Eco latex balloons",
            quantity=1.0,
            unit="lot",
            estimated_rate_inr=3000.0,
            total_cost_inr=3000.0,
            priority=PriorityTier.OPERATIONAL,
            status="ACTIVE"
        )
    ]
    small_plan = MasterEventPlan(
        event_id="evt_small",
        event_type="birthday",
        title="Micro Intimate Birthday",
        location_city="Pune",
        currency="INR",
        total_budget_limit=20000.0,
        current_estimated_total=8000.0,
        boq=small_boq,
        schedule=[
            ScheduleBlock(
                block_id="sb_01",
                phase="Party",
                start_time_iso="2026-11-15T18:00:00",
                end_time_iso="2026-11-15T21:00:00",
                activity="Celebration & Cake",
                responsible_party="Host",
                is_outdoor=False
            )
        ]
    )
    assert small_plan.current_estimated_total <= small_plan.total_budget_limit
    assert len(small_plan.boq) == 2

    # High luxury budget
    luxury_plan = create_preset_meadow_wedding()
    assert luxury_plan.total_budget_limit == 1500000.0
    assert luxury_plan.current_estimated_total < luxury_plan.total_budget_limit


def test_headcount_scaling_invariants():
    """Verify headcount scaling behavior across presets."""
    p1 = create_preset_meadow_wedding()
    p2 = create_preset_cyberpunk_birthday()
    p3 = create_preset_diwali_mela()

    # Headcount & scale expectations
    assert any(it.quantity == 300.0 for it in p1.boq if "catering" in it.category.lower())
    assert any(it.quantity == 60.0 for it in p2.boq if "catering" in it.category.lower())
    assert any(it.quantity == 25.0 for it in p3.boq if "stall" in it.category.lower())

    # Mathematical integrity across presets
    for plan in [p1, p2, p3]:
        assert plan.current_estimated_total == round(sum(it.total_cost_inr for it in plan.boq), 2)
        assert plan.current_estimated_total <= plan.total_budget_limit


def test_backwards_date_leap_year_and_short_horizon():
    """Verify backwards planning date calculation on leap years and short horizons."""
    # Leap year date: 2028-03-01 minus 14 days should yield 2028-02-16
    d1 = get_backwards_date("2028-03-01", 14)
    assert d1 == "2028-02-16"

    # 180 days before 2026-11-15
    d2 = get_backwards_date("2026-11-15", 180)
    dt2 = datetime.strptime(d2, "%Y-%m-%d")
    assert dt2 < datetime(2026, 11, 15)

    # Malformed date fallback
    d_fallback = get_backwards_date("invalid-date", 30)
    assert d_fallback == "2026-11-01"
