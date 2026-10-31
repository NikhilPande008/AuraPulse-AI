import os
import json
import asyncio
import logging
from typing import Optional, List, Dict
from fastapi import FastAPI, HTTPException, Request, Query, Response
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

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Autonomous Multimodal Event Planning & Reactive Contingency Engine",
)

# CORS configuration restricted to authorized frontend origins
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
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """Preserves structured error payloads like {"code": "GENERATION_FAILED", "message": ...}"""
    if isinstance(exc.detail, dict) and "code" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


class SheetsExportRequest(BaseModel):
    spreadsheet_title: str
    boq_items: List[dict]
    currency: Optional[str] = "INR"


class CalendarSyncRequest(BaseModel):
    calendar_id: Optional[str] = "primary"
    event_title: str
    schedule_blocks: List[dict]


class VisualAlternativeRequest(BaseModel):
    prompt_description: str
    theme: Optional[str] = "Palace Royal Marquee"


class CopilotRequest(BaseModel):
    event_plan: MasterEventPlan
    user_prompt: str
    history: Optional[List[Dict[str, str]]] = Field(default_factory=list)


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
        "google_apis": {
            "places_maps": bool(settings.GOOGLE_MAPS_API_KEY),
            "sheets_v4": bool(settings.GOOGLE_APPLICATION_CREDENTIALS),
            "calendar_v3": bool(settings.GOOGLE_APPLICATION_CREDENTIALS)
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
        raise HTTPException(status_code=500, detail=f"Aura Vision deconstruction failed: {str(e)}")


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
    except Exception as e:
        logger.error(f"Chat Co-Pilot failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Chat Co-Pilot failed: {str(e)}")


@app.post("/api/v1/pulse/simulate", response_model=ContingencyDiff)
async def api_simulate_contingency(request: SimulationRequest):
    """
    Pulse Dynamic Reactive Engine:
    Applies deterministic tier locks and Gemini 2.5 Pro multi-constraint reasoning to
    generate an actionable ContingencyDiff with ADDED, MODIFIED, and DROPPED items.
    """
    try:
        diff = await evaluate_contingency(plan=request.plan, trigger=request.trigger)
        return diff
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pulse Engine evaluation failed: {str(e)}")


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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vendor query failed: {str(e)}")


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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ICS calendar export failed: {str(e)}")


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
    except Exception as e:
        logger.error(f"Google Sheets export failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=503 if "auth" in str(e).lower() or "credentials" in str(e).lower() else 500,
            detail=f"Google Sheets export failed: {str(e)}"
        )


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
    except Exception as e:
        logger.error(f"Google Calendar sync failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=503 if "auth" in str(e).lower() or "credentials" in str(e).lower() else 500,
            detail=f"Google Calendar sync failed: {str(e)}"
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generative Studio failed: {str(e)}")
