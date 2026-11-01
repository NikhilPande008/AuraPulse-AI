"""Copilot tool definitions and tool execution implementations."""

import logging
import uuid

from backend.app.agents.copilot.diff_builder import build_contingency_diff
from backend.app.schemas.contingency import (
    BOQDiffItem,
    ContingencyDiff,
    CrisisTriggerType,
    DiffAction,
)
from backend.app.schemas.event_plan import (
    BOQItem,
    MasterEventPlan,
    PriorityTier,
)
from backend.app.services.budget import rebalance_to_ceiling, recompute_totals
from backend.app.services.timeline import build_milestones

logger = logging.getLogger("aurapulse.copilot.tools")


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
        it.rate = it.estimated_rate_inr
        it.total_cost_inr = round(it.quantity * it.estimated_rate_inr, 2)
        it.total_cost = it.total_cost_inr
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


def execute_add_item(
    plan: MasterEventPlan,
    category: str,
    name: str,
    specification: str = "Added via Co-Pilot",
    quantity: float = 1.0,
    unit: str = "lot",
    rate_inr: float = 10000.0,
    priority: str = "Operational",
) -> tuple[MasterEventPlan, ContingencyDiff]:
    """Adds a new line item to the BOQ."""
    new_plan = plan.model_copy(deep=True)
    try:
        tier = PriorityTier(priority)
    except ValueError:
        tier = PriorityTier.OPERATIONAL

    total_cost = round(float(quantity) * float(rate_inr), 2)
    new_item = BOQItem(
        item_id=f"boq_add_{uuid.uuid4().hex[:6]}",
        category=category,
        name=name,
        specification=specification or f"Added via Co-Pilot advisory tool call ({name})",
        quantity=float(quantity),
        unit=unit,
        estimated_rate_inr=float(rate_inr),
        total_cost_inr=total_cost,
        rate=float(rate_inr),
        total_cost=total_cost,
        priority=tier,
        priority_tier=tier,
        status="ACTIVE",
    )
    new_plan.boq.append(new_item)
    recompute_totals(new_plan)

    diff = build_contingency_diff(
        trigger_type=CrisisTriggerType.WEATHER_RISK,
        description=f"Co-Pilot added line item: {name}",
        summary_narrative=f"Added '{name}' in category '{category}' at ₹{total_cost:,.2f} ({tier.value} tier).",
        original_total_inr=plan.current_estimated_total,
        new_total_inr=new_plan.current_estimated_total,
        updated_plan=new_plan,
        boq_diffs=[
            BOQDiffItem(
                item_id=new_item.item_id,
                action=DiffAction.ADDED,
                original_item=None,
                updated_item=new_item,
                reason=f"Co-Pilot added '{name}' ({unit}) at ₹{rate_inr:,.2f}/unit.",
            )
        ],
        actionable_mitigations=[f"Verify supplier availability for {name}"],
        diff_prefix="diff_add",
    )
    return new_plan, diff


def _find_boq_item(plan: MasterEventPlan, item_id: str) -> BOQItem | None:
    """Finds an item by item_id or name."""
    query = item_id.lower()
    for it in plan.boq:
        if it.item_id == item_id or it.name.lower() == query or query in it.name.lower():
            return it
    return None


def execute_remove_item(plan: MasterEventPlan, item_id: str) -> tuple[MasterEventPlan, ContingencyDiff]:
    """Removes a line item by ID or name."""
    new_plan = plan.model_copy(deep=True)
    target_item = _find_boq_item(new_plan, item_id)

    if not target_item or target_item.status == "DROPPED":
        diff = build_contingency_diff(
            trigger_type=CrisisTriggerType.BUDGET_COMPRESSION,
            description=f"Removal attempted for {item_id}",
            summary_narrative=f"Item '{item_id}' was not found or already dropped.",
            original_total_inr=plan.current_estimated_total,
            new_total_inr=plan.current_estimated_total,
            updated_plan=new_plan,
            diff_prefix="diff_rm",
        )
        return new_plan, diff

    orig_copy = target_item.model_copy(deep=True)
    released_cost = target_item.total_cost_inr
    target_item.status = "DROPPED"
    target_item.total_cost_inr = 0.0
    target_item.total_cost = 0.0
    recompute_totals(new_plan)

    diff = build_contingency_diff(
        trigger_type=CrisisTriggerType.BUDGET_COMPRESSION,
        description=f"Removed line item {orig_copy.name}",
        summary_narrative=f"Removed '{orig_copy.name}' from BOQ, releasing ₹{released_cost:,.2f}.",
        original_total_inr=plan.current_estimated_total,
        new_total_inr=new_plan.current_estimated_total,
        updated_plan=new_plan,
        boq_diffs=[
            BOQDiffItem(
                item_id=target_item.item_id,
                action=DiffAction.REMOVED,
                original_item=orig_copy,
                updated_item=target_item,
                reason=f"Co-Pilot removed '{orig_copy.name}', saving ₹{released_cost:,.2f}.",
            )
        ],
        actionable_mitigations=[f"Cancelled procurement for {orig_copy.name}"],
        diff_prefix="diff_rm",
    )
    return new_plan, diff


def execute_update_item(
    plan: MasterEventPlan,
    item_id: str,
    quantity: float | None = None,
    rate_inr: float | None = None,
    name: str | None = None,
) -> tuple[MasterEventPlan, ContingencyDiff]:
    """Updates quantity, rate, or name of an existing item."""
    new_plan = plan.model_copy(deep=True)
    target_item = _find_boq_item(new_plan, item_id)

    if not target_item or target_item.status == "DROPPED":
        diff = build_contingency_diff(
            trigger_type=CrisisTriggerType.BUDGET_COMPRESSION,
            description="Update attempted",
            summary_narrative=f"Item '{item_id}' not found.",
            original_total_inr=plan.current_estimated_total,
            new_total_inr=plan.current_estimated_total,
            updated_plan=new_plan,
            diff_prefix="diff_upd",
        )
        return new_plan, diff

    orig_copy = target_item.model_copy(deep=True)
    if name is not None:
        target_item.name = name
    if quantity is not None and quantity > 0:
        target_item.quantity = float(quantity)
    if rate_inr is not None and rate_inr >= 0:
        target_item.estimated_rate_inr = float(rate_inr)
        target_item.rate = float(rate_inr)

    target_item.total_cost_inr = round(target_item.quantity * target_item.estimated_rate_inr, 2)
    target_item.total_cost = target_item.total_cost_inr
    target_item.status = "MODIFIED"
    recompute_totals(new_plan)

    diff = build_contingency_diff(
        trigger_type=CrisisTriggerType.BUDGET_COMPRESSION,
        description=f"Updated item {target_item.name}",
        summary_narrative=f"Updated '{target_item.name}' specifications in the Bill of Quantities.",
        original_total_inr=plan.current_estimated_total,
        new_total_inr=new_plan.current_estimated_total,
        updated_plan=new_plan,
        boq_diffs=[
            BOQDiffItem(
                item_id=target_item.item_id,
                action=DiffAction.MODIFIED,
                original_item=orig_copy,
                updated_item=target_item,
                reason=f"Updated {target_item.name} quantity/rate.",
            )
        ],
        diff_prefix="diff_upd",
    )
    return new_plan, diff


def execute_set_event_date(plan: MasterEventPlan, new_date: str) -> MasterEventPlan:
    """Sets a new target event date and updates milestones backwards."""
    new_plan = plan.model_copy(deep=True)
    new_plan.event_date = new_date
    new_plan.planning_milestones = build_milestones(
        event_date=new_date,
        event_type=new_plan.event_type,
        culture_region=new_plan.culture_region,
    )
    return new_plan


def _scale_headcount_boq_items(plan: MasterEventPlan, ratio: float, new_headcount: int) -> list[BOQDiffItem]:
    """Scales guest-sensitive BOQ line items proportionally."""
    guest_units = ("pax", "plate", "guest", "person", "attendee", "head")
    boq_diffs: list[BOQDiffItem] = []
    for item in plan.boq:
        if item.status == "DROPPED":
            continue
        unit_lower = item.unit.lower()
        if any(h in unit_lower for h in guest_units):
            orig_copy = item.model_copy(deep=True)
            old_qty = item.quantity
            item.quantity = round(item.quantity * ratio, 2)
            item.total_cost_inr = round(item.quantity * item.estimated_rate_inr, 2)
            item.total_cost = item.total_cost_inr
            item.status = "MODIFIED"
            boq_diffs.append(
                BOQDiffItem(
                    item_id=item.item_id,
                    action=DiffAction.MODIFIED,
                    original_item=orig_copy,
                    updated_item=item,
                    reason=(
                        f"Scaled quantity from {old_qty} to {item.quantity} {item.unit} "
                        f"to match new headcount ({new_headcount} guests)."
                    ),
                )
            )
    return boq_diffs


def execute_set_headcount(plan: MasterEventPlan, new_headcount: int) -> tuple[MasterEventPlan, ContingencyDiff]:
    """Updates headcount (1..10000) and proportionally scales guest items."""
    if new_headcount < 1 or new_headcount > 10000:
        raise ValueError(f"Headcount must be between 1 and 10000 (received {new_headcount})")

    new_plan = plan.model_copy(deep=True)
    old_headcount = getattr(new_plan, "headcount", None) or 100
    if old_headcount <= 0:
        old_headcount = 100
    ratio = float(new_headcount) / float(old_headcount)
    new_plan.headcount = new_headcount

    boq_diffs = _scale_headcount_boq_items(new_plan, ratio, new_headcount)
    recompute_totals(new_plan)

    shortfall_note = ""
    if new_plan.current_estimated_total > new_plan.total_budget_limit:
        new_plan, shortfall, _drops = rebalance_to_ceiling(new_plan, new_plan.total_budget_limit)
        if shortfall > 0:
            shortfall_note = f" Note: Spending ceiling exceeded by ₹{shortfall:,.2f}; non-critical lines adjusted."

    narrative = (
        f"Updated headcount from {old_headcount} to {new_headcount} guests. "
        f"Per-person catering and guest items scaled proportionally.{shortfall_note}"
    )
    diff = build_contingency_diff(
        trigger_type=CrisisTriggerType.BUDGET_COMPRESSION,
        description=f"Headcount changed to {new_headcount}",
        summary_narrative=narrative,
        original_total_inr=plan.current_estimated_total,
        new_total_inr=new_plan.current_estimated_total,
        updated_plan=new_plan,
        boq_diffs=boq_diffs,
        actionable_mitigations=[f"Update venue banquet manager for {new_headcount} headcount lock"],
        diff_prefix="diff_hc",
    )
    return new_plan, diff


def execute_change_headcount(plan: MasterEventPlan, delta: int) -> tuple[MasterEventPlan, ContingencyDiff]:
    """Relative headcount update."""
    old_headcount = getattr(plan, "headcount", None) or 100
    return execute_set_headcount(plan, old_headcount + delta)


def execute_decline_off_topic(reason: str) -> str:
    """Tool: decline_off_topic."""
    return f"I specialize exclusively in event planning, budgeting, scheduling, and vendor logistics. {reason}"


# Declarations for Gemini function calling
def scale_budget(percentage: float) -> str:
    """Scales budget ceiling and line items by percentage (-90 to +100)."""
    return f"scale_budget({percentage})"


def add_item(category: str, name: str, quantity: float, unit: str, rate_inr: float, priority: str) -> str:
    """Adds a new line item to the Bill of Quantities."""
    return f"add_item({name})"


def remove_item(item_id: str) -> str:
    """Removes a line item by item_id or name from the Bill of Quantities."""
    return f"remove_item({item_id})"


def update_item(
    item_id: str, quantity: float | None = None, rate_inr: float | None = None, name: str | None = None
) -> str:
    """Updates specifications, quantity, or unit rate of an existing BOQ item."""
    return f"update_item({item_id})"


def set_event_date(new_date: str) -> str:
    """Sets a new target event date (YYYY-MM-DD) and dynamically recalculates backwards milestones."""
    return f"set_event_date({new_date})"


def set_headcount(new_total: int) -> str:
    """Updates headcount (1 to 10000) to an absolute total and scales per-guest line items proportionally."""
    return f"set_headcount({new_total})"


def change_headcount(delta: int) -> str:
    """Changes headcount by a relative delta (positive or negative)."""
    return f"change_headcount({delta})"


def decline_off_topic(reason: str) -> str:
    """Declines an off-topic query unrelated to event planning or budgeting."""
    return f"decline_off_topic({reason})"


COPILOT_TOOLS = [
    scale_budget,
    add_item,
    remove_item,
    update_item,
    set_event_date,
    set_headcount,
    change_headcount,
    decline_off_topic,
]
