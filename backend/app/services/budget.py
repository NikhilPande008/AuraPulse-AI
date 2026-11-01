import copy
from typing import List, Tuple

from ..schemas import (
    BOQDiffItem,
    DiffAction,
    MasterEventPlan,
    PriorityTier,
)


def recompute_totals(plan: MasterEventPlan) -> MasterEventPlan:
    """
    Deterministically calculates line totals (quantity * rate) and master plan spend.
    Ensures synonym fields (rate, total_cost) stay in sync and DROPPED items contribute ₹0.
    """
    total = 0.0
    for item in plan.boq:
        if item.status == "DROPPED":
            item.total_cost_inr = 0.0
            item.total_cost = 0.0
        else:
            item.total_cost_inr = round(float(item.quantity) * float(item.estimated_rate_inr), 2)
            item.total_cost = item.total_cost_inr
            total += item.total_cost_inr
        item.rate = item.estimated_rate_inr
        item.priority_tier = item.priority

    plan.current_estimated_total = round(total, 2)
    return plan


def rebalance_to_ceiling(
    plan: MasterEventPlan,
    ceiling: float
) -> Tuple[MasterEventPlan, float, List[BOQDiffItem]]:
    """
    Rebalances plan spend down to ceiling:
    1. Trims Tier-3 Discretionary items first (down to 0 / DROPPED).
    2. If still short, trims Tier-2 Operational items proportionally down to a 50% floor.
    3. Never touches Tier-1 Critical safety/food lines.
    4. Computes shortfall = new_total - ceiling (0.0 if achieved).
    Returns (updated_plan, shortfall, boq_diffs).
    """
    new_plan = plan.model_copy(deep=True)
    recompute_totals(new_plan)
    boq_diffs: List[BOQDiffItem] = []

    if new_plan.current_estimated_total <= ceiling:
        return new_plan, 0.0, boq_diffs

    needed_savings = round(new_plan.current_estimated_total - ceiling, 2)
    accumulated_savings = 0.0

    # Phase 1: Discretionary Items (can be trimmed up to 100% or dropped)
    disc_items = [it for it in new_plan.boq if it.priority == PriorityTier.DISCRETIONARY and it.status != "DROPPED"]
    total_disc = sum(it.total_cost_inr for it in disc_items)

    if total_disc > 0:
        if total_disc <= needed_savings:
            # Drop all discretionary items
            for item in disc_items:
                orig_item = copy.deepcopy(item)
                item.status = "DROPPED"
                accumulated_savings += item.total_cost_inr
                item.total_cost_inr = 0.0
                item.total_cost = 0.0
                item.estimated_rate_inr = 0.0
                item.rate = 0.0
                boq_diffs.append(
                    BOQDiffItem(
                        item_id=item.item_id,
                        action=DiffAction.REMOVED,
                        original_item=orig_item,
                        updated_item=item,
                        reason=f"Dropped discretionary line item '{item.name}' to absorb budget cut."
                    )
                )
        else:
            # Scale discretionary items proportionally
            disc_factor = max(0.0, (total_disc - needed_savings) / total_disc)
            for item in disc_items:
                orig_item = copy.deepcopy(item)
                old_cost = item.total_cost_inr
                item.estimated_rate_inr = round(item.estimated_rate_inr * disc_factor, 2)
                item.rate = item.estimated_rate_inr
                item.total_cost_inr = round(item.quantity * item.estimated_rate_inr, 2)
                item.total_cost = item.total_cost_inr
                item.status = "MODIFIED" if item.total_cost_inr > 0 else "DROPPED"
                accumulated_savings += (old_cost - item.total_cost_inr)
                boq_diffs.append(
                    BOQDiffItem(
                        item_id=item.item_id,
                        action=DiffAction.MODIFIED if item.status == "MODIFIED" else DiffAction.REMOVED,
                        original_item=orig_item,
                        updated_item=item,
                        reason=f"Trimmed discretionary line item '{item.name}' from ₹{old_cost:,.2f} to ₹{item.total_cost_inr:,.2f}."
                    )
                )

    recompute_totals(new_plan)

    # Phase 2: Operational Items (trim up to 50% max floor if more savings needed)
    if new_plan.current_estimated_total > ceiling:
        still_needed = round(new_plan.current_estimated_total - ceiling, 2)
        op_items = [it for it in new_plan.boq if it.priority == PriorityTier.OPERATIONAL and it.status != "DROPPED"]
        max_op_reduction = sum(it.total_cost_inr * 0.50 for it in op_items)

        if max_op_reduction > 0:
            reduction_ratio = min(1.0, still_needed / max_op_reduction)
            for item in op_items:
                orig_item = copy.deepcopy(item)
                old_cost = item.total_cost_inr
                cut_factor = 1.0 - (0.50 * reduction_ratio)
                item.estimated_rate_inr = round(item.estimated_rate_inr * cut_factor, 2)
                item.rate = item.estimated_rate_inr
                item.total_cost_inr = round(item.quantity * item.estimated_rate_inr, 2)
                item.total_cost = item.total_cost_inr
                item.status = "MODIFIED"
                boq_diffs.append(
                    BOQDiffItem(
                        item_id=item.item_id,
                        action=DiffAction.MODIFIED,
                        original_item=orig_item,
                        updated_item=item,
                        reason=f"Optimized operational rate for '{item.name}' from ₹{old_cost:,.2f} to ₹{item.total_cost_inr:,.2f} (locked 50% floor)."
                    )
                )

    recompute_totals(new_plan)

    shortfall = max(0.0, round(new_plan.current_estimated_total - ceiling, 2))
    return new_plan, shortfall, boq_diffs
