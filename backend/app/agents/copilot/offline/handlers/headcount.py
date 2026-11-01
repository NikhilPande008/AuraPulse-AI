import re

from backend.app.agents.copilot.models import CopilotResult
from backend.app.agents.copilot.offline import messages
from backend.app.agents.copilot.offline.handlers.base import IntentHandler
from backend.app.agents.copilot.tools import execute_set_headcount
from backend.app.schemas.event_plan import MasterEventPlan

HC_POS_PATTERNS = (
    re.compile(r"(?:add|increase)\s+(\d+)\s*(?:more\s+)?(?:guests?|pax|people)?"),
    re.compile(r"(?:add|increase)\s+(?:guests?|pax|people|headcount)\s+by\s+(\d+)"),
    re.compile(r"(\d+)\s*(?:more\s+)?(?:guests?|pax|people)\s*(?:add|increase)"),
    re.compile(r"(\d+)\s*(?:मेहमान|अतिथि)\s*(?:और\s*)?(?:जोड़ो|बढ़ाओ|जोड़ो|बढ़ाओ)"),
    re.compile(r"(\d+)\s+और\s+(?:मेहमान|अतिथि)"),
    re.compile(r"(\d+)\s+(?:लोग|व्यक्ति)\s+और"),
    re.compile(r"(\d+)\s*(?:पाहुणे)\s*(?:वाढवा|जोडा)"),
    re.compile(r"(?:जोड़ो|बढ़ाओ|जोड़ो|बढ़ाओ)\s*(\d+)\s*(?:मेहमान|अतिथि|लोग)"),
    re.compile(r"(?:वाढवा|जोडा)\s*(\d+)\s*(?:पाहुणे)"),
    re.compile(r"(\d+)\s*(?:मेहमान|अतिथि|पाहुणे)\s*(?:अधिक)"),
)

HC_NEG_PATTERNS = (
    re.compile(r"(?:reduce|cut|remove|decrease)\s+(\d+)\s*(?:guests?|pax|people)?"),
    re.compile(r"(?:reduce|cut|remove|decrease)\s+(?:guests?|pax|people|headcount)\s+by\s+(\d+)"),
    re.compile(r"(\d+)\s*(?:guests?|pax|people)\s*(?:less|fewer|reduce|cut|remove)"),
    re.compile(r"(\d+)\s*(?:मेहमान|अतिथि|लोग)\s*कम(?:\s*(?:करो|करें|कीजिए))?"),
    re.compile(r"(?:कम\s*(?:करो|करें|कीजिए))\s*(\d+)\s*(?:मेहमान|अतिथि|लोग)?"),
    re.compile(r"(\d+)\s*(?:पाहुणे|लोक)\s*कमी(?:\s*(?:करा))?"),
    re.compile(r"(?:कमी\s*करा)\s*(\d+)\s*(?:पाहुणे|लोक)?"),
)

HC_ABS_PATTERNS = (
    re.compile(r"(?:set|change)\s+(?:headcount\s+to\s+|guests?\s+to\s+|guests?\s*=\s*|pax\s+to\s+)(\d+)"),
    re.compile(r"(?:headcount|guests?|pax)\s*(?:to|=)\s*(\d+)"),
    re.compile(r"(?:set|change)\s+(?:headcount|guests?|pax)\s+(\d+)"),
    re.compile(r"(?:set|change)\s+(\d+)\s*(?:guests?|pax|people)"),
    re.compile(r"(\d+)\s*(?:मेहमान|अतिथि|पाहुणे)\s*(?:करो|करें|करा)"),
    re.compile(r"(?:मेहमान|अतिथि|पाहुणे|हेडकाउंट)\s*(\d+)\s*(?:करो|करें|करा)"),
    re.compile(r"(?:मेहमान|अतिथि|पाहुणे|हेडकाउंट)\s*(?:संख्या\s*)?(\d+)"),
)


def _match_first(patterns: tuple[re.Pattern[str], ...], text: str) -> re.Match[str] | None:
    for p in patterns:
        m = p.search(text)
        if m:
            return m
    return None


class HeadcountIntentHandler(IntentHandler):
    """Handles relative and absolute headcount updates."""

    def matches(self, prompt: str) -> bool:
        lower = prompt.lower()
        return bool(
            _match_first(HC_POS_PATTERNS, lower)
            or _match_first(HC_NEG_PATTERNS, lower)
            or _match_first(HC_ABS_PATTERNS, lower)
        )

    def _resolve_target_hc(self, prompt: str, old_hc: int) -> int | None:
        lower = prompt.lower()
        pos = _match_first(HC_POS_PATTERNS, lower)
        if pos:
            return old_hc + int(pos.group(1))
        neg = _match_first(HC_NEG_PATTERNS, lower)
        if neg:
            return old_hc - int(neg.group(1))
        abs_hc = _match_first(HC_ABS_PATTERNS, lower)
        if abs_hc:
            return int(abs_hc.group(1))
        return None

    def apply(self, plan: MasterEventPlan, prompt: str, lang: str) -> CopilotResult:
        old_hc = getattr(plan, "headcount", None) or 100
        target_hc = self._resolve_target_hc(prompt, old_hc)

        if target_hc is None or target_hc < 1 or target_hc > 10000:
            tmpl = messages.HEADCOUNT_RANGE_WARNINGS.get(lang, messages.HEADCOUNT_RANGE_WARNINGS["en"])
            reply = tmpl.format(target_hc=target_hc or 0, old_hc=old_hc)
            return CopilotResult(
                updated_plan=plan.model_copy(deep=True),
                diff=None,
                reply=reply,
                suggested_ideas=["Enter a valid guest count between 1 and 10,000"],
                mode="offline_rules",
            )

        updated_plan, diff = execute_set_headcount(plan, target_hc)
        reply_tmpl = messages.HEADCOUNT_REPLIES.get(lang, messages.HEADCOUNT_REPLIES["en"])
        reply = reply_tmpl.format(old_hc=old_hc, target_hc=target_hc)
        ideas_raw = messages.HEADCOUNT_IDEAS.get(lang, messages.HEADCOUNT_IDEAS["en"])
        ideas = [i.format(target_hc=target_hc) for i in ideas_raw]

        return CopilotResult(
            updated_plan=updated_plan,
            diff=diff,
            reply=reply,
            suggested_ideas=ideas,
            mode="offline_rules",
        )
