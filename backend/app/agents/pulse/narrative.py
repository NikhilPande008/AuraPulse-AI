"""AI narrative generation for Pulse Engine crisis scenarios."""

from typing import Any

import google.api_core.exceptions
import httpx

from ...config import settings
from ...core.constants import CRISIS_NARRATIVE_TIMEOUT
from ...llm.client import _GENAI_AVAILABLE, GeminiError, generate
from ...prompts import load_prompt
from ...schemas import CrisisTrigger, MasterEventPlan


def _format_narrative_prompt(
    plan: MasterEventPlan,
    trigger: CrisisTrigger,
    original_total: float,
    new_total: float,
    ceiling: float,
    boq_diffs_len: int,
    schedule_diffs_len: int,
) -> str:
    template = load_prompt("pulse_narrative.v1.md")
    return template.format(
        title=plan.title,
        location_city=plan.location_city,
        trigger_type=trigger.trigger_type,
        description=trigger.description,
        original_total=f"{original_total:,.2f}",
        new_total=f"{new_total:,.2f}",
        ceiling=f"{ceiling:,.2f}",
        boq_diffs_len=boq_diffs_len,
        schedule_diffs_len=schedule_diffs_len,
    )


def _extract_response_text(res: object) -> str | None:
    text = getattr(res, "text", None)
    return str(text).strip() if text else None


async def _generate_crisis_narrative(
    plan: MasterEventPlan,
    trigger: CrisisTrigger,
    original_total: float,
    new_total: float,
    ceiling: float,
    boq_diffs_len: int,
    schedule_diffs_len: int,
) -> str | None:
    api_key = settings.gemini_api_key()
    if not (api_key and _GENAI_AVAILABLE):
        return None
    try:
        prompt = _format_narrative_prompt(
            plan, trigger, original_total, new_total, ceiling, boq_diffs_len, schedule_diffs_len
        )
        gemini_res: Any = await generate(
            model=settings.GEMINI_FLASH_MODEL,
            contents=[prompt],
            config=None,
            timeout=CRISIS_NARRATIVE_TIMEOUT,
        )
        return _extract_response_text(gemini_res)
    except (
        GeminiError,
        google.api_core.exceptions.GoogleAPIError,
        httpx.HTTPError,
        TimeoutError,
        ValueError,
        AttributeError,
        OSError,
        RuntimeError,
    ):
        return None
