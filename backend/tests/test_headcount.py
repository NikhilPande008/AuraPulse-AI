import pytest

from backend.app.agents.copilot import (
    _execute_deterministic_copilot,
    apply_tool_call,
    execute_set_headcount,
)
from backend.app.fixtures.sample_plans import create_preset_meadow_wedding


def test_add_50_guests_increases_from_300_to_350():
    plan = create_preset_meadow_wedding()
    assert plan.headcount == 300

    updated_plan, diff, reply, ideas = _execute_deterministic_copilot(
        event_plan=plan,
        user_prompt="add 50 guests"
    )

    assert updated_plan.headcount == 350
    assert diff is not None
    assert "350" in reply
    # Verify per-head BOQ items scaled by 350/300
    pax_items = [i for i in updated_plan.boq if "pax" in i.unit.lower()]
    assert len(pax_items) > 0
    for it in pax_items:
        assert it.quantity == 350.0


def test_set_guests_to_250_is_absolute():
    plan = create_preset_meadow_wedding()
    assert plan.headcount == 300

    updated_plan, diff, reply, ideas = _execute_deterministic_copilot(
        event_plan=plan,
        user_prompt="set guests to 250"
    )

    assert updated_plan.headcount == 250
    assert diff is not None
    assert "250" in reply
    pax_items = [i for i in updated_plan.boq if "pax" in i.unit.lower()]
    assert len(pax_items) > 0
    for it in pax_items:
        assert it.quantity == 250.0


def test_change_headcount_out_of_range_warns():
    plan = create_preset_meadow_wedding()
    assert plan.headcount == 300

    # Upper bound exceedance
    updated_plan, diff, reply, ideas = _execute_deterministic_copilot(
        event_plan=plan,
        user_prompt="add 20000 guests"
    )
    assert updated_plan.headcount == 300
    assert diff is None
    assert "Warning" in reply or "between 1 and 10,000" in reply

    # Direct function call ValueError validation
    with pytest.raises(ValueError) as excinfo:
        execute_set_headcount(plan, 0)
    assert "between 1 and 10000" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        execute_set_headcount(plan, 15000)
    assert "between 1 and 10000" in str(excinfo.value)


def test_copilot_dispatches_change_headcount():
    plan = create_preset_meadow_wedding()
    assert plan.headcount == 300

    new_plan, diff, msg = apply_tool_call(
        plan=plan,
        tool_name="change_headcount",
        args={"delta": 50}
    )
    assert new_plan.headcount == 350
    assert diff is not None
    assert "Changed headcount by 50" in msg


def test_hindi_and_marathi_headcount_updates():
    plan = create_preset_meadow_wedding()

    # Hindi Devanagari digit: ५० मेहमान जोड़ो
    plan_hi, diff_hi, reply_hi, _ = _execute_deterministic_copilot(
        event_plan=plan,
        user_prompt="५० मेहमान जोड़ो",
        lang="hi"
    )
    assert plan_hi.headcount == 350

    # Marathi absolute: पाहुणे २५० करा
    plan_mr, diff_mr, reply_mr, _ = _execute_deterministic_copilot(
        event_plan=plan,
        user_prompt="पाहुणे २५० करा",
        lang="mr"
    )
    assert plan_mr.headcount == 250
