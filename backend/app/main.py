import json
import asyncio
import logging
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

logger = logging.getLogger("aurapulse")

from .config import settings
from .schemas import (
    MasterEventPlan,
    CrisisTrigger,
    ContingencyDiff,
    SimulationRequest,
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
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Autonomous Multimodal Event Planning & Reactive Contingency Engine",
)

# CORS configuration for Next.js client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DeconstructRequest(BaseModel):
    image_base64: Optional[str] = None
    moodboard_preset: Optional[str] = "royal_palace"
    headcount: int = 450
    locality: str = "Jaipur"
    budget_ceiling: float = 3500000.0
    event_type: str = "wedding"


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
            "stream": "/api/v1/pulse/events/stream",
            "vendors": "/api/v1/integrations/vendors",
            "sheets_export": "/api/v1/integrations/sheets/export",
            "calendar_sync": "/api/v1/integrations/calendar/sync"
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
            locality=payload.locality,
            budget_ceiling=payload.budget_ceiling,
            event_type=payload.event_type
        )
        return plan
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
        res = await chat_copilot(event_plan=payload.event_plan, user_prompt=payload.user_prompt)
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


@app.get("/api/v1/pulse/events/stream")
async def api_stream_contingency_events():
    """
    Server-Sent Events (SSE) telemetry stream:
    Emits real-time state solver heartbeats and crisis simulation transitions.
    """
    async def event_generator():
        steps = [
            {"step": "INTAKE", "msg": "AuraPulse event bus initialized. Listening for real-time risk triggers..."},
            {"step": "WEATHER_MONITOR", "msg": "Microclimate telemetry nominal. Rain probability 12% at target coordinates."},
            {"step": "SOLVER_READY", "msg": "Deterministic constraint graph loaded: 3 Tier-1 Critical lines locked."},
            {"step": "FABRIC_READY", "msg": "Google Maps Places and Sheets API endpoints hot-standby."}
        ]
        for s in steps:
            yield f"data: {json.dumps(s)}\n\n"
            await asyncio.sleep(1.0)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/v1/integrations/vendors")
async def api_get_vendors(
    query: str = Query(..., description="Vendor category search query"),
    city: str = Query(..., description="Target city"),
    min_rating: float = Query(4.0, description="Minimum Google rating")
):
    """
    Vendor Discovery via Google Maps Places API:
    Queries verified local suppliers with live ratings and reviews.
    """
    try:
        results = await fetch_verified_vendors(query=query, city=city, min_rating=min_rating)
        return {
            "city": city,
            "query": query,
            "count": len(results),
            "vendors": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vendor query failed: {str(e)}")


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
