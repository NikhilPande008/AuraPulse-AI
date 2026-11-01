"""Offline deterministic intent handling and replanning pipeline."""

from ....schemas.contingency import ContingencyDiff
from ....schemas.event_plan import MasterEventPlan
from ..models import CopilotResult
from . import messages
from .intents import INTENT_HANDLERS
from .language import detect_language, normalize_prompt


def run_offline(plan: MasterEventPlan, prompt: str, lang: str | None = None) -> CopilotResult:
    """Execute the offline deterministic intent pipeline.

    Matches user prompt against an ordered chain of intent handlers (budget cuts,
    headcount, date shifts, dietary/cultural changes, refusals) and produces
    structured modifications.

    Args:
        plan: Current MasterEventPlan.
        prompt: User's raw text prompt.
        lang: Optional ISO language code ("en", "hi", "mr"). Auto-detected if None.

    Returns:
        CopilotResult containing reply, updated_plan, diff, and suggested ideas.
    """
    if lang is None:
        lang = detect_language(prompt, getattr(plan, "language", None))
    prompt_norm = normalize_prompt(prompt)

    result = None
    for handler in INTENT_HANDLERS:
        if handler.matches(prompt_norm):
            result = handler.apply(plan, prompt_norm, lang)
            break

    if result is None:
        # Fallback guaranteed by DefaultIntentHandler
        result = INTENT_HANDLERS[-1].apply(plan, prompt_norm, lang)

    if result.diff is not None:
        result.diff.original_total_inr = plan.current_estimated_total
        result.diff.new_total_inr = result.updated_plan.current_estimated_total
        result.diff.budget_delta_inr = round(
            result.updated_plan.current_estimated_total - plan.current_estimated_total, 2
        )

    return result


def _execute_deterministic_copilot(
    event_plan: MasterEventPlan,
    user_prompt: str,
    prompt_lower: str | None = None,
    lang: str | None = None,
) -> tuple[MasterEventPlan, ContingencyDiff | None, str, list[str]]:
    """Legacy backward-compatible adapter for tests."""
    result = run_offline(event_plan, user_prompt, lang=lang)
    return result.updated_plan, result.diff, result.reply, result.suggested_ideas


def _generate_suggested_ideas(plan: MasterEventPlan, prompt_lower: str, lang: str) -> list[str]:
    """Provides grounded contextual follow-ups in the active language."""
    return messages.SUGGESTED_IDEAS_BY_LANG.get(lang, messages.SUGGESTED_IDEAS_BY_LANG["en"])


__all__ = [
    "_execute_deterministic_copilot",
    "_generate_suggested_ideas",
    "run_offline",
]
