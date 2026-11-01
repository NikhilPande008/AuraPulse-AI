from unittest.mock import MagicMock, patch

from pydantic import SecretStr

from backend.app.config import Settings, settings
from backend.app.llm.client import _CLIENT_HOLDER, get_genai_client


def test_secret_never_exposed_in_str_or_repr() -> None:
    """str(settings.GEMINI_API_KEY) and repr(settings) must never contain the raw secret."""
    raw_secret = "dummy_secret_value_for_testing"
    cfg = Settings(
        GEMINI_API_KEY=SecretStr(raw_secret),
        GOOGLE_MAPS_API_KEY=SecretStr(raw_secret),
    )

    # SecretStr masking in str()
    assert str(cfg.GEMINI_API_KEY) == "**********"
    assert raw_secret not in str(cfg.GEMINI_API_KEY)
    assert raw_secret not in repr(cfg)

    # get_secret_value() via helper methods exposes unmasked key cleanly
    assert cfg.gemini_api_key() == raw_secret
    assert cfg.google_maps_api_key() == raw_secret


def test_genai_client_receives_unmasked_key() -> None:
    """When GEMINI_API_KEY is configured, genai.Client receives the unmasked string."""
    test_key = "test-key-123"
    _CLIENT_HOLDER.clear()

    mock_client_factory = MagicMock(return_value=MagicMock())
    with (
        patch.object(settings, "GEMINI_API_KEY", SecretStr(test_key)),
        patch("backend.app.llm.client._GENAI_AVAILABLE", True),
        patch("backend.app.llm.client.genai.Client", mock_client_factory),
    ):
        client = get_genai_client()
        assert client is not None
        mock_client_factory.assert_called_once_with(api_key=test_key)

    _CLIENT_HOLDER.clear()
