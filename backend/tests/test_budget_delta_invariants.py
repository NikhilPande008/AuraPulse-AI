"""Tests verifying mathematical invariants on budget_delta_inr across all copilot intents and pulse triggers."""

import pytest
from fastapi.testclient import TestClient

from backend.app.fixtures import create_baseline_wedding_plan, create_preset_meadow_wedding
from backend.app.main import app

client = TestClient(app)

COPILOT_PROMPTS = [
    "Cut budget by 20% across all flexible items",
    "Cut florals by 20% and add a live solo saxophonist",
    "add 50 guests",
    "set guests to 250",
    "50 मेहमान कम करो",
    "Suggest 5 interactive games for 30th birthday and add a Game Master",
    "Add Sakhar Puda ceremony and pooja samagri audit to timeline",
    "Switch catering to authentic Puneri Maharashtrian menu with Puran Poli and Modaks",
    "Shift event date to 2027-01-15",
    "Move it 2 weeks earlier",
    "Write a python script to calculate fibonacci numbers",
    "General event optimization advice",
]

PULSE_TRIGGERS = [
    {"trigger_type": "WEATHER_RISK", "description": "Heavy rainfall expected during outdoor ceremony"},
    {"trigger_type": "BUDGET_COMPRESSION", "description": "Sponsor dropped out, cut 15%", "budget_cut_percent": 15.0},
    {"trigger_type": "TIMELINE_SLIPPAGE", "description": "Highway delay stalled delivery trucks by 2 hours"},
    {
        "trigger_type": "SUPPLY_FAILURE",
        "description": "Primary catering vendor cancelled",
        "affected_vendor_category": "Catering",
    },
]


@pytest.mark.parametrize("prompt", COPILOT_PROMPTS)
def test_copilot_budget_delta_invariant(prompt: str):
    """Verify that whenever copilot returns a diff, budget_delta_inr == round(new - original, 2)."""
    plan = create_preset_meadow_wedding()
    payload = {"event_plan": plan.model_dump(), "user_prompt": prompt}
    response = client.post("/api/v1/aura/chat-copilot", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    diff = data.get("contingency_diff") or data.get("diff")
    if diff:
        orig = diff["original_total_inr"]
        new = diff["new_total_inr"]
        delta = diff["budget_delta_inr"]
        assert delta == round(new - orig, 2), f"Prompt '{prompt}': delta {delta} != round({new} - {orig}, 2)"


@pytest.mark.parametrize("trigger", PULSE_TRIGGERS)
def test_pulse_simulate_budget_delta_invariant(trigger: dict):
    """Verify that /pulse/simulate response always satisfies budget_delta_inr == round(new - original, 2)."""
    plan = create_baseline_wedding_plan()
    payload = {"plan": plan.model_dump(), "trigger": trigger}
    response = client.post("/api/v1/pulse/simulate", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    orig = data["original_total_inr"]
    new = data["new_total_inr"]
    delta = data["budget_delta_inr"]
    assert delta == round(
        new - orig, 2
    ), f"Trigger {trigger['trigger_type']}: delta {delta} != round({new} - {orig}, 2)"
