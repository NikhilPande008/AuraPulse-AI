import pytest
from backend.app.integrations.google_maps import fetch_verified_vendors
from backend.app.integrations.google_sheets import export_event_to_google_sheets
from backend.app.integrations.google_calendar import sync_schedule_to_google_calendar
from backend.app.agents.aura_vision import create_baseline_wedding_plan


@pytest.mark.asyncio
async def test_google_maps_vendor_fetch():
    vendors = await fetch_verified_vendors(query="sound and light rental", city="Jaipur", min_rating=4.5)
    assert len(vendors) > 0
    assert "name" in vendors[0]
    assert "rating" in vendors[0]
    assert vendors[0]["rating"] >= 4.0
    assert vendors[0]["is_verified"] is True


def test_google_sheets_export_formulas():
    plan = create_baseline_wedding_plan()
    boq_dicts = [item.model_dump() for item in plan.boq]
    result = export_event_to_google_sheets(
        spreadsheet_title="Test Royal Wedding",
        boq_items=boq_dicts
    )
    assert result["status"] == "SUCCESS"
    assert result["items_exported"] == len(boq_dicts)
    assert "=SUM(" in result["grand_total_formula"]
    assert "priority_formulas" in result
    assert "=SUMIF(" in result["priority_formulas"]["Critical Tier Formula"]


def test_google_calendar_schedule_sync():
    plan = create_baseline_wedding_plan()
    sched_dicts = [b.model_dump() for b in plan.schedule]
    res = sync_schedule_to_google_calendar(
        calendar_id="primary",
        event_title="Jaipur Destination Wedding",
        schedule_blocks=sched_dicts
    )
    assert res["status"] == "SUCCESS"
    assert res["total_blocks_synced"] == len(sched_dicts)
    assert len(res["synced_events"]) > 0
