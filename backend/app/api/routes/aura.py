"""Aura Vision moodboard deconstruction and conversational copilot endpoints."""

import logging

from fastapi import APIRouter, HTTPException

from ...agents import chat_copilot, deconstruct_moodboard
from ...llm.client import GeminiError
from ...schemas import DeconstructRequest, MasterEventPlan
from ..models import CopilotRequest, CopilotResponse

logger = logging.getLogger("aurapulse.routes.aura")
router = APIRouter(prefix="/api/v1/aura", tags=["Aura Vision & Copilot"])


@router.post("/deconstruct", response_model=MasterEventPlan)
async def api_deconstruct_moodboard(payload: DeconstructRequest) -> MasterEventPlan:
    """Deconstruct moodboard or preset into a structured MasterEventPlan.

    Args:
        payload: User intake parameters and optional moodboard image.

    Returns:
        The generated MasterEventPlan.

    Raises:
        HTTPException: On generation failures or invalid input.
    """
    try:
        return await deconstruct_moodboard(
            image_base64=payload.image_base64,
            moodboard_preset=payload.moodboard_preset,
            headcount=payload.headcount,
            locality=payload.city,
            city=payload.city,
            budget_ceiling=payload.budget,
            budget=payload.budget,
            event_type=payload.event_type,
            event_date=payload.event_date,
            culture_region=payload.culture_region,
            theme=payload.theme,
            dietary=payload.dietary,
            language=payload.language,
        )
    except (HTTPException, GeminiError):
        raise
    except Exception as e:
        logger.error(f"Aura Vision deconstruction failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"code": "GENERATION_FAILED", "message": "Failed to generate event plan from input."},
        ) from e


@router.post("/chat-copilot", response_model=CopilotResponse)
async def api_chat_copilot(payload: CopilotRequest) -> CopilotResponse:
    """Execute conversational replanning and idea generation.

    Args:
        payload: Input containing the current event plan and user instruction.

    Returns:
        Structured CopilotResponse with replan diffs, suggestions, and reply.

    Raises:
        HTTPException: On unrecoverable copilot execution failures.
    """
    try:
        res = await chat_copilot(
            event_plan=payload.event_plan,
            user_prompt=payload.user_prompt,
            history=payload.history,
        )
        return CopilotResponse.model_validate(res)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat Co-Pilot failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"code": "COPILOT_FAILED", "message": "Copilot encountered an error. Please try again."},
        ) from e
