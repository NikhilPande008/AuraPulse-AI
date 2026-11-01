"""Health and system discovery endpoints."""

from fastapi import APIRouter

from ...config import settings
from ...integrations.google_sheets import is_sheets_configured
from ..models import HealthApis, HealthResponse, RootResponse

router = APIRouter(tags=["Health"])


@router.get("/", response_model=RootResponse)
def root() -> RootResponse:
    """Return root system classification and available endpoints."""
    return RootResponse(
        system=settings.PROJECT_NAME,
        classification="Autonomous Multimodal Event Planning & Reactive Contingency Engine",
        version=settings.VERSION,
        status="ONLINE",
        endpoints={
            "health": "/api/health",
            "deconstruct": "/api/v1/aura/deconstruct",
            "simulate": "/api/v1/pulse/simulate",
            "vendors": "/api/v1/integrations/vendors",
            "sheets_export": "/api/v1/integrations/sheets/export",
            "calendar_ics": "/api/v1/export/calendar-ics",
        },
    )


@router.get("/api/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return health status of core engines and external Google service APIs."""
    return HealthResponse(
        status="healthy",
        version=settings.VERSION,
        engine_flash=settings.GEMINI_FLASH_MODEL,
        gemini_configured=bool(settings.gemini_api_key()),
        places_configured=bool(settings.google_maps_api_key()),
        sheets_configured=is_sheets_configured(),
        google_apis=HealthApis(
            gemini=bool(settings.gemini_api_key()),
            places_maps=bool(settings.google_maps_api_key()),
            sheets_v4=is_sheets_configured(),
            calendar_ics=True,
        ),
    )
