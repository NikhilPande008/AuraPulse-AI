import pytest

from backend.app.agents.aura_vision import create_baseline_wedding_plan
from backend.app.agents.pulse_engine import evaluate_contingency
from backend.app.schemas import (
    CrisisTrigger,
    CrisisTriggerType,
    DiffAction,
    PriorityTier,
)


@pytest.mark.asyncio
async def test_weather_risk_contingency():
    plan = create_baseline_wedding_plan()
    trigger = CrisisTrigger(
        trigger_type=CrisisTriggerType.WEATHER_RISK,
        description="Flash rain alert: 85% probability in 2 hours",
        weather_condition="Heavy Downpour",
    )

    diff = await evaluate_contingency(plan=plan, trigger=trigger)
    assert diff.trigger.trigger_type == CrisisTriggerType.WEATHER_RISK
    # Emergency canopy was added
    added_items = [d for d in diff.boq_diffs if d.action == DiffAction.ADDED]
    assert len(added_items) == 1
    assert "Canopy" in added_items[0].updated_item.name or "Marquee" in added_items[0].updated_item.name

    # Outdoor blocks were re-routed to protected zone
    for sched_diff in diff.schedule_diffs:
        assert sched_diff.updated_block.is_outdoor is False


@pytest.mark.asyncio
async def test_budget_compression_contingency():
    plan = create_baseline_wedding_plan()
    original_total = plan.current_estimated_total
    trigger = CrisisTrigger(
        trigger_type=CrisisTriggerType.BUDGET_COMPRESSION,
        description="Client requests urgent 20% budget cut",
        budget_cut_percent=20.0,
    )

    diff = await evaluate_contingency(plan=plan, trigger=trigger)
    assert diff.new_total_inr < original_total
    # Critical tier items must remain untouched (only Discretionary trimmed or dropped)
    critical_in_updated = [item for item in diff.updated_plan.boq if item.priority == PriorityTier.CRITICAL]
    assert len(critical_in_updated) >= 3
    assert all(item.status == "ACTIVE" for item in critical_in_updated)


@pytest.mark.asyncio
async def test_timeline_slippage_contingency():
    plan = create_baseline_wedding_plan()
    trigger = CrisisTrigger(
        trigger_type=CrisisTriggerType.TIMELINE_SLIPPAGE,
        description="Baraat arrival stuck in traffic, delayed 60 minutes",
        delay_minutes=60,
    )

    diff = await evaluate_contingency(plan=plan, trigger=trigger)
    assert len(diff.schedule_diffs) > 0
    # Procession block should be shifted
    procession = next(s for s in diff.updated_plan.schedule if "Baraat" in s.phase)
    assert procession.start_time_iso == "19:00"  # was 18:00 + 60 min
