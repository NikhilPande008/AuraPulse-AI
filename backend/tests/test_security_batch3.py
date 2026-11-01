import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import SecretStr

from backend.app.agents.copilot import chat_copilot
from backend.app.fixtures.sample_plans import create_preset_meadow_wedding
from backend.app.main import SlidingWindowLimiter, get_client_ip


def test_spoofed_leftmost_xff_does_not_bypass_limit():
    """Attackers spoofing leftmost X-Forwarded-For should not evade the rate limiter when TRUSTED_PROXY_HOPS is 1."""
    limiter = SlidingWindowLimiter(per_minute=2, per_day=10)
    client_ip = "203.0.113.195"

    # Direct IP recorded twice reaches limit
    assert limiter.check_and_record(client_ip) is True
    assert limiter.check_and_record(client_ip) is True
    assert limiter.check_and_record(client_ip) is False

    # Mock request with spoofed leftmost IP and real client IP at right
    mock_request = MagicMock()
    mock_request.headers = {"x-forwarded-for": f"10.0.0.1, 10.0.0.2, {client_ip}"}
    resolved_ip = get_client_ip(mock_request)
    assert resolved_ip == client_ip

    # Now verify limiter rejects the resolved IP
    assert limiter.check_and_record(resolved_ip) is False


def test_limiter_prunes_old_entries():
    """SlidingWindowLimiter drops entries > 24h and removes empty keys from memory."""
    limiter = SlidingWindowLimiter(per_minute=5, per_day=20)
    now = time.time()

    # Seed with an entry 25 hours ago
    old_time = now - (25 * 3600)
    limiter._minute_buckets["stale_ip"] = [old_time]
    limiter._day_buckets["stale_ip"] = [old_time]

    # Seed with an active entry
    limiter._minute_buckets["active_ip"] = [now - 10]
    limiter._day_buckets["active_ip"] = [now - 10]

    limiter.prune(now=now)

    # stale_ip must be completely deleted
    assert "stale_ip" not in limiter._minute_buckets
    assert "stale_ip" not in limiter._day_buckets

    # active_ip must remain
    assert "active_ip" in limiter._minute_buckets
    assert "active_ip" in limiter._day_buckets


@pytest.mark.asyncio
async def test_copilot_system_prompt_in_config_not_contents():
    """Verify Gemini Copilot passes system_instruction in GenerateContentConfig and not in contents."""
    plan = create_preset_meadow_wedding()

    mock_response = MagicMock()
    mock_response.text = "Plan updated"
    mock_response.function_calls = []

    with (
        patch("backend.app.config.settings.GEMINI_API_KEY", SecretStr("mock_key")),
        patch("backend.app.agents.copilot.gemini_path.generate", new_callable=AsyncMock) as mock_generate,
    ):
        mock_generate.return_value = mock_response

        _ = await chat_copilot(
            event_plan=plan, user_prompt="Add a floral centerpiece", history=[{"role": "user", "content": "hello"}]
        )

        assert mock_generate.called
        call_kwargs = mock_generate.call_args.kwargs
        contents = call_kwargs["contents"]
        config = call_kwargs["config"]

        # Check config contains system_instruction
        assert hasattr(config, "system_instruction")
        assert config.system_instruction is not None
        assert (
            "AuraPulse Co-Pilot" in config.system_instruction or "event architect" in config.system_instruction.lower()
        )

        # Check contents only contain user/model Content turns, NOT raw system_instruction string
        for c in contents:
            # Each content is a Content object with a role ('user' or 'model')
            assert hasattr(c, "role")
            assert c.role in ("user", "model")
            for part in c.parts:
                assert "You are Aura Copilot" not in part.text
