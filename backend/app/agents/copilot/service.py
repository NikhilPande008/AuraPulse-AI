"""Copilot service orchestration: Gemini tool calling with deterministic offline fallback."""

from typing import Any

from ...schemas.event_plan import MasterEventPlan
from .gemini_path import run_gemini_path
from .offline import run_offline


async def chat_copilot(
    event_plan: MasterEventPlan,
    user_prompt: str,
    history: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Conversational Ideas and Budget Co-Pilot entry point.

    Attempts Gemini tool calling with function execution first. Falls back
    to the offline deterministic intent handler when Gemini is unreachable.

    Args:
        event_plan: The current MasterEventPlan state.
        user_prompt: User natural language instruction or query.
        history: Optional list of previous chat message turns.

    Returns:
        Dict conforming to CopilotResponse wire format containing copilot_reply,
        updated_plan, suggested_ideas, diff, mode, and declined.
    """
    result = await run_gemini_path(event_plan, user_prompt, history)
    if result is None:
        result = run_offline(event_plan, user_prompt)

    return result.to_dict()
