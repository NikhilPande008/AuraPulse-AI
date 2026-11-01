import uuid

from .....schemas.event_plan import (
    MasterEventPlan,
    MilestoneCategory,
    MilestonePhase,
    PlanningMilestone,
)
from .....services.timeline import default_event_date, get_backwards_date
from ...models import CopilotResult
from .. import messages
from .base import IntentHandler


class RitualIntentHandler(IntentHandler):
    """Handles Sakhar Puda ceremony and pooja samagri roadmap milestone."""

    KEYWORDS = ("sakhar", "puda", "pooja", "samagri", "ceremony")

    def matches(self, prompt: str) -> bool:
        lower = prompt.lower()
        return any(k in lower for k in self.KEYWORDS)

    def apply(self, plan: MasterEventPlan, prompt: str, lang: str) -> CopilotResult:
        new_plan = plan.model_copy(deep=True)
        ms_list = list(new_plan.planning_milestones or [])
        if not any("sakhar" in m.title.lower() or "ritual" in m.title.lower() for m in ms_list):
            ms_list.append(
                PlanningMilestone(
                    id=f"ms_sakhar_{uuid.uuid4().hex[:6]}",
                    phase=MilestonePhase.T_MINUS_1_MONTH,
                    title="Sakhar Puda Ritual & Pooja Samagri Audit",
                    description="Conduct formal engagement ceremony, purchase auspicious items and verify priest checklist",
                    due_date=get_backwards_date(new_plan.event_date or default_event_date(90), 30),
                    category=MilestoneCategory.RITUALS,
                    completed=False,
                )
            )
            new_plan.planning_milestones = ms_list
        return CopilotResult(
            updated_plan=new_plan,
            diff=None,
            reply=messages.RITUALS_REPLY,
            suggested_ideas=messages.RITUALS_IDEAS,
            mode="offline_rules",
        )
