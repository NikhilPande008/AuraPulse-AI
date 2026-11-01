"""Helper for constructing standardized ContingencyDiff instances."""

import uuid
from datetime import datetime

from ...schemas.contingency import (
    BOQDiffItem,
    ContingencyDiff,
    CrisisTrigger,
    CrisisTriggerType,
    ScheduleDiffItem,
)
from ...schemas.event_plan import MasterEventPlan


def build_contingency_diff(
    trigger_type: CrisisTriggerType,
    description: str,
    summary_narrative: str,
    original_total_inr: float,
    new_total_inr: float,
    updated_plan: MasterEventPlan,
    boq_diffs: list[BOQDiffItem] | None = None,
    schedule_diffs: list[ScheduleDiffItem] | None = None,
    actionable_mitigations: list[str] | None = None,
    budget_cut_percent: float | None = None,
    diff_prefix: str = "diff",
    budget_delta_override: float | None = None,
) -> ContingencyDiff:
    """Build a standardized ContingencyDiff instance for plan alterations.

    Args:
        trigger_type: Category of crisis or replan trigger.
        description: Description of the replan event or trigger.
        summary_narrative: Human-readable narrative of changes.
        original_total_inr: Baseline spend prior to changes.
        new_total_inr: Updated spend following changes.
        updated_plan: The newly modified MasterEventPlan.
        boq_diffs: Optional list of item modifications.
        schedule_diffs: Optional list of timeline adjustments.
        actionable_mitigations: Suggested mitigation checklist items.
        budget_cut_percent: Percentage reduction if applicable.
        diff_prefix: Identifier prefix for diff_id.
        budget_delta_override: Explicit budget delta value if applicable.

    Returns:
        Populated ContingencyDiff model instance.
    """
    trigger = CrisisTrigger(
        trigger_type=trigger_type,
        description=description,
        budget_cut_percent=budget_cut_percent,
    )
    delta = budget_delta_override if budget_delta_override is not None else round(new_total_inr - original_total_inr, 2)
    return ContingencyDiff(
        diff_id=f"{diff_prefix}_{uuid.uuid4().hex[:6]}",
        trigger=trigger,
        timestamp_iso=datetime.now().isoformat(),
        summary_narrative=summary_narrative,
        original_total_inr=original_total_inr,
        new_total_inr=new_total_inr,
        budget_delta_inr=delta,
        boq_diffs=boq_diffs or [],
        schedule_diffs=schedule_diffs or [],
        updated_plan=updated_plan,
        actionable_mitigations=actionable_mitigations or [],
    )
