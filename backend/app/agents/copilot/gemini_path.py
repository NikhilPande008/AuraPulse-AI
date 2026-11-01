"""Gemini-powered tool calling pipeline for Co-Pilot."""

import json
import logging
import os
from typing import Any, cast

import backend.app.agents.copilot as copilot_pkg
from backend.app.agents.copilot.dispatch import TOOL_REGISTRY
from backend.app.agents.copilot.models import CopilotResult
from backend.app.agents.copilot.offline import _generate_suggested_ideas
from backend.app.agents.copilot.offline.language import detect_language
from backend.app.agents.copilot.tools import COPILOT_TOOLS
from backend.app.config import settings
from backend.app.core.constants import COPILOT_TIMEOUT
from backend.app.prompts import load_prompt
from backend.app.schemas.contingency import ContingencyDiff
from backend.app.schemas.event_plan import MasterEventPlan

logger = logging.getLogger("aurapulse.copilot.gemini")

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None  # type: ignore[assignment]
    types = None  # type: ignore[assignment]


def is_gemini_available() -> bool:
    """Checks if Gemini client and API key are configured."""
    key = getattr(copilot_pkg, "settings", settings).GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
    return bool(key and genai)


def _build_plan_context(event_plan: MasterEventPlan) -> dict[str, Any]:
    """Builds a compact summary of the active plan for Gemini context."""
    compact_boq = [
        {
            "item_id": it.item_id,
            "name": it.name,
            "category": it.category,
            "quantity": it.quantity,
            "unit": it.unit,
            "rate": it.estimated_rate_inr,
            "priority": it.priority.value,
            "status": it.status,
        }
        for it in event_plan.boq
        if it.status != "DROPPED"
    ]
    return {
        "title": event_plan.title,
        "city": event_plan.location_city,
        "event_date": event_plan.event_date,
        "headcount": getattr(event_plan, "headcount", 100),
        "budget_ceiling": event_plan.total_budget_limit,
        "current_spend": event_plan.current_estimated_total,
        "active_boq_items": compact_boq[:30],
        "milestones": [{"title": m.title, "due_date": m.due_date} for m in (event_plan.planning_milestones or [])[:8]],
    }


def _build_contents(plan_context: dict[str, Any], user_prompt: str, history: list[dict[str, str]] | None) -> list[Any]:
    """Assembles multi-turn message history and current prompt payload."""
    contents: list[Any] = []
    for h in (history or [])[-6:]:
        role = "user" if h.get("role") in ("user", "human") else "model"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=h.get("content", ""))]))

    user_turn = (
        f"<active_plan_context>\n{json.dumps(plan_context, indent=2)}\n</active_plan_context>\n\n"
        f"User Request: {user_prompt}"
    )
    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=user_turn)]))
    return contents


def _execute_single_call(
    call: Any, plan: MasterEventPlan
) -> tuple[MasterEventPlan, ContingencyDiff | None, bool, str | None]:
    fn_name = getattr(call, "name", "")
    fn_args = getattr(call, "args", {}) or {}
    handler = TOOL_REGISTRY.get(fn_name)
    if not handler:
        return plan, None, False, None
    try:
        new_plan, diff, reply, is_declined = handler(plan, fn_args)
        if is_declined:
            return plan, None, True, reply
        return new_plan, diff, False, None
    except Exception as e:  # noqa: BLE001
        logger.warning(f"Error executing function call {fn_name}: {e}")
        return plan, None, False, None


def _dispatch_function_calls(
    function_calls: list[Any], event_plan: MasterEventPlan
) -> tuple[MasterEventPlan, ContingencyDiff | None, bool, str | None]:
    """Iterates through function calls and dispatches via TOOL_REGISTRY."""
    updated_plan = event_plan.model_copy(deep=True)
    active_diff: ContingencyDiff | None = None

    for call in function_calls:
        updated_plan, diff, is_declined, declined_reply = _execute_single_call(call, updated_plan)
        if is_declined:
            return event_plan, None, True, declined_reply
        if diff:
            active_diff = diff

    return updated_plan, active_diff, False, None


def _resolve_reply_text(response: Any, active_diff: ContingencyDiff | None, user_prompt: str) -> str:
    """Extracts conversational response text or falls back to diff narrative."""
    reply_text = getattr(response, "text", "") or ""
    if not reply_text:
        if active_diff:
            return active_diff.summary_narrative
        return f"Processed request: '{user_prompt}'."
    return reply_text


async def run_gemini_path(
    event_plan: MasterEventPlan,
    user_prompt: str,
    history: list[dict[str, str]] | None = None,
) -> CopilotResult | None:
    """Attempts to run conversational copilot through Gemini 2.5 Flash."""
    if not is_gemini_available():
        return None

    try:
        system_instruction = load_prompt("copilot_system.v1.md")

        plan_context = _build_plan_context(event_plan)
        contents = _build_contents(plan_context, user_prompt, history)

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=cast(list[Any], list(COPILOT_TOOLS)),
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            temperature=0.2,
        )

        response = await copilot_pkg.generate(
            model=getattr(copilot_pkg, "settings", settings).GEMINI_FLASH_MODEL,
            contents=contents,
            config=config,
            timeout=COPILOT_TIMEOUT,
        )

        tool_executed = False
        updated_plan = event_plan.model_copy(deep=True)
        active_diff: ContingencyDiff | None = None

        if hasattr(response, "function_calls") and response.function_calls:
            tool_executed = True
            updated_plan, active_diff, is_declined, decline_msg = _dispatch_function_calls(
                response.function_calls, event_plan
            )
            if is_declined and decline_msg:
                return CopilotResult(
                    updated_plan=event_plan,
                    diff=None,
                    reply=decline_msg,
                    suggested_ideas=[],
                    declined=True,
                    mode="gemini_function_calling",
                )

        reply_text = _resolve_reply_text(response, active_diff, user_prompt)
        lang = detect_language(user_prompt, getattr(event_plan, "language", None))
        ideas = _generate_suggested_ideas(updated_plan, user_prompt.lower(), lang)

        return CopilotResult(
            updated_plan=updated_plan,
            diff=active_diff,
            reply=reply_text,
            suggested_ideas=ideas,
            declined=False,
            mode="gemini_function_calling" if tool_executed else "gemini_chat",
        )
    except Exception as e:  # noqa: BLE001
        logger.warning(f"Gemini Co-Pilot bypassed to offline deterministic solver: {e}")
        return None
