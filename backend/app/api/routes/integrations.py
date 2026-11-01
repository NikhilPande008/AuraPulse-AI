"""Google ecosystem integrations: Maps Places, Sheets export, and Calendar sync."""

import asyncio
import logging
from typing import Any, NoReturn

from fastapi import APIRouter, HTTPException, Query

from ...config import settings
from ...integrations import (
    export_event_to_google_sheets,
    fetch_verified_vendors,
    sync_schedule_to_google_calendar,
)
from ...integrations.google_sheets import (
    SheetsExportError,
    SheetsNotConfiguredError,
)
from ..models import (
    CalendarSyncRequest,
    CalendarSyncResponse,
    SheetsExportRequest,
    SheetsExportResponse,
    VendorSearchResponse,
)

logger = logging.getLogger("aurapulse.routes.integrations")
router = APIRouter(prefix="/api/v1/integrations", tags=["Integrations"])


def _extract_vendor_data(data: Any) -> tuple[list[dict[str, Any]], bool, str]:
    vendors = data.get("vendors", []) if isinstance(data, dict) else data
    is_cfg = data.get("is_configured", False) if isinstance(data, dict) else bool(settings.GOOGLE_MAPS_API_KEY)
    status_val = (
        data.get("status", "ACTIVE" if is_cfg else "SIMULATED")
        if isinstance(data, dict)
        else ("ACTIVE" if is_cfg else "SIMULATED")
    )
    return vendors, is_cfg, status_val


@router.get("/vendors", response_model=VendorSearchResponse)
async def api_get_vendors(
    query: str = Query(..., description="Vendor category search query"),
    city: str = Query(..., description="Target city"),
    min_rating: float = Query(4.0, description="Minimum Google rating"),
) -> VendorSearchResponse:
    """Discover verified local vendors using Google Maps Places API.

    Args:
        query: Search term for vendor category.
        city: Target city or locality.
        min_rating: Minimum rating filter (default: 4.0).

    Returns:
        VendorSearchResponse with verified local vendor listings.
    """
    try:
        data = await fetch_verified_vendors(query=query, city=city, min_rating=min_rating)
        vendors, is_cfg, status_val = _extract_vendor_data(data)
        return VendorSearchResponse(
            city=city,
            query=query,
            count=len(vendors),
            vendors=vendors,
            is_configured=is_cfg,
            status=status_val,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Vendor query failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail={"code": "VENDOR_QUERY_FAILED", "message": "Failed to fetch vendors."}
        ) from e


def _raise_sheets_error(e: Exception) -> NoReturn:
    if isinstance(e, SheetsNotConfiguredError):
        raise HTTPException(
            status_code=503,
            detail={"code": "SHEETS_NOT_CONFIGURED", "message": "Google Sheets API credentials not configured."},
        ) from e
    if isinstance(e, SheetsExportError):
        logger.error(f"Google Sheets export failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=502,
            detail={"code": "SHEETS_EXPORT_FAILED", "message": "Google Sheets export failed."},
        ) from e
    logger.error(f"Google Sheets export failed: {e}", exc_info=True)
    raise HTTPException(
        status_code=500, detail={"code": "SHEETS_ERROR", "message": "Google Sheets export failed."}
    ) from e


@router.post("/sheets/export", response_model=SheetsExportResponse)
async def api_export_sheets(payload: SheetsExportRequest) -> SheetsExportResponse:
    """Export BOQ line items into a formula-driven Google Sheets spreadsheet.

    Args:
        payload: Export request containing spreadsheet title and BOQ items.

    Returns:
        SheetsExportResponse with spreadsheet ID and URL.

    Raises:
        HTTPException: If credentials are missing (503) or export fails (502/500).
    """
    try:
        res = await asyncio.to_thread(
            export_event_to_google_sheets,
            spreadsheet_title=payload.spreadsheet_title,
            boq_items=payload.boq_items,
            currency=payload.currency or "INR",
        )
        return SheetsExportResponse.model_validate(res)
    except HTTPException:
        raise
    except Exception as e:  # noqa: BLE001
        _raise_sheets_error(e)


def _raise_calendar_error(e: Exception) -> NoReturn:
    logger.error(f"Google Calendar sync failed: {e}", exc_info=True)
    err_str = str(e).lower()
    code = 503 if ("auth" in err_str or "credentials" in err_str) else 500
    raise HTTPException(
        status_code=code,
        detail={"code": "CALENDAR_SYNC_FAILED", "message": "Google Calendar sync failed."},
    ) from e


@router.post("/calendar/sync", response_model=CalendarSyncResponse)
async def api_sync_calendar(payload: CalendarSyncRequest) -> CalendarSyncResponse:
    """Generate calendar web intent synchronizations for schedule blocks.

    Args:
        payload: Calendar synchronization request payload.

    Returns:
        CalendarSyncResponse containing synchronized event links.

    Raises:
        HTTPException: If calendar synchronization encounters an error.
    """
    try:
        res = await asyncio.to_thread(
            sync_schedule_to_google_calendar,
            calendar_id=payload.calendar_id or "primary",
            event_title=payload.event_title,
            schedule_blocks=payload.schedule_blocks,
        )
        return CalendarSyncResponse.model_validate(res)
    except HTTPException:
        raise
    except Exception as e:  # noqa: BLE001
        _raise_calendar_error(e)
