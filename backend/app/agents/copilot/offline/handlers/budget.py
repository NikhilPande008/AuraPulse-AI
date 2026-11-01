import re

from .....schemas.event_plan import MasterEventPlan
from ...models import CopilotResult
from ...tools import execute_scale_budget
from .. import messages
from .base import IntentHandler

BUDGET_CUT_PATTERNS = (
    re.compile(r"(?:cut|reduce|down|slash)\s+(?:the\s+)?budget\s+(?:by\s+)?(\d+)\s*(?:%|percent)"),
    re.compile(r"budget\s+(?:cut|down|drop)\s+(?:by\s+)?(\d+)\s*(?:%|percent)"),
    re.compile(r"(\d+)\s*(?:%|percent)\s*(?:budget\s+cut|cut|reduction)"),
    re.compile(r"बजट\s+(?:को\s+)?(\d+)\s*(?:%|प्रतिशत)?\s*कम\s*(?:करो|करें)"),
    re.compile(r"(\d+)\s*(?:%|प्रतिशत)\s*बजट\s*कम"),
    re.compile(r"बजेट\s+(\d+)\s*%\s*कमी\s*करा"),
    re.compile(r"(\d+)\s*%\s*बजेट\s*कमी"),
)


def _match_first(patterns: tuple[re.Pattern[str], ...], text: str) -> re.Match[str] | None:
    for p in patterns:
        m = p.search(text)
        if m:
            return m
    return None


class BudgetScaleIntentHandler(IntentHandler):
    """Handles budget cuts and expansions."""

    def matches(self, prompt: str) -> bool:
        return bool(_match_first(BUDGET_CUT_PATTERNS, prompt.lower()))

    def apply(self, plan: MasterEventPlan, prompt: str, lang: str) -> CopilotResult:
        m = _match_first(BUDGET_CUT_PATTERNS, prompt.lower())
        pct = float(m.group(1)) if m else 20.0
        pct = -abs(pct)

        updated_plan, diff = execute_scale_budget(plan, pct)
        reply_tmpl = messages.BUDGET_CUT_REPLIES.get(lang, messages.BUDGET_CUT_REPLIES["en"])
        reply = reply_tmpl.format(
            abs_pct=abs(pct),
            pct=pct,
            total=updated_plan.current_estimated_total,
            limit=updated_plan.total_budget_limit,
        )
        ideas = messages.BUDGET_CUT_IDEAS.get(lang, messages.BUDGET_CUT_IDEAS["en"])

        return CopilotResult(
            updated_plan=updated_plan,
            diff=diff,
            reply=reply,
            suggested_ideas=ideas,
            mode="offline_rules",
        )
