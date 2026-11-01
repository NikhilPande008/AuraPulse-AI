"""Budget calculation and contingency rebalancing service for AuraPulse AI."""

import copy

from ..core.constants import OPERATIONAL_FLOOR
from ..schemas import (
    BOQDiffItem,
    BOQItem,
    DiffAction,
    MasterEventPlan,
    PriorityTier,
)


def recompute_totals(plan: MasterEventPlan) -> MasterEventPlan:
    """Deterministically recalculates line item totals and master plan spend.

    Args:
        plan: The MasterEventPlan to recalculate.

    Returns:
        The updated MasterEventPlan with recomputed totals.
    """
    total = 0.0
    for item in plan.boq:
        if item.status == "DROPPED":
            item.total_cost_inr = 0.0
        else:
            item.total_cost_inr = round(float(item.quantity) * float(item.estimated_rate_inr), 2)
            total += item.total_cost_inr
        item.mirror_synonyms()

    plan.current_estimated_total = round(total, 2)
    return plan


def _drop_all_discretionary(
    disc_items: list[BOQItem],
) -> tuple[float, list[BOQDiffItem]]:
    diffs: list[BOQDiffItem] = []
    accumulated_savings = 0.0
    for item in disc_items:
        orig_item = copy.deepcopy(item)
        item.status = "DROPPED"
        accumulated_savings += item.total_cost_inr
        item.total_cost_inr = 0.0
        item.estimated_rate_inr = 0.0
        item.mirror_synonyms()
        diffs.append(
            BOQDiffItem(
                item_id=item.item_id,
                action=DiffAction.REMOVED,
                original_item=orig_item,
                updated_item=item,
                reason=f"Dropped discretionary line item '{item.name}' to absorb budget cut.",
            )
        )
    return accumulated_savings, diffs


def _scale_discretionary(
    disc_items: list[BOQItem], total_disc: float, needed_savings: float
) -> tuple[float, list[BOQDiffItem]]:
    diffs: list[BOQDiffItem] = []
    accumulated_savings = 0.0
    disc_factor = max(0.0, (total_disc - needed_savings) / total_disc)
    for item in disc_items:
        orig_item = copy.deepcopy(item)
        old_cost = item.total_cost_inr
        item.estimated_rate_inr = round(item.estimated_rate_inr * disc_factor, 2)
        item.total_cost_inr = round(item.quantity * item.estimated_rate_inr, 2)
        item.status = "MODIFIED" if item.total_cost_inr > 0 else "DROPPED"
        item.mirror_synonyms()
        accumulated_savings += old_cost - item.total_cost_inr
        diffs.append(
            BOQDiffItem(
                item_id=item.item_id,
                action=DiffAction.MODIFIED if item.status == "MODIFIED" else DiffAction.REMOVED,
                original_item=orig_item,
                updated_item=item,
                reason=f"Trimmed discretionary line item '{item.name}' from ₹{old_cost:,.2f} to ₹{item.total_cost_inr:,.2f}.",
            )
        )
    return accumulated_savings, diffs


def _trim_discretionary(plan: MasterEventPlan, needed_savings: float) -> tuple[float, list[BOQDiffItem]]:
    disc_items = [it for it in plan.boq if it.priority == PriorityTier.DISCRETIONARY and it.status != "DROPPED"]
    total_disc = sum(it.total_cost_inr for it in disc_items)
    if total_disc <= 0:
        return 0.0, []
    if total_disc <= needed_savings:
        return _drop_all_discretionary(disc_items)
    return _scale_discretionary(disc_items, total_disc, needed_savings)


def _trim_operational(plan: MasterEventPlan, needed_savings: float) -> tuple[float, list[BOQDiffItem]]:
    op_items = [it for it in plan.boq if it.priority == PriorityTier.OPERATIONAL and it.status != "DROPPED"]
    max_op_reduction = sum(it.total_cost_inr * (1.0 - OPERATIONAL_FLOOR) for it in op_items)
    if max_op_reduction <= 0:
        return 0.0, []

    reduction_ratio = min(1.0, needed_savings / max_op_reduction)
    cut_factor = 1.0 - ((1.0 - OPERATIONAL_FLOOR) * reduction_ratio)
    diffs: list[BOQDiffItem] = []
    accumulated_savings = 0.0

    for item in op_items:
        orig_item = copy.deepcopy(item)
        old_cost = item.total_cost_inr
        item.estimated_rate_inr = round(item.estimated_rate_inr * cut_factor, 2)
        item.total_cost_inr = round(item.quantity * item.estimated_rate_inr, 2)
        item.status = "MODIFIED"
        item.mirror_synonyms()
        accumulated_savings += old_cost - item.total_cost_inr
        diffs.append(
            BOQDiffItem(
                item_id=item.item_id,
                action=DiffAction.MODIFIED,
                original_item=orig_item,
                updated_item=item,
                reason=f"Optimized operational rate for '{item.name}' from ₹{old_cost:,.2f} to ₹{item.total_cost_inr:,.2f} (locked 50% floor).",
            )
        )
    return accumulated_savings, diffs


def rebalance_to_ceiling(plan: MasterEventPlan, ceiling: float) -> tuple[MasterEventPlan, float, list[BOQDiffItem]]:
    """Rebalances plan spend down to ceiling.

    Trims Tier-3 Discretionary items first (down to 0 / DROPPED).
    If still short, trims Tier-2 Operational items proportionally down to a 50% floor.
    Never touches Tier-1 Critical safety/food lines.

    Args:
        plan: The MasterEventPlan to balance.
        ceiling: The target maximum budget ceiling in INR.

    Returns:
        A tuple of (updated_plan, shortfall, boq_diffs), where shortfall is 0.0 if achieved.
    """
    new_plan = plan.model_copy(deep=True)
    recompute_totals(new_plan)
    boq_diffs: list[BOQDiffItem] = []

    if new_plan.current_estimated_total <= ceiling:
        return new_plan, 0.0, boq_diffs

    needed_savings = round(new_plan.current_estimated_total - ceiling, 2)
    _, disc_diffs = _trim_discretionary(new_plan, needed_savings)
    boq_diffs.extend(disc_diffs)
    recompute_totals(new_plan)

    if new_plan.current_estimated_total > ceiling:
        still_needed = round(new_plan.current_estimated_total - ceiling, 2)
        _, op_diffs = _trim_operational(new_plan, still_needed)
        boq_diffs.extend(op_diffs)
        recompute_totals(new_plan)

    shortfall = max(0.0, round(new_plan.current_estimated_total - ceiling, 2))
    return new_plan, shortfall, boq_diffs
