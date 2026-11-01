from backend.app.agents.copilot.models import CopilotResult
from backend.app.agents.copilot.offline import messages
from backend.app.agents.copilot.offline.handlers.base import IntentHandler
from backend.app.schemas.event_plan import MasterEventPlan
from backend.app.services.budget import recompute_totals


class CateringIntentHandler(IntentHandler):
    """Handles regional and cultural catering cuisine swaps."""

    KEYWORDS = ("puneri", "marathi", "cuisine", "food", "menu", "puran poli", "catering", "शाकाहारी", "जेवण")

    def matches(self, prompt: str) -> bool:
        lower = prompt.lower()
        return any(k in lower for k in self.KEYWORDS)

    def apply(self, plan: MasterEventPlan, prompt: str, lang: str) -> CopilotResult:
        new_plan = plan.model_copy(deep=True)
        for item in new_plan.boq:
            if item.category.lower() in ["catering", "food"]:
                item.name = "Authentic Puneri Maharashtrian Banquet & Live Faral Stations"
                item.specification = (
                    "Traditional pure-ghee Puran Poli, Katachi Amti, Kothimbir Vadi, "
                    "and artisanal Ukdiche Modak live counter"
                )
                item.status = "MODIFIED"
                break
        recompute_totals(new_plan)

        reply = messages.CATERING_REPLIES.get(lang, messages.CATERING_REPLIES["en"])
        ideas = messages.CATERING_IDEAS.get(lang, messages.CATERING_IDEAS["en"])

        return CopilotResult(
            updated_plan=new_plan,
            diff=None,
            reply=reply,
            suggested_ideas=ideas,
            mode="offline_rules",
        )
