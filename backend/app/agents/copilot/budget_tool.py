"""Deterministic budget scaling tools and helpers for copilot operations."""

from ...schemas.contingency import (
    BOQDiffItem,
    ContingencyDiff,
    CrisisTriggerType,
    DiffAction,
)
from ...schemas.event_plan import (
    BOQItem,
    MasterEventPlan,
    PriorityTier,
)
from ...services.budget import recompute_totals
from .diff_builder import build_contingency_diff


def _scale_budget_expansion(
    plan: MasterEventPlan, original_limit: float, original_total: float, factor: float, percentage: float
) -> tuple[MasterEventPlan, ContingencyDiff]:
    """Handles non-negative budget scaling (expansion)."""
    new_limit = round(original_limit * factor, 2)
    plan.total_budget_limit = new_limit
    narrative = (
        f"Budget ceiling increased from ₹{original_limit:,.2f} to ₹{new_limit:,.2f}. "
        f"Current spend remains ₹{original_total:,.2f}."
    )
    diff = build_contingency_diff(
        trigger_type=CrisisTriggerType.BUDGET_COMPRESSION,
        description=f"Co-Pilot expanded budget ceiling by {percentage:+.1f}%",
        summary_narrative=narrative,
        original_total_inr=original_total,
        new_total_inr=original_total,
        updated_plan=plan,
        actionable_mitigations=[
            "Additional ceiling headroom is available for decor upgrades or premium entertainment."
        ],
        diff_prefix="diff_scale",
    )
    return plan, diff


def _apply_cut_to_items(
    non_critical_items: list[BOQItem], needed_cut: float, total_non_critical: float
) -> tuple[list[BOQDiffItem], float]:
    """Applies cuts proportionally across non-critical BOQ items."""
    boq_diffs: list[BOQDiffItem] = []
    if total_non_critical <= 0:
        return boq_diffs, 0.0

    if needed_cut <= total_non_critical:
        scale_factor = (total_non_critical - needed_cut) / total_non_critical
        shortfall = 0.0
    else:
        scale_factor = 0.0
        shortfall = needed_cut - total_non_critical

    for it in non_critical_items:
        orig_copy = it.model_copy(deep=True)
        old_cost = it.total_cost_inr
        it.estimated_rate_inr = round(it.estimated_rate_inr * scale_factor, 2)
        it.total_cost_inr = round(it.quantity * it.estimated_rate_inr, 2)
        it.mirror_synonyms()
        it.status = "MODIFIED" if it.total_cost_inr > 0 else "DROPPED"
        boq_diffs.append(
            BOQDiffItem(
                item_id=it.item_id,
                action=DiffAction.MODIFIED if it.status == "MODIFIED" else DiffAction.REMOVED,
                original_item=orig_copy,
                updated_item=it,
                reason=f"Co-Pilot scaled '{it.name}' down from ₹{old_cost:,.2f} to ₹{it.total_cost_inr:,.2f}.",
            )
        )
    return boq_diffs, shortfall


def _protect_critical_items(plan: MasterEventPlan, boq_diffs: list[BOQDiffItem]) -> None:
    """Appends UNCHANGED diff records for Tier-1 critical items."""
    for it in plan.boq:
        if it.priority == PriorityTier.CRITICAL:
            boq_diffs.append(
                BOQDiffItem(
                    item_id=it.item_id,
                    action=DiffAction.UNCHANGED,
                    original_item=it.model_copy(deep=True),
                    updated_item=it,
                    reason="Tier-1 Critical item protected: locked at 100% spend.",
                )
            )


def _build_cut_narrative(
    original_limit: float,
    new_limit: float,
    original_total: float,
    new_total: float,
    percentage: float,
    shortfall: float,
) -> tuple[str, list[str]]:
    """Builds the summary narrative and mitigations for budget cut."""
    warnings: list[str] = []
    if shortfall > 0:
        warnings.append(f"Couldn't reach ₹{new_limit:,.2f} without cutting Critical items; short by ₹{shortfall:,.2f}.")

    narrative = (
        f"Budget scaled by {percentage:+.1f}% (ceiling ₹{original_limit:,.2f} → ₹{new_limit:,.2f}). "
        f"Critical safety & food items were locked intact. "
        f"Spend adjusted from ₹{original_total:,.2f} to ₹{new_total:,.2f}."
    )
    if shortfall > 0:
        narrative += f" Note: shortfall of ₹{shortfall:,.2f} remains to protect core Tier-1 deliverables."

    mitigations = [
        "Audit revised vendor rates in the Bill of Quantities",
        "Confirm adjusted delivery specifications with suppliers",
    ]
    if warnings:
        mitigations.extend(warnings)
    return narrative, mitigations


def _scale_budget_cut(
    plan: MasterEventPlan, original_limit: float, original_total: float, factor: float, percentage: float
) -> tuple[MasterEventPlan, ContingencyDiff]:
    """Handles negative budget scaling (cut)."""
    new_limit = round(original_limit * factor, 2)
    plan.total_budget_limit = new_limit

    needed_cut = round(original_total * (-percentage / 100.0), 2)
    non_critical_items = [it for it in plan.boq if it.priority != PriorityTier.CRITICAL and it.status != "DROPPED"]
    total_non_critical = sum(it.total_cost_inr for it in non_critical_items)

    boq_diffs, shortfall = _apply_cut_to_items(non_critical_items, needed_cut, total_non_critical)
    _protect_critical_items(plan, boq_diffs)
    recompute_totals(plan)

    narrative, mitigations = _build_cut_narrative(
        original_limit, new_limit, original_total, plan.current_estimated_total, percentage, shortfall
    )

    diff = build_contingency_diff(
        trigger_type=CrisisTriggerType.BUDGET_COMPRESSION,
        description=f"Co-Pilot scaled budget by {percentage:+.1f}%",
        summary_narrative=narrative,
        original_total_inr=original_total,
        new_total_inr=plan.current_estimated_total,
        updated_plan=plan,
        boq_diffs=boq_diffs,
        actionable_mitigations=mitigations,
        budget_cut_percent=abs(percentage),
        diff_prefix="diff_scale",
    )
    return plan, diff


def execute_scale_budget(plan: MasterEventPlan, percentage: float) -> tuple[MasterEventPlan, ContingencyDiff]:
    """Scales the budget ceiling and line items deterministically."""
    new_plan = plan.model_copy(deep=True)
    original_limit = new_plan.total_budget_limit
    original_total = new_plan.current_estimated_total
    factor = 1.0 + (percentage / 100.0)

    if percentage >= 0:
        return _scale_budget_expansion(new_plan, original_limit, original_total, factor, percentage)
    return _scale_budget_cut(new_plan, original_limit, original_total, factor, percentage)
