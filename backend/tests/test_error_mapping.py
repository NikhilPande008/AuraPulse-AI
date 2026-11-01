"""Unit tests for typed Gemini exception mapping and route rate limits."""

from unittest.mock import patch

from fastapi.testclient import TestClient
from pydantic import SecretStr

from backend.app.fixtures.sample_plans import create_preset_meadow_wedding
from backend.app.llm.client import (
    GeminiBadOutputError,
    GeminiQuotaError,
    GeminiUnavailableError,
)
from backend.app.main import app

client = TestClient(app, raise_server_exceptions=False)


def test_gemini_unavailable_maps_to_503():
    """GeminiUnavailableError raised during plan generation must return HTTP 503."""
    with patch("backend.app.api.routes.aura.deconstruct_moodboard", side_effect=GeminiUnavailableError("Upstream 503")):
        resp = client.post(
            "/api/v1/aura/deconstruct",
            json={
                "event_type": "wedding",
                "city": "Pune",
                "budget": 1500000.0,
                "headcount": 300,
            },
        )
        assert resp.status_code == 503
        data = resp.json()
        assert data["code"] == "GEMINI_UNAVAILABLE"


def test_gemini_quota_maps_to_429():
    """GeminiQuotaError raised during plan generation must return HTTP 429."""
    with patch("backend.app.api.routes.aura.deconstruct_moodboard", side_effect=GeminiQuotaError("Quota exceeded")):
        resp = client.post(
            "/api/v1/aura/deconstruct",
            json={
                "event_type": "wedding",
                "city": "Pune",
                "budget": 1500000.0,
                "headcount": 300,
            },
        )
        assert resp.status_code == 429
        data = resp.json()
        assert data["code"] == "GEMINI_QUOTA_EXCEEDED"


def test_gemini_bad_output_maps_to_502():
    """GeminiBadOutputError raised during plan generation must return HTTP 502."""
    with patch("backend.app.api.routes.aura.deconstruct_moodboard", side_effect=GeminiBadOutputError("Corrupted JSON")):
        resp = client.post(
            "/api/v1/aura/deconstruct",
            json={
                "event_type": "wedding",
                "city": "Pune",
                "budget": 1500000.0,
                "headcount": 300,
            },
        )
        assert resp.status_code == 502
        data = resp.json()
        assert data["code"] == "GEMINI_BAD_OUTPUT"


def test_studio_render_sanitizes_errors():
    """POST /api/v1/studio/render-alternative falls back gracefully without leaking tracebacks."""
    with patch("backend.app.config.settings.GEMINI_API_KEY", SecretStr("")):
        resp = client.post(
            "/api/v1/studio/render-alternative",
            json={
                "prompt_description": "Waterproof glass marquee canopy under heavy monsoon rain",
                "theme": "Monsoon Palace",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "FALLBACK"
        assert data["is_generated"] is False
        assert "sample image" in data["error"]
        assert "Traceback" not in data["error"]


def test_copilot_chat_handles_bad_output_gracefully():
    """Copilot endpoint degrades to offline rules when Gemini outputs bad format."""
    plan = create_preset_meadow_wedding()
    with patch("backend.app.agents.copilot.gemini_path.run_gemini_path", return_value=None):
        resp = client.post(
            "/api/v1/aura/chat-copilot",
            json={
                "event_plan": plan.model_dump(),
                "user_prompt": "Cut budget by 15%",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["mode"] == "offline_rules"
        assert "diff" in data and data["diff"] is not None
