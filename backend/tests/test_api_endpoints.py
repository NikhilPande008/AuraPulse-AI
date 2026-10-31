import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.schemas import CrisisTriggerType

client = TestClient(app)


def test_health_endpoint():
    """Verify GET /api/health returns 200 and healthy status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "engine_flash" in data
    assert "engine_pro" in data


def test_deconstruct_endpoint():
    """Verify POST /api/v1/aura/deconstruct validates schema and returns MasterEventPlan."""
    payload = {
        "moodboard_preset": "meadow_wedding",
        "headcount": 300,
        "locality": "Pune",
        "budget_ceiling": 1500000.0,
        "event_type": "wedding"
    }
    response = client.post("/api/v1/aura/deconstruct", json=payload)
    assert response.status_code == 200
    plan = response.json()
    assert "event_id" in plan
    assert plan["event_type"] == "wedding"
    assert plan["location_city"] == "Pune"
    assert len(plan["boq"]) > 0
    assert len(plan["schedule"]) > 0
    assert plan["total_budget_limit"] == 1500000.0
    assert plan["current_estimated_total"] > 0


def test_simulate_contingency_endpoint():
    """Verify POST /api/v1/pulse/simulate calculates and returns valid ContingencyDiff."""
    # First get a valid baseline plan
    plan_res = client.post("/api/v1/aura/deconstruct", json={
        "moodboard_preset": "meadow_wedding",
        "headcount": 300,
        "locality": "Pune",
        "budget_ceiling": 1500000.0,
        "event_type": "wedding"
    })
    assert plan_res.status_code == 200
    plan = plan_res.json()

    # Simulate Weather Crisis
    sim_payload = {
        "plan": plan,
        "trigger": {
            "trigger_type": CrisisTriggerType.WEATHER_RISK.value,
            "description": "Flash storm incoming in 2 hours",
            "weather_condition": "Severe Torrential Rain"
        }
    }
    response = client.post("/api/v1/pulse/simulate", json=sim_payload)
    assert response.status_code == 200
    diff = response.json()
    assert "diff_id" in diff
    assert "boq_diffs" in diff
    assert len(diff["boq_diffs"]) > 0

    # Verify presence of state mutation actions: ADDED or MODIFIED
    actions = {d["action"] for d in diff["boq_diffs"]}
    assert "ADDED" in actions or "MODIFIED" in actions


def test_vendor_discovery_endpoint():
    """Verify GET /api/v1/integrations/vendors returns valid schema and honest status."""
    response = client.get("/api/v1/integrations/vendors?query=floral&city=Pune&min_rating=4.0")
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Pune"
    assert "vendors" in data
    assert "is_configured" in data
    assert "status" in data


def test_sheets_export_endpoint():
    """Verify POST /api/v1/integrations/sheets/export produces formula workbook."""
    payload = {
        "spreadsheet_title": "Test Smoke Suite",
        "boq_items": [
            {
                "item_id": "test_1",
                "name": "Bamboo Pergola",
                "category": "Infrastructure",
                "specification": "Weather proof",
                "quantity": 1,
                "unit": "lot",
                "estimated_rate_inr": 180000,
                "total_cost_inr": 180000,
                "priority": "Critical",
                "status": "ACTIVE"
            }
        ]
    }
    response = client.post("/api/v1/integrations/sheets/export", json=payload)
    # Without service-account credentials the API must NOT fabricate a docs.google.com link.
    assert response.status_code == 503
    res_data = response.json()
    assert res_data["code"] == "SHEETS_NOT_CONFIGURED"
    assert "spreadsheet_url" not in res_data
