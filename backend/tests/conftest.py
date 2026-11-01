import pytest
from pydantic import SecretStr

from backend.app.config import settings


@pytest.fixture(autouse=True)
def test_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sets standard testing environment without external network calls and without rate limits."""
    monkeypatch.setattr(settings, "DISABLE_RATE_LIMIT", True)
    monkeypatch.setattr(settings, "GEMINI_API_KEY", SecretStr(""))
    monkeypatch.setattr(settings, "GOOGLE_MAPS_API_KEY", SecretStr(""))
    monkeypatch.setattr(settings, "GOOGLE_APPLICATION_CREDENTIALS", "")
