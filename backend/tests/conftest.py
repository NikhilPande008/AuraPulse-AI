import os
import pytest
from backend.app.config import settings

@pytest.fixture(autouse=True)
def test_environment(monkeypatch):
    """Sets standard testing environment without external network calls and without rate limits."""
    monkeypatch.setenv("DISABLE_RATE_LIMIT", "true")
    monkeypatch.setenv("GEMINI_API_KEY", "")
    monkeypatch.setenv("GOOGLE_MAPS_API_KEY", "")
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "")
    monkeypatch.setattr(settings, "GOOGLE_MAPS_API_KEY", "")
    monkeypatch.setattr(settings, "GOOGLE_APPLICATION_CREDENTIALS", "")
