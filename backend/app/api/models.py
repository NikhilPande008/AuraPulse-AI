"""API Request and Response Pydantic models for AuraPulse endpoints."""

from typing import Any

from pydantic import BaseModel, Field

from ..agents.copilot.models import CopilotResponse
from ..schemas import MasterEventPlan

__all__ = [
    "CalendarSyncRequest",
    "CalendarSyncResponse",
    "CalendarSyncedEvent",
    "CopilotRequest",
    "CopilotResponse",
    "HealthApis",
    "HealthResponse",
    "RootResponse",
    "SheetsExportRequest",
    "SheetsExportResponse",
    "StudioRenderResponse",
    "VendorSearchResponse",
    "VisualAlternativeRequest",
]


class RootResponse(BaseModel):
    system: str
    classification: str
    version: str
    status: str
    endpoints: dict[str, str]


class HealthApis(BaseModel):
    gemini: bool
    places_maps: bool
    sheets_v4: bool
    calendar_ics: bool


class HealthResponse(BaseModel):
    status: str
    version: str
    engine_flash: str
    gemini_configured: bool
    places_configured: bool
    sheets_configured: bool
    google_apis: HealthApis


class SheetsExportRequest(BaseModel):
    spreadsheet_title: str = Field(..., max_length=200)
    boq_items: list[dict[str, Any]] = Field(..., max_length=500)
    currency: str | None = "INR"


class SheetsExportResponse(BaseModel):
    status: str = "SUCCESS"
    spreadsheet_id: str | None = None
    spreadsheet_title: str | None = None
    spreadsheet_url: str | None = None
    title: str | None = None
    rows_written: int | None = None
    total_rows_created: int | None = None
    grand_total_formula: str | None = None
    priority_formulas: dict[str, str] | None = None
    items_exported: int | None = None
    currency: str | None = "INR"
    message: str | None = None


class CalendarSyncRequest(BaseModel):
    calendar_id: str | None = "primary"
    event_title: str = Field(..., max_length=200)
    schedule_blocks: list[dict[str, Any]] = Field(..., max_length=100)


class CalendarSyncedEvent(BaseModel):
    block_id: str | None = None
    activity: str | None = None
    calendar_link: str | None = None
    status: str = "READY"


class CalendarSyncResponse(BaseModel):
    event_title: str
    total_blocks_synced: int
    synced_events: list[CalendarSyncedEvent]
    status: str
    export_mode: str


class VisualAlternativeRequest(BaseModel):
    prompt_description: str = Field(..., max_length=1000)
    theme: str | None = Field("Palace Royal Marquee", max_length=80)


class StudioRenderResponse(BaseModel):
    image_url: str
    prompt: str
    model: str | None = None
    status: str
    is_generated: bool
    source: str
    error: str | None = None


class VendorSearchResponse(BaseModel):
    city: str
    query: str
    count: int
    vendors: list[dict[str, Any]]
    is_configured: bool
    status: str


class CopilotRequest(BaseModel):
    event_plan: MasterEventPlan
    user_prompt: str = Field(..., min_length=1, max_length=1000)
    history: list[dict[str, str]] | None = Field(default_factory=list, max_length=12)
