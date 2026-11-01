"""Generative Studio rendering endpoints."""

import logging

from fastapi import APIRouter, HTTPException

from ...agents import generate_visual_alternative
from ..models import StudioRenderResponse, VisualAlternativeRequest

logger = logging.getLogger("aurapulse.routes.studio")
router = APIRouter(prefix="/api/v1/studio", tags=["Generative Studio"])


@router.post("/render-alternative", response_model=StudioRenderResponse)
async def api_render_alternative(payload: VisualAlternativeRequest) -> StudioRenderResponse:
    """Generate visual renders for event staging using Imagen 3 or fallback imagery.

    Args:
        payload: VisualAlternativeRequest with prompt description and optional theme.

    Returns:
        StudioRenderResponse with image URL and metadata.

    Raises:
        HTTPException: If studio rendering fails.
    """
    try:
        res = await generate_visual_alternative(
            prompt_description=payload.prompt_description,
            event_theme=payload.theme or "Palace Royal Marquee",
        )
        return StudioRenderResponse.model_validate(res)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Generative Studio failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500, detail={"code": "STUDIO_FAILED", "message": "Generative Studio rendering failed."}
        ) from e
