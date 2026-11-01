import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from ..schemas import MasterEventPlan
from ..services.timeline import default_event_date


def _escape_text(text: str) -> str:
    """Escapes RFC 5545 TEXT values: \\ -> \\\\, ; -> \\;, , -> \\,, \\n -> \\n."""
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\\", "\\\\")
    text = text.replace(";", "\\;").replace(",", "\\,")
    text = text.replace("\n", "\\n")
    return text


def _fold_line(line: str) -> str:
    """
    Folds an RFC 5545 line so no physical line exceeds 75 octets in UTF-8.
    Continuation lines begin with a single ASCII space.
    """
    encoded = line.encode("utf-8")
    if len(encoded) <= 75:
        return line

    chunks: List[str] = []
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


def generate_calendar_ics(plan: MasterEventPlan) -> str:
    """
    RFC-5545 Calendar Export (CR-14 / K23):
    Generates standard RFC-5545 .ics calendar content with:
    - Escaped text values (\\, ;, ,, \\n)
    - 75-octet line folding
    - Planning milestones as all-day events on calculated due_date.
    - Day-of schedule blocks on event_date with TZID=Asia/Kolkata.
    - Standard CRLF (\\r\\n) line endings.
    """
    now_utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    event_date = plan.event_date or (date.today() + timedelta(days=90)).strftime("%Y-%m-%d")
    clean_city = _escape_text(plan.location_city or "India")
    cal_name = _escape_text(plan.title or "AuraPulse Event")

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

    # 1. Backwards Planning Milestones as All-Day Events
    for ms in plan.planning_milestones or []:
        due_str = ms.due_date.replace("-", "")
        try:
            d_obj = datetime.strptime(ms.due_date, "%Y-%m-%d").date()
            next_day_str = (d_obj + timedelta(days=1)).strftime("%Y%m%d")
        except Exception:
            next_day_str = due_str

        summary = _escape_text(f"[{ms.phase}] {ms.title}")
        desc = _escape_text(
            f"AuraPulse Milestone\n"
            f"Category: {ms.category}\n"
            f"Deliverable: {ms.description}\n"
            f"Phase: {ms.phase}"
        )

        raw_lines.extend([
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
        ])

    # 2. Day-of Run-of-Show Schedule Blocks (TZID=Asia/Kolkata)
    clean_date = event_date.replace("-", "")

    for block in plan.schedule or []:
        start_raw = block.start_time_iso
        end_raw = block.end_time_iso

        if "T" in start_raw:
            try:
                dt_s = datetime.fromisoformat(start_raw)
                start_fmt = dt_s.strftime("%Y%m%dT%H%M%S")
            except Exception:
                start_fmt = f"{clean_date}T100000"
        else:
            parts = start_raw.split(":")
            hh = parts[0].zfill(2)
            mm = parts[1].zfill(2) if len(parts) > 1 else "00"
            start_fmt = f"{clean_date}T{hh}{mm}00"

        if "T" in end_raw:
            try:
                dt_e = datetime.fromisoformat(end_raw)
                end_fmt = dt_e.strftime("%Y%m%dT%H%M%S")
            except Exception:
                end_fmt = f"{clean_date}T110000"
        else:
            parts = end_raw.split(":")
            hh = parts[0].zfill(2)
            mm = parts[1].zfill(2) if len(parts) > 1 else "00"
            end_fmt = f"{clean_date}T{hh}{mm}00"

        outdoor_tag = " [OUTDOOR ZONE - WEATHER WATCH]" if block.is_outdoor else " [INDOOR / COVERED]"
        summary = _escape_text(f"[{block.phase}] {block.activity}{outdoor_tag}")
        desc = _escape_text(
            f"AuraPulse Run-of-Show\n"
            f"Phase: {block.phase}\n"
            f"Responsible Party: {block.responsible_party}\n"
            f"Zone: {'Outdoor Zone (Weather Alert)' if block.is_outdoor else 'Covered / Indoor Zone'}\n"
            f"Block ID: {block.block_id}"
        )

        raw_lines.extend([
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
        ])

    raw_lines.append("END:VCALENDAR")

    # Apply 75-octet line folding
    folded_blocks = [_fold_line(line) for line in raw_lines]
    return "\r\n".join(folded_blocks) + "\r\n"


def generate_google_calendar_web_intent(
    title: str,
    start_iso: str,
    end_iso: str,
    details: str,
    location: str = "India"
) -> str:
    """
    Generates standard zero-permission Google Calendar web intent link (CR-14):
    https://calendar.google.com/calendar/render?action=TEMPLATE&text={title}&dates={start}/{end}&details={details}&ctz=Asia/Kolkata
    """
    import urllib.parse
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
    schedule_blocks: List[Dict[str, Any]],
    event_date_prefix: Optional[str] = None
) -> Dict[str, Any]:
    """
    Public schedule exporter for run-of-show blocks.
    Replaced silent service-account write with zero-permission client intent links.
    """
    if not event_date_prefix:
        event_date_prefix = default_event_date(90)
    synced_events = []
    for block in schedule_blocks:
        st = block.get("start_time_iso", "10:00")
        et = block.get("end_time_iso", "11:00")
        clean_date = event_date_prefix.replace("-", "")
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
        synced_events.append({
            "block_id": block.get("block_id"),
            "activity": block.get("activity"),
            "calendar_link": intent,
            "status": "READY"
        })

    return {
        "event_title": event_title,
        "total_blocks_synced": len(synced_events),
        "synced_events": synced_events,
        "status": "SUCCESS",
        "export_mode": "RFC-5545 / Web Intent"
    }
