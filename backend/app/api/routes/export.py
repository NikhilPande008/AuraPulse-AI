"""Calendar and file export endpoints."""

import logging

from fastapi import APIRouter, HTTPException, Response

from ...integrations import generate_calendar_ics
from ...schemas import MasterEventPlan

logger = logging.getLogger("aurapulse.routes.export")
router = APIRouter(prefix="/api/v1/export", tags=["Export"])


@router.post("/calendar-ics")
async def api_export_calendar_ics(plan: MasterEventPlan) -> Response:
    """Generate and return an RFC-5545 compliant .ics calendar file.

    Args:
        plan: The MasterEventPlan containing schedule and milestone data.

    Returns:
        HTTP Response with text/calendar content type and file attachment headers.

    Raises:
        HTTPException: If .ics file generation fails.
    """
    try:
        ics_text = generate_calendar_ics(plan)
        filename = f"{plan.event_id or 'event'}_schedule.ics"
        return Response(
            content=ics_text,
            media_type="text/calendar; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("ICS calendar export failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500, detail={"code": "ICS_EXPORT_FAILED", "message": "Failed to export calendar."}
        ) from e
