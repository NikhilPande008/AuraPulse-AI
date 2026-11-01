import pytest
from pydantic import ValidationError

from backend.app.agents.aura_vision import create_baseline_wedding_plan
from backend.app.schemas import (
    BOQItem,
    CrisisTrigger,
    CrisisTriggerType,
    MasterEventPlan,
    PriorityTier,
)


def test_boq_item_strict_validation():
    # Valid item
    item = BOQItem(
        item_id="boq_test_1",
        category="Floral",
        name="Exotic Marigold Wall",
        specification="100 sq ft woven floral curtain",
        quantity=1.0,
        unit="lot",
        estimated_rate_inr=50000.0,
        total_cost_inr=50000.0,
        priority=PriorityTier.DISCRETIONARY,
        status="ACTIVE"
    )
    assert item.item_id == "boq_test_1"
    assert item.priority == PriorityTier.DISCRETIONARY

    # Strict type violation check: wrong quantity type
    with pytest.raises(ValidationError):
        BOQItem(
            item_id="boq_test_fail",
            category="Lighting",
            name="Strobe Lights",
            specification="Bad data",
            quantity="invalid_number",  # strict=True rejects non-float string
            unit="units",
            estimated_rate_inr=1000.0,
            total_cost_inr=1000.0,
            priority=PriorityTier.OPERATIONAL
        )


def test_master_event_plan_structure():
    plan = create_baseline_wedding_plan(headcount=300, city="Mumbai", budget=2500000.0)
    assert plan.location_city == "Mumbai"
    assert len(plan.boq) > 0
    assert len(plan.schedule) > 0
    assert any(item.priority == PriorityTier.CRITICAL for item in plan.boq)
    assert any(item.priority == PriorityTier.DISCRETIONARY for item in plan.boq)

    # Validate json serialization round-trip
    dumped = plan.model_dump_json()
    reconstructed = MasterEventPlan.model_validate_json(dumped)
    assert reconstructed.event_id == plan.event_id
    assert len(reconstructed.boq) == len(plan.boq)


def test_crisis_trigger_model():
    trigger = CrisisTrigger(
        trigger_type=CrisisTriggerType.BUDGET_COMPRESSION,
        description="Emergency budget contraction of 20%",
        budget_cut_percent=20.0
    )
    assert trigger.trigger_type == CrisisTriggerType.BUDGET_COMPRESSION
    assert trigger.budget_cut_percent == 20.0
