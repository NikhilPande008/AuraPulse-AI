import os

import pytest
from backend.app.llm.client import generate_event_plan
from backend.app.schemas import PlanRequest


@pytest.mark.live
@pytest.mark.asyncio
async def test_live_gemini_generation():
    """Live integration test against Gemini API (opt-in via -m live or RUN_LIVE_TESTS=true)."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or os.getenv("RUN_LIVE_TESTS", "false").lower() != "true":
        pytest.skip("RUN_LIVE_TESTS != true or GEMINI_API_KEY missing; skipping live test")

    request = PlanRequest(
        event_type="birthday",
        city="Pune",
        headcount=50,
        budget=100000.0,
        theme="Retro Arcade",
    )
    plan = await generate_event_plan(request)
    assert plan.event_type == "birthday"
    assert plan.location_city == "Pune"
    assert len(plan.boq) > 0
    assert plan.current_estimated_total <= plan.total_budget_limit
