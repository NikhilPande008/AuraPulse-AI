"""Weather risk contingency handler for Pulse Engine."""

import copy

from ...core.constants import EMERGENCY_MARQUEE_COST_INR
from ...schemas import (
    BOQDiffItem,
    BOQItem,
    CrisisTrigger,
    DiffAction,
    MasterEventPlan,
    PriorityTier,
    ScheduleBlock,
    ScheduleDiffItem,
)
from ...services.budget import rebalance_to_ceiling, recompute_totals
from .models import CrisisExecutionResult


def _build_emergency_canopy() -> BOQItem:
    return BOQItem(
        item_id="boq_emerg_canopy",
        category="Infrastructure & Weatherproofing",
        name="Emergency German Pagoda Marquee & Waterproof Flooring",
        specification="Clear-span heavy vinyl all-weather pagoda with anti-skid raised wooden subfloor",
        quantity=1.0,
        unit="lot",
        estimated_rate_inr=EMERGENCY_MARQUEE_COST_INR,
        total_cost_inr=EMERGENCY_MARQUEE_COST_INR,
        priority=PriorityTier.CRITICAL,
        priority_tier=PriorityTier.CRITICAL,
        status="ACTIVE",
    )


def _reroute_outdoor_blocks(schedule: list[ScheduleBlock]) -> list[ScheduleDiffItem]:
    diffs: list[ScheduleDiffItem] = []
    for block in schedule:
        if block.is_outdoor:
            orig_block = copy.deepcopy(block)
            block.is_outdoor = False
            block.activity += " (Re-routed to Pagoda Canopy Zone)"
            block.responsible_party += " + Weather Marshal"
            diffs.append(
                ScheduleDiffItem(
                    block_id=block.block_id,
                    action=DiffAction.MODIFIED,
                    original_block=orig_block,
                    updated_block=block,
                    reason="Shifted outdoor activity into protected all-weather covered zone.",
                )
            )
    return diffs


async def _handle_weather_risk(
    updated_plan: MasterEventPlan, trigger: CrisisTrigger, original_total: float
) -> tuple[MasterEventPlan, CrisisExecutionResult]:
    res = CrisisExecutionResult()
    condition = trigger.weather_condition or "Severe Rainstorm & High Wind"
    res.mitigations.append(f"Deploy weather contingency protocol for {condition}")

    canopy_item = _build_emergency_canopy()
    updated_plan.boq.append(canopy_item)
    recompute_totals(updated_plan)
    res.boq_diffs.append(
        BOQDiffItem(
            item_id=canopy_item.item_id,
            action=DiffAction.ADDED,
            original_item=None,
            updated_item=canopy_item,
            reason="Added emergency weatherproofing marquee (INR 185,000) to protect guests and sensitive electronics.",
        )
    )

    updated_plan, shortfall, rebal_diffs = rebalance_to_ceiling(updated_plan, updated_plan.total_budget_limit)
    res.boq_diffs.extend(rebal_diffs)

    if shortfall > 0:
        res.narrative_paragraphs.append(
            f"WEATHER PROTOCOL ACTIVATED: High probability of {condition} detected. "
            "German Pagoda Marquee (INR 185,000) injected into the BOQ. "
            f"Total spend exceeds ceiling by INR {shortfall:,.2f} because Tier-1 Critical core lines cannot be reduced: "
            "approve the extra spend or cut further."
        )
        res.mitigations.append(
            f"WARNING: Budget ceiling exceeded by INR {shortfall:,.2f} even after trimming Discretionary and Operational tiers. "
            "Approve additional funds or reduce scope manually."
        )
    else:
        res.narrative_paragraphs.append(
            f"WEATHER PROTOCOL ACTIVATED: High probability of {condition} detected. "
            "German Pagoda Marquee injected into the BOQ. "
            f"Discretionary and Operational items were rebalanced, staying within the INR {updated_plan.total_budget_limit:,.2f} ceiling."
        )
        res.mitigations.append(
            f"Weather marquee funded within the INR {updated_plan.total_budget_limit:,.2f} budget ceiling."
        )

    res.schedule_diffs.extend(_reroute_outdoor_blocks(updated_plan.schedule))
    res.mitigations.append("Ground-supported electrical GFCI disconnects installed at all wet perimeter points.")
    res.mitigations.append(
        "Shortlist marquee rental vendors (use Vendor Finder) and confirm mobilization time before committing."
    )
    return updated_plan, res
