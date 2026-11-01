from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.app.agents.aura_vision import create_baseline_wedding_plan
from backend.app.integrations.google_calendar import (
    generate_calendar_ics,
    generate_google_calendar_web_intent,
)
from backend.app.integrations.google_maps import fetch_verified_vendors
from backend.app.integrations.google_sheets import export_event_to_google_sheets
from backend.app.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_places_api_new_parsing():
    """
    Verifies Places API (New) https://places.googleapis.com/v1/places:searchText
    parses displayName, formattedAddress, rating, userRatingCount, nationalPhoneNumber, googleMapsUri.
    """
    mock_places_response = {
        "places": [
            {
                "id": "places/ChIJ_test_nashik_sound",
                "displayName": {"text": "Peshwa Acoustic & Trussing"},
                "formattedAddress": "Gangapur Road, Nashik, Maharashtra 422005",
                "rating": 4.8,
                "userRatingCount": 210,
                "nationalPhoneNumber": "+91 253 234 5678",
                "googleMapsUri": "https://maps.google.com/?cid=123456789",
            }
        ]
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json = MagicMock(return_value=mock_places_response)

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp):
        with patch("backend.app.config.settings.GOOGLE_MAPS_API_KEY", "mock_key_123"):
            data = await fetch_verified_vendors(query="sound and light rental", city="Nashik", min_rating=4.5)
            assert data["is_configured"] is True
            assert data["status"] == "ACTIVE"
            vendors = data["vendors"]
            assert len(vendors) == 1
            v = vendors[0]
            assert v["name"] == "Peshwa Acoustic & Trussing"
            assert v["rating"] == 4.8
            assert v["user_ratings_total"] == 210
            assert v["phone"] == "+91 253 234 5678"
            assert "googleMapsUri" in v["google_maps_uri"] or "maps.google.com" in v["google_maps_uri"]
            assert v["is_verified"] is True


@pytest.mark.asyncio
async def test_places_api_honest_fallback_unconfigured():
    """
    Verifies that when Maps API key is unset or error occurs,
    an empty vendor list is returned with status 'SIMULATED' and is_configured: false.
    Never marks unverified or mock vendors with is_verified: True.
    """
    with patch("backend.app.config.settings.GOOGLE_MAPS_API_KEY", ""):
        data = await fetch_verified_vendors(query="decor", city="Pune")
        assert data["is_configured"] is False
        assert data["status"] == "SIMULATED"
        assert len(data["vendors"]) == 0


def test_rfc5545_calendar_export_ics():
    """
    Verifies standard RFC-5545 .ics generation:
    - Milestones as all-day events on due_date.
    - Day-of schedule blocks on event_date with TZID=Asia/Kolkata.
    - CRLF line endings (\\r\\n).
    """
    plan = create_baseline_wedding_plan()
    ics_text = generate_calendar_ics(plan)

    # 1. Standard RFC-5545 headers & line endings
    assert "BEGIN:VCALENDAR\r\n" in ics_text
    assert "VERSION:2.0\r\n" in ics_text
    assert "END:VCALENDAR\r\n" in ics_text
    assert "TZID:Asia/Kolkata\r\n" in ics_text

    # 2. Milestones as all-day events
    assert "DTSTART;VALUE=DATE:" in ics_text
    assert "DTEND;VALUE=DATE:" in ics_text

    # 3. Timed schedule blocks with Asia/Kolkata timezone
    assert "DTSTART;TZID=Asia/Kolkata:" in ics_text
    assert "DTEND;TZID=Asia/Kolkata:" in ics_text
    assert "SUMMARY:" in ics_text
    assert "LOCATION:" in ics_text


def test_calendar_ics_api_endpoint():
    """
    Verifies POST /api/v1/export/calendar-ics returns 200 and valid .ics content.
    """
    plan = create_baseline_wedding_plan()
    response = client.post("/api/v1/export/calendar-ics", json=plan.model_dump())
    assert response.status_code == 200
    assert "text/calendar" in response.headers["content-type"]
    assert "attachment; filename=" in response.headers["content-disposition"]
    content = response.text
    assert "BEGIN:VCALENDAR" in content
    assert "END:VCALENDAR" in content
    assert "TZID:Asia/Kolkata" in content


def test_google_calendar_web_intent():
    """
    Verifies generation of zero-permission Google Calendar web intent links.
    """
    intent = generate_google_calendar_web_intent(
        title="Royal Sangeet Night",
        start_iso="20261115T180000",
        end_iso="20261115T230000",
        details="Music and dance celebration",
        location="Jaipur Palace",
    )
    assert "https://calendar.google.com/calendar/render" in intent
    assert "action=TEMPLATE" in intent
    assert "ctz=Asia%2FKolkata" in intent or "ctz=Asia/Kolkata" in intent
    assert "Royal+Sangeet+Night" in intent or "Royal%20Sangeet%20Night" in intent


def test_google_sheets_export_formulas():
    """Without credentials, Sheets export raises instead of returning a fake SUCCESS link."""
    import pytest

    from backend.app.integrations.google_sheets import SheetsNotConfiguredError

    plan = create_baseline_wedding_plan()
    boq_dicts = [item.model_dump() for item in plan.boq]
    with pytest.raises(SheetsNotConfiguredError):
        export_event_to_google_sheets(spreadsheet_title="Test Royal Wedding", boq_items=boq_dicts)


def test_ics_escaping_folding_and_crlf():
    """Verify RFC-5545 escaping of special characters, 75-octet line folding, and CRLF."""
    plan = create_baseline_wedding_plan()
    plan.title = "Grand Wedding, Reception; Dinner & Dance \\ Celebration with an exceptionally long description exceeding seventy-five characters on a single line"
    ics_text = generate_calendar_ics(plan)

    # 1. Ends with CRLF
    assert ics_text.endswith("\r\n")
    # 2. Every line ends with CRLF
    for line in ics_text.split("\r\n"):
        assert len(line.encode("utf-8")) <= 75
    # 3. Escaped characters present
    assert "\\," in ics_text or "\\;" in ics_text or "\\\\" in ics_text
