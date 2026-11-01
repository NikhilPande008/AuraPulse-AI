"""Aura Vision: Moodboard deconstruction and event plan generation."""

import logging
from collections.abc import Sequence
from typing import Literal, cast

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
    DietaryType,
    MasterEventPlan,
    PlanRequest,
)
from ..services.timeline import build_milestones, default_event_date, get_backwards_date

logger = logging.getLogger("aurapulse.aura_vision")

# Re-export sample presets and backwards date helper for backward compatibility
__all__ = [
    "SAMPLE_PRESETS",
    "create_baseline_wedding_plan",
    "create_preset_cyberpunk_birthday",
    "create_preset_diwali_mela",
    "create_preset_meadow_wedding",
    "deconstruct_moodboard",
    "get_backwards_date",
]

VALID_EVENT_TYPES = {"wedding", "birthday", "community_event", "community_festival"}
VALID_LANGUAGES = {"en", "hi", "mr"}
VALID_DIETARY = {"veg", "jain", "vegan", "non_veg", "halal", "no_onion_garlic"}


def _apply_preset_overrides(
    plan: MasterEventPlan,
    event_date: str | None,
    culture_region: str | None,
    theme: str | None,
) -> None:
    if event_date:
        plan.event_date = event_date
        plan.planning_milestones = build_milestones(
            event_date=event_date,
            event_type=plan.event_type,
            culture_region=culture_region or plan.culture_region,
        )
    if culture_region:
        plan.culture_region = culture_region
    if theme:
        plan.theme = theme


def _build_preset_plan(
    moodboard_preset: str,
    event_date: str | None,
    culture_region: str | None,
    theme: str | None,
) -> MasterEventPlan:
    preset_builder = SAMPLE_PRESETS[moodboard_preset]
    plan = preset_builder(event_date=event_date or default_event_date())
    _apply_preset_overrides(plan, event_date, culture_region, theme)
    return plan


def _resolve_event_type(
    event_type: str,
) -> Literal["wedding", "birthday", "community_event", "community_festival"]:
    norm = "community_event" if event_type == "community_festival" else event_type
    if norm not in VALID_EVENT_TYPES:
        norm = "wedding"
    return cast(
        Literal["wedding", "birthday", "community_event", "community_festival"],
        norm,
    )


def _resolve_language(language: str) -> Literal["en", "hi", "mr"]:
    return cast(Literal["en", "hi", "mr"], language if language in VALID_LANGUAGES else "en")


def _resolve_dietary(dietary: Sequence[str] | None) -> list[DietaryType]:
    return [cast(DietaryType, d) for d in (dietary or []) if d in VALID_DIETARY]


def _clean_plan_request(
    event_type: str,
    event_date: str | None,
    effective_city: str,
    headcount: int,
    effective_budget: float,
    culture_region: str | None,
    theme: str | None,
    dietary: Sequence[str] | None,
    language: str,
    image_base64: str | None,
    moodboard_preset: str | None,
) -> PlanRequest:
    return PlanRequest(
        event_type=_resolve_event_type(event_type),
        event_date=event_date,
        city=effective_city,
        headcount=headcount,
        budget=effective_budget,
        culture_region=culture_region,
        theme=theme,
        dietary=_resolve_dietary(dietary),
        language=_resolve_language(language),
        image_base64=image_base64,
        moodboard_preset=moodboard_preset,
    )


async def _generate_via_gemini(
    event_type: str,
    event_date: str | None,
    effective_city: str,
    headcount: int,
    effective_budget: float,
    culture_region: str | None,
    theme: str | None,
    dietary: Sequence[str] | None,
    language: str,
    image_base64: str | None,
    moodboard_preset: str | None,
) -> MasterEventPlan:
    try:
        plan_req = _clean_plan_request(
            event_type=event_type,
            event_date=event_date,
            effective_city=effective_city,
            headcount=headcount,
            effective_budget=effective_budget,
            culture_region=culture_region,
            theme=theme,
            dietary=dietary,
            language=language,
            image_base64=image_base64,
            moodboard_preset=moodboard_preset,
        )
        return await generate_event_plan(plan_req)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Gemini event plan generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail={
                "code": "GENERATION_FAILED",
                "message": "Failed to generate event plan via Gemini. Please retry or choose a preset.",
            },
        ) from e


async def deconstruct_moodboard(
    image_base64: str | None = None,
    moodboard_preset: str | None = None,
    headcount: int = 400,
    locality: str = "Pune",
    city: str | None = None,
    budget_ceiling: float = 1500000.0,
    budget: float | None = None,
    event_type: str = "wedding",
    event_date: str | None = None,
    culture_region: str | None = None,
    theme: str | None = None,
    dietary: Sequence[str] | None = None,
    language: str = "en",
) -> MasterEventPlan:
    """Deconstruct moodboards or presets into structured event plans.

    Returns deterministic sample presets when a recognized preset key is passed,
    or synthesizes custom event plans via Gemini 2.5 Flash.

    Args:
        image_base64: Base64-encoded image string of the moodboard.
        moodboard_preset: Preset identifier (e.g. "meadow_wedding").
        headcount: Estimated number of guests.
        locality: Legacy alias for city.
        city: Event host city.
        budget_ceiling: Maximum budget in INR.
        budget: Legacy alias for budget ceiling.
        event_type: Category of event ("wedding", "birthday", etc.).
        event_date: Event date formatted as YYYY-MM-DD.
        culture_region: Regional or cultural context.
        theme: Event aesthetic or theme description.
        dietary: Dietary constraints (e.g. ["pure_veg"]).
        language: Language code ("en", "hi", "mr").

    Returns:
        A validated MasterEventPlan.

    Raises:
        HTTPException: If plan generation fails (503).
    """
    if moodboard_preset and moodboard_preset in SAMPLE_PRESETS:
        return _build_preset_plan(moodboard_preset, event_date, culture_region, theme)

    effective_city = city or locality or "Pune"
    effective_budget = budget if budget is not None else budget_ceiling
    return await _generate_via_gemini(
        event_type=event_type,
        event_date=event_date,
        effective_city=effective_city,
        headcount=headcount,
        effective_budget=effective_budget,
        culture_region=culture_region,
        theme=theme,
        dietary=dietary,
        language=language,
        image_base64=image_base64,
        moodboard_preset=moodboard_preset,
    )
