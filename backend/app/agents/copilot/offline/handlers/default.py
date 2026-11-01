from backend.app.agents.copilot.models import CopilotResult
from backend.app.agents.copilot.offline import messages
from backend.app.agents.copilot.offline.handlers.base import IntentHandler
from backend.app.schemas.event_plan import MasterEventPlan


class DefaultIntentHandler(IntentHandler):
    """Fallback handler providing grounded contextual overview."""

    def matches(self, prompt: str) -> bool:
        return True

    def apply(self, plan: MasterEventPlan, prompt: str, lang: str) -> CopilotResult:
        tmpl = messages.DEFAULT_REPLIES.get(lang, messages.DEFAULT_REPLIES["en"])
        reply = tmpl.format(
            prompt=prompt,
            title=plan.title,
            total=plan.current_estimated_total,
            limit=plan.total_budget_limit,
        )
        ideas = messages.DEFAULT_IDEAS.get(lang, messages.DEFAULT_IDEAS["en"])
        return CopilotResult(
            updated_plan=plan.model_copy(deep=True),
            diff=None,
            reply=reply,
            suggested_ideas=ideas,
            mode="offline_rules",
        )
