"""Timeline slippage contingency handler for Pulse Engine."""

import copy

from ...schemas import (
    CrisisTrigger,
    DiffAction,
    MasterEventPlan,
    ScheduleBlock,
    ScheduleDiffItem,
)
from .models import CrisisExecutionResult


def shift_time_str(time_str: str, minutes_to_add: int) -> tuple[str, bool]:
    """Helper to shift HH:MM time strings by minutes.

    Returns (new_time_str, next_day_flag) without silent midnight wrap-around.
    """
    try:
        parts = time_str.split(":")
        h = int(parts[0])
        m = int(parts[1])
        total_m = h * 60 + m + minutes_to_add
        next_day = total_m >= 24 * 60
        wrapped_m = total_m % (24 * 60)
        return f"{wrapped_m // 60:02d}:{wrapped_m % 60:02d}", next_day
    except (ValueError, IndexError):
        return time_str, False


def _find_delayed_start_min(schedule: list[ScheduleBlock]) -> int | None:
    keywords = ("procession", "baraat", "ceremony", "arrival", "dinner", "banquet", "party")
    for block in schedule:
        if any(keyword in block.phase.lower() or keyword in block.activity.lower() for keyword in keywords):
            try:
                parts = block.start_time_iso.split(":")
                return int(parts[0]) * 60 + int(parts[1])
            except (ValueError, IndexError, AttributeError):
                pass
    return None


def _should_shift_block(block: ScheduleBlock, delayed_start_min: int | None) -> bool:
    if delayed_start_min is not None:
        try:
            parts = block.start_time_iso.split(":")
            b_min = int(parts[0]) * 60 + int(parts[1])
            return b_min >= delayed_start_min
        except (ValueError, IndexError, AttributeError):
            return True
    return any(
        kw in block.phase
        for kw in (
            "Procession",
            "Baraat",
            "Ceremony",
            "Dinner",
            "Banquet",
            "Party",
            "Afterparty",
            "Dance",
            "Feast",
        )
    )


def _shift_schedule_blocks(
    schedule: list[ScheduleBlock], delay: int, delayed_start_min: int | None
) -> tuple[list[ScheduleDiffItem], bool]:
    diffs: list[ScheduleDiffItem] = []
    has_midnight = False
    for block in schedule:
        if not _should_shift_block(block, delayed_start_min):
            continue
        orig_block = copy.deepcopy(block)
        new_start, start_next_day = shift_time_str(block.start_time_iso, delay)
        new_end, end_next_day = shift_time_str(block.end_time_iso, delay)
        block.start_time_iso = new_start
        block.end_time_iso = new_end
        if start_next_day or end_next_day:
            has_midnight = True
            if "(+1 day)" not in block.activity:
                block.activity += " (+1 day)"
        diffs.append(
            ScheduleDiffItem(
                block_id=block.block_id,
                action=DiffAction.MODIFIED,
                original_block=orig_block,
                updated_block=block,
                reason=f"Cascaded schedule block by +{delay} min to accommodate procession delay."
                + (" Crosses midnight (+1 day)." if (start_next_day or end_next_day) else ""),
            )
        )
    return diffs, has_midnight


async def _handle_timeline_slippage(
    updated_plan: MasterEventPlan, trigger: CrisisTrigger, original_total: float
) -> tuple[MasterEventPlan, CrisisExecutionResult]:
    res = CrisisExecutionResult()
    delay = trigger.delay_minutes or 60
    res.mitigations.append(f"Ripple-shift schedule by +{delay} minutes with catering freshness lock")
    res.narrative_paragraphs.append(
        f"TIMELINE SLIPPAGE PROTOCOL: Event procession/VIP delayed by {delay} minutes. "
        "Graph dependency solver shifted subsequent schedule blocks starting at or after the delay forward, "
        "while coordinating with catering head to maintain holding temperature."
    )

    delayed_start = _find_delayed_start_min(updated_plan.schedule)
    sched_diffs, has_midnight = _shift_schedule_blocks(updated_plan.schedule, delay, delayed_start)
    res.schedule_diffs.extend(sched_diffs)

    if has_midnight:
        res.mitigations.append("Schedule block crossed midnight: flagged as +1 day event wrap-around.")

    res.mitigations.append("Notified kitchen dispatch to adjust chafing dish firing times to prevent overcooking.")
    res.mitigations.append("Re-export the updated run-of-show via the iCal (.ics) / Google Calendar buttons.")
    return updated_plan, res
