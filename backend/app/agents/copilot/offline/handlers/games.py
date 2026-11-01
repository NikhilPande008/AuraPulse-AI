from .....schemas.event_plan import MasterEventPlan
from .....services.budget import recompute_totals
from ...models import CopilotResult
from ...tools import execute_add_item
from .. import messages
from .base import IntentHandler


class GamesIntentHandler(IntentHandler):
    """Handles birthday party games and emcee addition."""

    def matches(self, prompt: str) -> bool:
        lower = prompt.lower()
        return "game" in lower or ("birthday" in lower and "master" in lower)

    def apply(self, plan: MasterEventPlan, prompt: str, lang: str) -> CopilotResult:
        new_plan = plan.model_copy(deep=True)
        active_diff = None
        if not any("game" in it.name.lower() for it in new_plan.boq):
            new_plan, diff_add = execute_add_item(
                new_plan,
                category="Entertainment & Games",
                name="Interactive Game Master & Emcee",
                specification="Professional host for customized trivia, scavenger hunt, and party games",
                quantity=1.0,
                unit="host",
                rate_inr=25000.0,
                priority="Operational",
            )
            active_diff = diff_add
        recompute_totals(new_plan)
        return CopilotResult(
            updated_plan=new_plan,
            diff=active_diff,
            reply=messages.GAMES_REPLY,
            suggested_ideas=messages.GAMES_IDEAS,
            mode="offline_rules",
        )
