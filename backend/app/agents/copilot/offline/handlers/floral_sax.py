from .....schemas.contingency import ContingencyDiff
from .....schemas.event_plan import MasterEventPlan
from .....services.budget import recompute_totals
from ...models import CopilotResult
from ...tools import execute_add_item
from .. import messages
from .base import IntentHandler


def _cut_floral_budget(plan: MasterEventPlan) -> None:
    """Reduces floral line item rates by 20%."""
    for it in plan.boq:
        if any(w in it.category.lower() or w in it.name.lower() for w in ["floral", "decor", "flower"]):
            it.estimated_rate_inr = round(it.estimated_rate_inr * 0.8, 2)
            it.total_cost_inr = round(it.quantity * it.estimated_rate_inr, 2)
            it.mirror_synonyms()
            it.status = "MODIFIED"


def _add_sax_item(new_plan: MasterEventPlan) -> tuple[MasterEventPlan, ContingencyDiff | None]:
    if any("sax" in it.name.lower() for it in new_plan.boq):
        return new_plan, None
    return execute_add_item(
        new_plan,
        category="Entertainment & Music",
        name="Live Solo Saxophonist (Sunset & Dinner Sets)",
        specification="3 hours live performance with wireless mic & monitor",
        quantity=1.0,
        unit="artist",
        rate_inr=35000.0,
        priority="Operational",
    )


class FloralSaxIntentHandler(IntentHandler):
    """Handles floral cut and solo saxophonist addition."""

    def matches(self, prompt: str) -> bool:
        lower = prompt.lower()
        return "sax" in lower or ("floral" in lower and any(w in lower for w in ["cut", "20", "reduce"]))

    def apply(self, plan: MasterEventPlan, prompt: str, lang: str) -> CopilotResult:
        new_plan = plan.model_copy(deep=True)
        lower = prompt.lower()
        active_diff = None

        if "floral" in lower:
            _cut_floral_budget(new_plan)

        if "sax" in lower:
            new_plan, active_diff = _add_sax_item(new_plan)

        recompute_totals(new_plan)
        return CopilotResult(
            updated_plan=new_plan,
            diff=active_diff,
            reply=messages.FLORAL_SAX_REPLY,
            suggested_ideas=messages.FLORAL_SAX_IDEAS,
            mode="offline_rules",
        )
