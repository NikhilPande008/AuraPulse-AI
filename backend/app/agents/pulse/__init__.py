"""Pulse Engine: Contingency evaluation and crisis management package."""

import uuid
from collections.abc import Callable, Coroutine
from datetime import datetime
from typing import Any

from ...schemas import (
    ContingencyDiff,
    CrisisTrigger,
    CrisisTriggerType,
    MasterEventPlan,
)
from ...services.budget import recompute_totals
from .budget import _handle_budget_compression
from .models import CrisisExecutionResult
from .narrative import _generate_crisis_narrative
from .supply import _handle_supply_failure
from .timeline import _handle_timeline_slippage, shift_time_str
from .weather import _handle_weather_risk

CRISIS_STRATEGIES: dict[
    CrisisTriggerType,
    Callable[
        [MasterEventPlan, CrisisTrigger, float],
        Coroutine[Any, Any, tuple[MasterEventPlan, CrisisExecutionResult]],
    ],
] = {
    CrisisTriggerType.WEATHER_RISK: _handle_weather_risk,
    CrisisTriggerType.BUDGET_COMPRESSION: _handle_budget_compression,
    CrisisTriggerType.TIMELINE_SLIPPAGE: _handle_timeline_slippage,
    CrisisTriggerType.SUPPLY_FAILURE: _handle_supply_failure,
}


async def evaluate_contingency(plan: MasterEventPlan, trigger: CrisisTrigger) -> ContingencyDiff:
    """Evaluate crisis triggers deterministically and generate contingency diffs.

    Dispatches to dedicated crisis handlers based on trigger type (weather, budget compression,
    timeline slippage, supply failure), balances budget against the plan ceiling, and generates
    an optional AI narrative summary.

    Args:
        plan: The baseline MasterEventPlan to adapt.
        trigger: The CrisisTrigger event describing the disruption.

    Returns:
        A ContingencyDiff detailing budget, BOQ, and schedule adaptations.
    """
    diff_id = f"diff_{uuid.uuid4().hex[:8]}"
    timestamp = datetime.now().isoformat()
    original_total = plan.current_estimated_total

    updated_plan = plan.model_copy(deep=True)
    recompute_totals(updated_plan)

    strategy = CRISIS_STRATEGIES.get(trigger.trigger_type)
    if strategy:
        updated_plan, res = await strategy(updated_plan, trigger, original_total)
    else:
        res = CrisisExecutionResult()

    recompute_totals(updated_plan)
    new_total = updated_plan.current_estimated_total
    budget_delta = round(new_total - original_total, 2)

    narrative = await _generate_crisis_narrative(
        plan,
        trigger,
        original_total,
        new_total,
        updated_plan.total_budget_limit,
        len(res.boq_diffs),
        len(res.schedule_diffs),
    )
    if narrative:
        res.narrative_paragraphs.append(narrative)

    return ContingencyDiff(
        diff_id=diff_id,
        trigger=trigger,
        timestamp_iso=timestamp,
        summary_narrative="\n\n".join(res.narrative_paragraphs),
        original_total_inr=original_total,
        new_total_inr=new_total,
        budget_delta_inr=budget_delta,
        boq_diffs=res.boq_diffs,
        schedule_diffs=res.schedule_diffs,
        updated_plan=updated_plan,
        actionable_mitigations=res.mitigations,
    )


__all__ = [
    "CrisisExecutionResult",
    "evaluate_contingency",
    "shift_time_str",
]
