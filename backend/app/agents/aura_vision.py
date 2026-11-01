import logging
from typing import List, Optional

from fastapi import HTTPException

from ..fixtures.sample_plans import (
    SAMPLE_PRESETS,
    create_baseline_wedding_plan,
    create_preset_cyberpunk_birthday,
    create_preset_diwali_mela,
    create_preset_meadow_wedding,
)
from ..llm.client import generate_event_plan
from ..schemas import (
    MasterEventPlan,
    PlanRequest,
)
from ..services.timeline import build_milestones, default_event_date, get_backwards_date

logger = logging.getLogger("aurapulse.aura_vision")

# Re-export sample presets and backwards date helper for backward compatibility
__all__ = [
    "create_preset_meadow_wedding",
    "create_preset_cyberpunk_birthday",
    "create_preset_diwali_mela",
    "create_baseline_wedding_plan",
    "get_backwards_date",
    "deconstruct_moodboard",
    "SAMPLE_PRESETS",
]


async def deconstruct_moodboard(
    image_base64: Optional[str] = None,
    moodboard_preset: Optional[str] = None,
    headcount: int = 400,
    locality: str = "Pune",
    city: Optional[str] = None,
    budget_ceiling: float = 1500000.0,
    budget: Optional[float] = None,
    event_type: str = "wedding",
    event_date: Optional[str] = None,
    culture_region: Optional[str] = None,
    theme: Optional[str] = None,
    dietary: Optional[List[str]] = None,
    language: str = "en",
) -> MasterEventPlan:
    """
    Multimodal Gemini 2.5 Flash agent (CR-06 & CR-08):
    1. Returns a canned preset ONLY when moodboard_preset strictly equals
       a recognized preset ID ("meadow_wedding", "cyber_birthday", "diwali_mela").
    2. For all custom parameters, calls Gemini 2.5 Flash asynchronously.
    3. If Gemini generation fails, raises an explicit HTTP 503 error:
       {"code": "GENERATION_FAILED", "message": "Failed to generate event plan via Gemini. Please retry or choose a preset."}
       No silent mock preset overrides.
    """
    # 1. Strict Preset Matching ONLY
    if moodboard_preset and moodboard_preset in SAMPLE_PRESETS:
        preset_builder = SAMPLE_PRESETS[moodboard_preset]
        plan = preset_builder(event_date=event_date or default_event_date())
        if event_date:
            plan.event_date = event_date
            plan.planning_milestones = build_milestones(
                event_date=event_date,
                event_type=plan.event_type,
                culture_region=culture_region or plan.culture_region
            )
        if culture_region:
            plan.culture_region = culture_region
        if theme:
            plan.theme = theme
        return plan

    # 2. Asynchronous Gemini 2.5 Flash Generation
    effective_city = city or locality or "Pune"
    effective_budget = budget if budget is not None else budget_ceiling
    effective_type = "community_event" if event_type == "community_festival" else event_type

    try:
        plan_req = PlanRequest(
            event_type=effective_type,
            event_date=event_date,
            city=effective_city,
            headcount=headcount,
            budget=effective_budget,
            culture_region=culture_region,
            theme=theme,
            dietary=dietary or [],
            language=language if language in ("en", "hi", "mr") else "en",
            image_base64=image_base64,
            moodboard_preset=moodboard_preset,
        )
        return await generate_event_plan(plan_req)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Gemini event plan generation failed: {e}", exc_info=True)
        # CR-06 requirement: Delete silent fallback; raise descriptive HTTP 503 error
        raise HTTPException(
            status_code=503,
            detail={
                "code": "GENERATION_FAILED",
                "message": "Failed to generate event plan via Gemini. Please retry or choose a preset."
            }
        )
