import re
from datetime import date, datetime, timedelta

from backend.app.agents.copilot.diff_builder import build_contingency_diff
from backend.app.agents.copilot.models import CopilotResult
from backend.app.agents.copilot.offline import messages
from backend.app.agents.copilot.offline.handlers.base import IntentHandler
from backend.app.agents.copilot.tools import execute_set_event_date
from backend.app.schemas.contingency import CrisisTriggerType
from backend.app.schemas.event_plan import MasterEventPlan
from backend.app.services.timeline import default_event_date

WORD_TO_NUM: dict[str, int] = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "एक": 1,
    "दो": 2,
    "तीन": 3,
    "चार": 4,
    "पाच": 5,
    "दोन": 2,
}

DATE_REL_PATTERNS = (
    re.compile(
        r"(?:move|shift|reschedule)?\s*(?:it\s+)?(?:by\s+)?(\d+|one|two|three|four)\s+(weeks?|days?|months?)\s+(earlier|prior|before|ahead|later|after)"
    ),
    re.compile(r"(\d+|one|two|three|four)\s+(weeks?|days?|months?)\s+(earlier|prior|before|ahead|later|after)"),
    re.compile(r"(\d+|दो|दोन|एक|तीन|चार)\s*(?:सप्ताह|हफ्ते|आठवडे)\s*(?:पहले|आधी|बाद|नंतर)"),
    re.compile(r"(?:पहले|आधी|बाद|नंतर)\s*(\d+|दो|दोन|एक|तीन|चार)\s*(?:सप्ताह|हफ्ते|आठवडे)"),
)

DATE_ABS_PATTERNS = (
    re.compile(
        r"(?:move|shift|change|set|reschedule|तारीख|दिनांक)\s+(?:event\s+)?(?:date\s+)?(?:to\s+|ला\s+|को\s+)?(\d{4}-\d{2}-\d{2})"
    ),
    re.compile(r"^.*(\d{4}-\d{2}-\d{2}).*$"),
)


def _match_first(patterns: tuple[re.Pattern[str], ...], text: str) -> re.Match[str] | None:
    for p in patterns:
        m = p.search(text)
        if m:
            return m
    return None


def _parse_relative_delta(cnt: int, full: str) -> int:
    if "month" in full or "महिने" in full:
        return cnt * 30
    if "day" in full or "दिवस" in full or "दिन" in full:
        return cnt
    return cnt * 7


class DateMoveIntentHandler(IntentHandler):
    """Handles relative and absolute event date moves."""

    def matches(self, prompt: str) -> bool:
        lower = prompt.lower()
        return bool(_match_first(DATE_REL_PATTERNS, lower) or _match_first(DATE_ABS_PATTERNS, lower))

    def _resolve_relative(self, prompt: str, curr_dt: date) -> tuple[str, date]:
        m = _match_first(DATE_REL_PATTERNS, prompt.lower())
        if not m:
            return "", curr_dt
        raw_cnt = m.group(1)
        cnt = WORD_TO_NUM.get(raw_cnt, int(raw_cnt) if raw_cnt.isdigit() else 2)
        full = m.group(0)
        is_earlier = any(w in full for w in ["earlier", "prior", "before", "ahead", "आधी", "पहले"])
        days = _parse_relative_delta(cnt, full)
        target = curr_dt - timedelta(days=days) if is_earlier else curr_dt + timedelta(days=days)
        return target.strftime("%Y-%m-%d"), target

    def _resolve_target_date(self, prompt: str, plan: MasterEventPlan) -> tuple[str | None, date | None]:
        lower = prompt.lower()
        curr_str = plan.event_date or default_event_date(90)
        try:
            curr_dt = datetime.strptime(curr_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            curr_dt = date.today() + timedelta(days=90)

        target_str, target_dt = self._resolve_relative(prompt, curr_dt)
        if target_str:
            return target_str, target_dt

        abs_match = _match_first(DATE_ABS_PATTERNS, lower)
        if abs_match:
            d_str = abs_match.group(1)
            try:
                return d_str, datetime.strptime(d_str, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                return None, None
        return None, None

    def apply(self, plan: MasterEventPlan, prompt: str, lang: str) -> CopilotResult:
        new_plan = plan.model_copy(deep=True)
        target_date_str, target_dt = self._resolve_target_date(prompt, new_plan)
        if not target_date_str or not target_dt:
            return CopilotResult(updated_plan=new_plan, diff=None, reply="Invalid date.", mode="offline_rules")

        if target_dt <= date.today():
            tmpl = messages.DATE_PAST_WARNINGS.get(lang, messages.DATE_PAST_WARNINGS["en"])
            return CopilotResult(
                updated_plan=new_plan,
                diff=None,
                reply=tmpl.format(target_date=target_date_str),
                suggested_ideas=["Choose a future event date"],
                mode="offline_rules",
            )

        new_plan = execute_set_event_date(new_plan, target_date_str)
        curr_date_str = plan.event_date or default_event_date(90)
        diff = build_contingency_diff(
            trigger_type=CrisisTriggerType.TIMELINE_SLIPPAGE,
            description=f"Event date shifted to {target_date_str}",
            summary_narrative=f"Rescheduled event date from {curr_date_str} to {target_date_str}. All planning milestones recalculated backwards from the new date.",
            original_total_inr=new_plan.current_estimated_total,
            new_total_inr=new_plan.current_estimated_total,
            updated_plan=new_plan,
            actionable_mitigations=[f"Notify all booked vendors about the rescheduled date: {target_date_str}"],
            diff_prefix="diff_date",
        )
        reply_tmpl = messages.DATE_REPLIES.get(lang, messages.DATE_REPLIES["en"])
        ideas_raw = messages.DATE_IDEAS.get(lang, messages.DATE_IDEAS["en"])
        ideas = [i.format(target_date=target_date_str) for i in ideas_raw]

        return CopilotResult(
            updated_plan=new_plan,
            diff=diff,
            reply=reply_tmpl.format(target_date=target_date_str),
            suggested_ideas=ideas,
            mode="offline_rules",
        )
