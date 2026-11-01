"""Google Calendar and RFC-5545 iCalendar (.ics) integration service."""

import urllib.parse
import uuid
from datetime import UTC, date, datetime, timedelta
from typing import Any

from ..schemas import MasterEventPlan, PlanningMilestone, ScheduleBlock
from ..services.timeline import default_event_date


def _escape_text(text: str) -> str:
    """Escapes RFC 5545 TEXT values: \\ -> \\\\, ; -> \\;, , -> \\,, \\n -> \\n."""
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\\", "\\\\")
    text = text.replace(";", "\\;").replace(",", "\\,")
    return text.replace("\n", "\\n")


def _fold_line(line: str) -> str:
    """
    Folds an RFC 5545 line so no physical line exceeds 75 octets in UTF-8.
    Continuation lines begin with a single ASCII space.
    """
    encoded = line.encode("utf-8")
    if len(encoded) <= 75:
        return line

    chunks: list[str] = []
    current_bytes = bytearray()
    max_len = 75

    for char in line:
        char_bytes = char.encode("utf-8")
        if len(current_bytes) + len(char_bytes) > max_len:
            chunks.append(current_bytes.decode("utf-8"))
            current_bytes = bytearray(b" " + char_bytes)
            max_len = 75
        else:
            current_bytes.extend(char_bytes)

    if current_bytes:
        chunks.append(current_bytes.decode("utf-8"))

    return "\r\n".join(chunks)


def _vevent_for_milestone(ms: PlanningMilestone, now_utc: str, clean_city: str) -> list[str]:
    due_str = ms.due_date.replace("-", "")
    try:
        d_obj = datetime.strptime(ms.due_date, "%Y-%m-%d").date()
        next_day_str = (d_obj + timedelta(days=1)).strftime("%Y%m%d")
    except (ValueError, TypeError):
        next_day_str = due_str

    summary = _escape_text(f"[{ms.phase}] {ms.title}")
    desc = _escape_text(
        f"AuraPulse Milestone\nCategory: {ms.category}\nDeliverable: {ms.description}\nPhase: {ms.phase}"
    )

    return [
        "BEGIN:VEVENT",
        f"UID:ms_{ms.id}_{uuid.uuid4().hex[:8]}@aurapulse.ai",
        f"DTSTAMP:{now_utc}",
        f"DTSTART;VALUE=DATE:{due_str}",
        f"DTEND;VALUE=DATE:{next_day_str}",
        f"SUMMARY:{summary}",
        f"DESCRIPTION:{desc}",
        f"LOCATION:{clean_city}",
        "STATUS:CONFIRMED",
        "END:VEVENT",
    ]


def _format_block_time(raw_time: str, clean_date: str, fallback_hour: str) -> str:
    if "T" in raw_time:
        try:
            dt = datetime.fromisoformat(raw_time)
            return dt.strftime("%Y%m%dT%H%M%S")
        except (ValueError, TypeError):
            return f"{clean_date}T{fallback_hour}0000"
    parts = raw_time.split(":")
    hh = parts[0].zfill(2)
    mm = parts[1].zfill(2) if len(parts) > 1 else "00"
    return f"{clean_date}T{hh}{mm}00"


def _vevent_for_block(block: ScheduleBlock, now_utc: str, clean_city: str, clean_date: str) -> list[str]:
    start_fmt = _format_block_time(block.start_time_iso, clean_date, "10")
    end_fmt = _format_block_time(block.end_time_iso, clean_date, "11")

    outdoor_tag = " [OUTDOOR ZONE - WEATHER WATCH]" if block.is_outdoor else " [INDOOR / COVERED]"
    summary = _escape_text(f"[{block.phase}] {block.activity}{outdoor_tag}")
    zone_label = "Outdoor Zone (Weather Alert)" if block.is_outdoor else "Covered / Indoor Zone"
    desc = _escape_text(
        f"AuraPulse Run-of-Show\n"
        f"Phase: {block.phase}\n"
        f"Responsible Party: {block.responsible_party}\n"
        f"Zone: {zone_label}\n"
        f"Block ID: {block.block_id}"
    )

    return [
        "BEGIN:VEVENT",
        f"UID:block_{block.block_id}_{uuid.uuid4().hex[:8]}@aurapulse.ai",
        f"DTSTAMP:{now_utc}",
        f"DTSTART;TZID=Asia/Kolkata:{start_fmt}",
        f"DTEND;TZID=Asia/Kolkata:{end_fmt}",
        f"SUMMARY:{summary}",
        f"DESCRIPTION:{desc}",
        f"LOCATION:{clean_city}",
        "STATUS:CONFIRMED",
        "END:VEVENT",
    ]


def generate_calendar_ics(plan: MasterEventPlan) -> str:
    """Generate standard RFC-5545 .ics calendar content.

    Creates all-day events for planning milestones and Asia/Kolkata timed events
    for run-of-show schedule blocks with proper line folding and CRLF line endings.

    Args:
        plan: The MasterEventPlan containing schedule and milestones.

    Returns:
        RFC-5545 compliant iCalendar string formatted with CRLF.
    """
    now_utc = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    event_date = plan.event_date or (date.today() + timedelta(days=90)).strftime("%Y-%m-%d")
    clean_city = _escape_text(plan.location_city or "India")
    cal_name = _escape_text(plan.title or "AuraPulse Event")
    clean_date = event_date.replace("-", "")

    raw_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//AuraPulse AI//Event Planning Engine//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{cal_name}",
        "X-WR-TIMEZONE:Asia/Kolkata",
        "BEGIN:VTIMEZONE",
        "TZID:Asia/Kolkata",
        "X-LIC-LOCATION:Asia/Kolkata",
        "BEGIN:STANDARD",
        "TZOFFSETFROM:+0530",
        "TZOFFSETTO:+0530",
        "TZNAME:IST",
        "DTSTART:19700101T000000",
        "END:STANDARD",
        "END:VTIMEZONE",
    ]

    for ms in plan.planning_milestones or []:
        raw_lines.extend(_vevent_for_milestone(ms, now_utc, clean_city))

    for block in plan.schedule or []:
        raw_lines.extend(_vevent_for_block(block, now_utc, clean_city, clean_date))

    raw_lines.append("END:VCALENDAR")
    folded_blocks = [_fold_line(line) for line in raw_lines]
    return "\r\n".join(folded_blocks) + "\r\n"


def generate_google_calendar_web_intent(
    title: str, start_iso: str, end_iso: str, details: str, location: str = "India"
) -> str:
    """Generate a zero-permission Google Calendar web template URL.

    Args:
        title: Event title.
        start_iso: Start datetime in YYYYMMDDTHHmmss format.
        end_iso: End datetime in YYYYMMDDTHHmmss format.
        details: Event description.
        location: Event venue or city location.

    Returns:
        Google Calendar web intent link.
    """
    params = {
        "action": "TEMPLATE",
        "text": title,
        "dates": f"{start_iso}/{end_iso}",
        "details": details,
        "location": location,
        "ctz": "Asia/Kolkata",
    }
    return f"https://calendar.google.com/calendar/render?{urllib.parse.urlencode(params)}"


def sync_schedule_to_google_calendar(
    calendar_id: str,
    event_title: str,
    schedule_blocks: list[dict[str, Any]],
    event_date_prefix: str | None = None,
) -> dict[str, Any]:
    """Generate calendar synchronization links for run-of-show blocks.

    Args:
        calendar_id: Target calendar identifier.
        event_title: Event title to prefix calendar entries.
        schedule_blocks: List of schedule block dictionaries.
        event_date_prefix: Date prefix formatted as YYYY-MM-DD.

    Returns:
        Summary dict containing synced_events with web intent URLs.
    """
    if not event_date_prefix:
        event_date_prefix = default_event_date(90)
    synced_events = []
    clean_date = event_date_prefix.replace("-", "")

    for block in schedule_blocks:
        st = block.get("start_time_iso", "10:00")
        et = block.get("end_time_iso", "11:00")
        st_parts = st.split(":")
        et_parts = et.split(":")
        s_iso = f"{clean_date}T{st_parts[0].zfill(2)}{st_parts[1].zfill(2) if len(st_parts) > 1 else '00'}00"
        e_iso = f"{clean_date}T{et_parts[0].zfill(2)}{et_parts[1].zfill(2) if len(et_parts) > 1 else '00'}00"

        intent = generate_google_calendar_web_intent(
            title=f"{event_title}: {block.get('activity', 'Activity')}",
            start_iso=s_iso,
            end_iso=e_iso,
            details=f"Phase: {block.get('phase', 'Phase')} | Responsible: {block.get('responsible_party', 'Lead')}",
        )
        synced_events.append(
            {
                "block_id": block.get("block_id"),
                "activity": block.get("activity"),
                "calendar_link": intent,
                "status": "READY",
            }
        )

    return {
        "event_title": event_title,
        "total_blocks_synced": len(synced_events),
        "synced_events": synced_events,
        "status": "SUCCESS",
        "export_mode": "RFC-5545 / Web Intent",
    }
