import os
import json
import time
import asyncio
import logging
from collections import defaultdict
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Request, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field

logger = logging.getLogger("aurapulse")

from .config import settings
from .schemas import (
    MasterEventPlan,
    CrisisTrigger,
    ContingencyDiff,
    SimulationRequest,
    PlanRequest,
    DeconstructRequest,
)
from .agents import (
    deconstruct_moodboard,
    evaluate_contingency,
    generate_visual_alternative,
    chat_copilot,
)
from .integrations import (
    fetch_verified_vendors,
    export_event_to_google_sheets,
    sync_schedule_to_google_calendar,
    generate_calendar_ics,
)
from .integrations.google_sheets import (
    SheetsNotConfiguredError,
    SheetsExportError,
    is_sheets_configured,
)
from .llm.client import GeminiUnavailable, GeminiQuota, GeminiBadOutput

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Autonomous Multimodal Event Planning & Reactive Contingency Engine",
)

# 1. Body Size Limit Middleware (6MB limit)
MAX_BODY_BYTES = 6 * 1024 * 1024  # 6 MB

@app.middleware("http")
async def limit_body_size_middleware(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > MAX_BODY_BYTES:
                return JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={
                        "code": "PAYLOAD_TOO_LARGE",
                        "message": "Request body exceeds the maximum permitted size of 6MB.",
                    },
                )
        except ValueError:
            pass

    return await call_next(request)


# 2. In-Memory Sliding-Window Rate Limiter
class SlidingWindowLimiter:
    def __init__(self, per_minute: int = 10, per_day: int = 100):
        self.per_minute = per_minute
        self.per_day = per_day
        self._minute_buckets: Dict[str, List[float]] = defaultdict(list)
        self._day_buckets: Dict[str, List[float]] = defaultdict(list)

    def check_and_record(self, key: str) -> bool:
        now = time.time()
        # Clean minute window
        min_cutoff = now - 60.0
        self._minute_buckets[key] = [t for t in self._minute_buckets[key] if t > min_cutoff]
        if len(self._minute_buckets[key]) >= self.per_minute:
            return False

        # Clean day window
        day_cutoff = now - 86400.0
        self._day_buckets[key] = [t for t in self._day_buckets[key] if t > day_cutoff]
        if len(self._day_buckets[key]) >= self.per_day:
            return False

        self._minute_buckets[key].append(now)
        self._day_buckets[key].append(now)
        return True


rate_limiter = SlidingWindowLimiter(per_minute=10, per_day=100)
AI_RATE_LIMITED_PATHS = {
    "/api/v1/aura/deconstruct",
    "/api/v1/aura/chat-copilot",
    "/api/v1/pulse/simulate",
}

@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    if request.url.path in AI_RATE_LIMITED_PATHS and request.method == "POST":
        # Allow disabling rate limiting in test suite if requested
        if os.getenv("DISABLE_RATE_LIMIT", "false").lower() != "true":
            client_ip = (
                request.headers.get("x-forwarded-for", "").split(",")[0].strip()
                or (request.client.host if request.client else "127.0.0.1")
            )
            if not rate_limiter.check_and_record(client_ip):
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "code": "RATE_LIMITED",
                        "message": "Too many requests. Please wait a moment before trying again.",
                    },
                )

    return await call_next(request)


# CORS configuration restricted to authorized origins
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
custom_origin = os.getenv("ALLOWED_ORIGIN")
if custom_origin:
    allowed_origins.extend([o.strip() for o in custom_origin.split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """Preserves structured error payloads like {"code": "...", "message": ...}."""
    if isinstance(exc.detail, dict) and "code" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": "HTTP_ERROR", "message": str(exc.detail)},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Sanitizes unhandled exceptions to avoid leaking internals or stack traces."""
    logger.error(f"Unhandled error handling {request.method} {request.url.path}: {exc}", exc_info=True)
    if isinstance(exc, GeminiUnavailable):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"code": "GEMINI_UNAVAILABLE", "message": "Gemini service is currently unavailable. Try again shortly."},
        )
    if isinstance(exc, GeminiQuota):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"code": "GEMINI_QUOTA_EXCEEDED", "message": "Gemini API quota exceeded. Please wait a minute."},
        )
    if isinstance(exc, GeminiBadOutput):
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"code": "GEMINI_BAD_OUTPUT", "message": "Gemini model produced an invalid response. Try again."},
        )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": "INTERNAL_ERROR",
            "message": "An internal error occurred while processing your request. Please try again.",
        },
    )


class SheetsExportRequest(BaseModel):
    spreadsheet_title: str = Field(..., max_length=200)
    boq_items: List[dict] = Field(..., max_length=500)
    currency: Optional[str] = "INR"


class CalendarSyncRequest(BaseModel):
    calendar_id: Optional[str] = "primary"
    event_title: str = Field(..., max_length=200)
    schedule_blocks: List[dict] = Field(..., max_length=100)


class VisualAlternativeRequest(BaseModel):
    prompt_description: str = Field(..., max_length=1000)
    theme: Optional[str] = Field("Palace Royal Marquee", max_length=80)


class CopilotRequest(BaseModel):
    event_plan: MasterEventPlan
    user_prompt: str = Field(..., min_length=1, max_length=1000)
    history: Optional[List[Dict[str, str]]] = Field(default_factory=list, max_length=12)


@app.get("/")
def root():
    return {
        "system": settings.PROJECT_NAME,
        "classification": "Autonomous Multimodal Event Planning & Reactive Contingency Engine",
        "version": settings.VERSION,
        "status": "ONLINE",
        "endpoints": {
            "health": "/api/health",
            "deconstruct": "/api/v1/aura/deconstruct",
            "simulate": "/api/v1/pulse/simulate",
            "vendors": "/api/v1/integrations/vendors",
            "sheets_export": "/api/v1/integrations/sheets/export",
            "calendar_ics": "/api/v1/export/calendar-ics",
        }
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "engine_flash": settings.GEMINI_FLASH_MODEL,
        "engine_pro": settings.GEMINI_PRO_MODEL,
        "gemini_configured": bool(settings.GEMINI_API_KEY),
        "places_configured": bool(settings.GOOGLE_MAPS_API_KEY),
        "sheets_configured": is_sheets_configured(),
        "google_apis": {
            "gemini": bool(settings.GEMINI_API_KEY),
            "places_maps": bool(settings.GOOGLE_MAPS_API_KEY),
            "sheets_v4": is_sheets_configured(),
            "calendar_ics": True,
        }
    }


@app.post("/api/v1/aura/deconstruct", response_model=MasterEventPlan)
async def api_deconstruct_moodboard(payload: DeconstructRequest):
    """
    Multimodal Vision-to-BOQ Intake:
    Processes user mood board via Gemini 2.5 Flash, extracts structural & botanical elements,
    and returns a strictly verified MasterEventPlan.
    """
    try:
        plan = await deconstruct_moodboard(
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
        return plan
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Aura Vision deconstruction failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"code": "GENERATION_FAILED", "message": "Failed to generate event plan from input."},
        )


@app.post("/api/v1/aura/chat-copilot")
async def api_chat_copilot(payload: CopilotRequest):
    """
    Conversational GenAI Ideas & Budget Co-Pilot:
    Processes user prompts (menu swaps, floral cuts, games, return gifts, cultural rituals)
    and returns advisory responses, updated MasterEventPlan, and actionable suggestions.
    """
    try:
        res = await chat_copilot(
            event_plan=payload.event_plan,
            user_prompt=payload.user_prompt,
            history=payload.history
        )
        return res
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat Co-Pilot failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"code": "COPILOT_FAILED", "message": "Copilot encountered an error. Please try again."},
        )


@app.post("/api/v1/pulse/simulate", response_model=ContingencyDiff)
async def api_simulate_contingency(request: SimulationRequest):
    """
    Pulse Dynamic Reactive Engine:
    Applies deterministic tier locks and Gemini 2.5 Flash multi-constraint reasoning to
    generate an actionable ContingencyDiff with ADDED, MODIFIED, and DROPPED items.
    """
    try:
        diff = await evaluate_contingency(plan=request.plan, trigger=request.trigger)
        return diff
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Pulse Engine evaluation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"code": "SIMULATION_FAILED", "message": "Contingency simulation failed."},
        )


# Telemetry loop purged per CR-18 (honest indicators only; no fabricated telemetry loops)
# @app.get("/api/v1/pulse/events/stream")
# async def api_stream_contingency_events():
#     ...


@app.get("/api/v1/integrations/vendors")
async def api_get_vendors(
    query: str = Query(..., description="Vendor category search query"),
    city: str = Query(..., description="Target city"),
    min_rating: float = Query(4.0, description="Minimum Google rating")
):
    """
    Vendor Discovery via Google Maps Places API (New) (CR-13):
    Queries verified local suppliers with live ratings and reviews.
    """
    try:
        data = await fetch_verified_vendors(query=query, city=city, min_rating=min_rating)
        vendors = data.get("vendors", []) if isinstance(data, dict) else data
        is_cfg = data.get("is_configured", False) if isinstance(data, dict) else bool(settings.GOOGLE_MAPS_API_KEY)
        status = data.get("status", "ACTIVE" if is_cfg else "SIMULATED") if isinstance(data, dict) else ("ACTIVE" if is_cfg else "SIMULATED")
        return {
            "city": city,
            "query": query,
            "count": len(vendors),
            "vendors": vendors,
            "is_configured": is_cfg,
            "status": status,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Vendor query failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail={"code": "VENDOR_QUERY_FAILED", "message": "Failed to fetch vendors."})


@app.post("/api/v1/export/calendar-ics")
async def api_export_calendar_ics(plan: MasterEventPlan):
    """
    RFC-5545 Calendar Export Endpoint (CR-14):
    Generates standard .ics calendar file containing:
    - Backwards planning milestones as all-day events on their calculated due_date.
    - Day-of schedule blocks on event_date with TZID=Asia/Kolkata.
    Zero-permission direct export for judges and end users.
    """
    try:
        ics_text = generate_calendar_ics(plan)
        filename = f"{plan.event_id or 'event'}_schedule.ics"
        return Response(
            content=ics_text,
            media_type="text/calendar; charset=utf-8",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ICS calendar export failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail={"code": "ICS_EXPORT_FAILED", "message": "Failed to export calendar."})


@app.post("/api/v1/integrations/sheets/export")
async def api_export_sheets(payload: SheetsExportRequest):
    """
    Live Export to Google Sheets API v4 (Non-blocking async worker):
    Generates a formula-driven spreadsheet with dynamic =SUM() & =SUMIF() calculations.
    """
    try:
        res = await asyncio.to_thread(
            export_event_to_google_sheets,
            spreadsheet_title=payload.spreadsheet_title,
            boq_items=payload.boq_items,
            currency=payload.currency or "INR"
        )
        return res
    except SheetsNotConfiguredError:
        raise HTTPException(
            status_code=503,
            detail={"code": "SHEETS_NOT_CONFIGURED", "message": "Google Sheets API credentials not configured."},
        )
    except SheetsExportError as e:
        logger.error(f"Google Sheets export failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=502,
            detail={"code": "SHEETS_EXPORT_FAILED", "message": "Google Sheets export failed."},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google Sheets export failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail={"code": "SHEETS_ERROR", "message": "Google Sheets export failed."})


@app.post("/api/v1/integrations/calendar/sync")
async def api_sync_calendar(payload: CalendarSyncRequest):
    """
    Run-of-show dispatch to Google Calendar API v3 (Non-blocking async worker):
    Schedules blocks with outdoor contingency tags and real-time alerts.
    """
    try:
        res = await asyncio.to_thread(
            sync_schedule_to_google_calendar,
            calendar_id=payload.calendar_id or "primary",
            event_title=payload.event_title,
            schedule_blocks=payload.schedule_blocks
        )
        return res
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google Calendar sync failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=503 if "auth" in str(e).lower() or "credentials" in str(e).lower() else 500,
            detail={"code": "CALENDAR_SYNC_FAILED", "message": "Google Calendar sync failed."}
        )


@app.post("/api/v1/studio/render-alternative")
async def api_render_alternative(payload: VisualAlternativeRequest):
    """
    Generative Studio via Imagen 3:
    Produces visual rendering of altered staging or marquee configurations.
    """
    try:
        res = await generate_visual_alternative(
            prompt_description=payload.prompt_description,
            event_theme=payload.theme or "Palace Royal Marquee"
        )
        return res
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generative Studio failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail={"code": "STUDIO_FAILED", "message": "Generative Studio rendering failed."})
