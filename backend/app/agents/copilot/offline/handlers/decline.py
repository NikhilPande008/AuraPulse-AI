import re

from backend.app.agents.copilot.models import CopilotResult
from backend.app.agents.copilot.offline import messages
from backend.app.agents.copilot.offline.handlers.base import IntentHandler
from backend.app.schemas.event_plan import MasterEventPlan


class DeclineIntentHandler(IntentHandler):
    """Detects prompt injections and off-topic queries."""

    INJECTION_KEYWORDS = (
        "ignore previous",
        "system prompt",
        "jailbreak",
        "developer mode",
        "pretend you are",
        "disregard all",
        "write a python",
        "write python",
        "solve this math",
        "who is the president",
        "capital of france",
        "stock price",
        "cryptocurrency",
        "bitcoin",
        "tell me a joke",
    )

    EVENT_CONTEXT_WORDS = (
        "event",
        "wedding",
        "birthday",
        "party",
        "anniversary",
        "reception",
        "conference",
        "sangeet",
        "mehendi",
        "haldi",
        "शादी",
        "विवाह",
        "जन्मदिन",
        "कार्यक्रम",
        "लग्न",
        "सोहळा",
        "समारंभ",
        "उत्सव",
        "मेळावा",
    )

    def matches(self, prompt: str) -> bool:
        lower = prompt.lower()
        if any(k in lower for k in self.INJECTION_KEYWORDS):
            return True

        has_context = any(w in lower for w in self.EVENT_CONTEXT_WORDS)
        if bool(re.search(r"\b(essay|homework|assignment)\b", lower)):
            return True
        if any(k in lower for k in ["निबंध", "होमवर्क", "गृहपाठ"]):
            return True
        return bool(re.search(r"\bwrite\s+(?:a\s+)?(?:poem|story|code|program)\b", lower)) and not has_context

    def apply(self, plan: MasterEventPlan, prompt: str, lang: str) -> CopilotResult:
        reply = messages.DECLINE_MESSAGES.get(lang, messages.DECLINE_MESSAGES["en"])
        return CopilotResult(
            updated_plan=plan.model_copy(deep=True),
            diff=None,
            reply=reply,
            suggested_ideas=[],
            declined=True,
            mode="offline_rules",
        )
