"""Budget compression contingency handler for Pulse Engine."""

from ...schemas import CrisisTrigger, MasterEventPlan
from ...services.budget import rebalance_to_ceiling
from .models import CrisisExecutionResult


async def _handle_budget_compression(
    updated_plan: MasterEventPlan, trigger: CrisisTrigger, original_total: float
) -> tuple[MasterEventPlan, CrisisExecutionResult]:
    res = CrisisExecutionResult()
    cut_pct = trigger.budget_cut_percent or 20.0
    target_savings = round(original_total * (cut_pct / 100.0), 2)
    target_limit = round(original_total - target_savings, 2)
    updated_plan.total_budget_limit = target_limit

    updated_plan, shortfall, rebal_diffs = rebalance_to_ceiling(updated_plan, target_limit)
    res.boq_diffs.extend(rebal_diffs)
    saved = round(original_total - updated_plan.current_estimated_total, 2)

    res.mitigations.append(f"Execute {cut_pct:.1f}% budget compression target (INR {target_savings:,.2f})")
    res.mitigations.append(f"Saved INR {saved:,.2f} of INR {target_savings:,.2f} target.")

    if shortfall > 0:
        shortfall_msg = f"Shortfall of INR {shortfall:,.2f} remains: cannot reach target savings without cutting Tier-1 Critical items."
        res.mitigations.append(f"WARNING: {shortfall_msg}")
        res.narrative_paragraphs.append(
            f"BUDGET COMPRESSION PROTOCOL: Client requested a {cut_pct:.1f}% expenditure compression. "
            "Deterministic rule protects all Tier-1 Critical safety, food, and power lines. "
            f"Saved INR {saved:,.2f} of INR {target_savings:,.2f} target. {shortfall_msg}"
        )
    else:
        res.narrative_paragraphs.append(
            f"BUDGET COMPRESSION PROTOCOL: Successfully achieved target savings of INR {saved:,.2f} "
            f"within the INR {target_limit:,.2f} ceiling without compromising Tier-1 guest safety or catering quality."
        )
    return updated_plan, res
