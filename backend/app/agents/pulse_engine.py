"""Pulse Engine: Contingency evaluation and crisis management for AuraPulse AI."""

import copy
import uuid
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ..config import settings
from ..core.constants import CRISIS_NARRATIVE_TIMEOUT, EMERGENCY_MARQUEE_COST_INR
from ..integrations.google_maps import fetch_verified_vendors
from ..llm.client import generate
from ..schemas import (
    BOQDiffItem,
    BOQItem,
    ContingencyDiff,
    CrisisTrigger,
    CrisisTriggerType,
    DiffAction,
    MasterEventPlan,
    PriorityTier,
    ScheduleBlock,
    ScheduleDiffItem,
)
from ..services.budget import rebalance_to_ceiling, recompute_totals

try:
    from google import genai
    from google.genai import types

    _GENAI_AVAILABLE = True
except ImportError:
    genai = None  # type: ignore[assignment]
    types = None  # type: ignore[assignment]
    _GENAI_AVAILABLE = False


@dataclass
class CrisisExecutionResult:
    boq_diffs: list[BOQDiffItem] = field(default_factory=list)
    schedule_diffs: list[ScheduleDiffItem] = field(default_factory=list)
    mitigations: list[str] = field(default_factory=list)
    narrative_paragraphs: list[str] = field(default_factory=list)


def shift_time_str(time_str: str, minutes_to_add: int) -> tuple[str, bool]:
    """
    Helper to shift HH:MM time strings by minutes.
    Returns (new_time_str, next_day_flag) without silent midnight wrap-around.
    """
    try:
        parts = time_str.split(":")
        h = int(parts[0])
        m = int(parts[1])
        total_m = h * 60 + m + minutes_to_add
        next_day = total_m >= 24 * 60
        wrapped_m = total_m % (24 * 60)
        return f"{wrapped_m // 60:02d}:{wrapped_m % 60:02d}", next_day
    except (ValueError, IndexError):
        return time_str, False


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


def _find_delayed_start_min(schedule: list[ScheduleBlock]) -> int | None:
    keywords = ("procession", "baraat", "ceremony", "arrival", "dinner", "banquet", "party")
    for block in schedule:
        if any(keyword in block.phase.lower() or keyword in block.activity.lower() for keyword in keywords):
            try:
                parts = block.start_time_iso.split(":")
                return int(parts[0]) * 60 + int(parts[1])
            except (ValueError, IndexError, AttributeError):
                pass
    return None


def _should_shift_block(block: ScheduleBlock, delayed_start_min: int | None) -> bool:
    if delayed_start_min is not None:
        try:
            parts = block.start_time_iso.split(":")
            b_min = int(parts[0]) * 60 + int(parts[1])
            return b_min >= delayed_start_min
        except (ValueError, IndexError, AttributeError):
            return True
    return any(
        kw in block.phase
        for kw in (
            "Procession",
            "Baraat",
            "Ceremony",
            "Dinner",
            "Banquet",
            "Party",
            "Afterparty",
            "Dance",
            "Feast",
        )
    )


def _shift_schedule_blocks(
    schedule: list[ScheduleBlock], delay: int, delayed_start_min: int | None
) -> tuple[list[ScheduleDiffItem], bool]:
    diffs: list[ScheduleDiffItem] = []
    has_midnight = False
    for block in schedule:
        if not _should_shift_block(block, delayed_start_min):
            continue
        orig_block = copy.deepcopy(block)
        new_start, start_next_day = shift_time_str(block.start_time_iso, delay)
        new_end, end_next_day = shift_time_str(block.end_time_iso, delay)
        block.start_time_iso = new_start
        block.end_time_iso = new_end
        if start_next_day or end_next_day:
            has_midnight = True
            if "(+1 day)" not in block.activity:
                block.activity += " (+1 day)"
        diffs.append(
            ScheduleDiffItem(
                block_id=block.block_id,
                action=DiffAction.MODIFIED,
                original_block=orig_block,
                updated_block=block,
                reason=f"Cascaded schedule block by +{delay} min to accommodate procession delay."
                + (" Crosses midnight (+1 day)." if (start_next_day or end_next_day) else ""),
            )
        )
    return diffs, has_midnight


async def _handle_timeline_slippage(
    updated_plan: MasterEventPlan, trigger: CrisisTrigger, original_total: float
) -> tuple[MasterEventPlan, CrisisExecutionResult]:
    res = CrisisExecutionResult()
    delay = trigger.delay_minutes or 60
    res.mitigations.append(f"Ripple-shift schedule by +{delay} minutes with catering freshness lock")
    res.narrative_paragraphs.append(
        f"TIMELINE SLIPPAGE PROTOCOL: Event procession/VIP delayed by {delay} minutes. "
        "Graph dependency solver shifted subsequent schedule blocks starting at or after the delay forward, "
        "while coordinating with catering head to maintain holding temperature."
    )

    delayed_start = _find_delayed_start_min(updated_plan.schedule)
    sched_diffs, has_midnight = _shift_schedule_blocks(updated_plan.schedule, delay, delayed_start)
    res.schedule_diffs.extend(sched_diffs)

    if has_midnight:
        res.mitigations.append("Schedule block crossed midnight: flagged as +1 day event wrap-around.")

    res.mitigations.append("Notified kitchen dispatch to adjust chafing dish firing times to prevent overcooking.")
    res.mitigations.append("Re-export the updated run-of-show via the iCal (.ics) / Google Calendar buttons.")
    return updated_plan, res


def _apply_vendor_replacement(item: BOQItem, top_vendor: dict[str, Any] | None) -> BOQDiffItem:
    orig_item = copy.deepcopy(item)
    if top_vendor:
        vendor_name = top_vendor.get("name") or "Google Maps listed vendor"
        rating = top_vendor.get("rating")
        rating_txt = f"{rating}/5.0" if rating is not None else "rating unavailable"
        item.name = f"{item.name} — replacement: {vendor_name}"
        item.specification = (
            f"Emergency replacement candidate via Google Maps Places API "
            f"({top_vendor.get('address', 'address unavailable')}, Rating: {rating_txt}). Confirm quote before booking."
        )
        reason = f"Substituted cancelled vendor with Google Maps listed candidate: {vendor_name} ({rating_txt})."
    else:
        item.specification = "NEEDS REPLACEMENT: No verified vendor found via Maps. Search manually."
        reason = "Replacement needed: no verified vendor found."

    item.estimated_rate_inr = round(item.estimated_rate_inr * 1.05, 2)
    item.total_cost_inr = round(item.quantity * item.estimated_rate_inr, 2)
    item.mirror_synonyms()
    item.status = "MODIFIED"
    return BOQDiffItem(
        item_id=item.item_id,
        action=DiffAction.MODIFIED,
        original_item=orig_item,
        updated_item=item,
        reason=reason,
    )


async def _lookup_replacement_vendor(category: str, city: str) -> dict[str, Any] | None:
    try:
        result = await fetch_verified_vendors(query=f"{category} contractor", city=city, min_rating=4.0)
        vendor_list = result.get("vendors", []) if isinstance(result, dict) else (result or [])
        return vendor_list[0] if vendor_list else None
    except Exception:  # noqa: BLE001
        return None


def _replace_matching_boq_items(
    boq: list[BOQItem], cat: str, top_vendor: dict[str, Any] | None
) -> tuple[list[BOQDiffItem], bool]:
    diffs: list[BOQDiffItem] = []
    cat_lower = cat.lower()
    matched_any = False
    for item in boq:
        if item.status == "DROPPED":
            continue
        item_cat = item.category.lower()
        if item_cat == cat_lower or cat_lower in item_cat or item_cat in cat_lower:
            matched_any = True
            diffs.append(_apply_vendor_replacement(item, top_vendor))
    return diffs, matched_any


async def _handle_supply_failure(
    updated_plan: MasterEventPlan, trigger: CrisisTrigger, original_total: float
) -> tuple[MasterEventPlan, CrisisExecutionResult]:
    res = CrisisExecutionResult()
    cat = trigger.affected_vendor_category or "Catering"
    res.mitigations.append(f"Automated vendor hot-swap for failed {cat} supplier via Google Maps Places API")
    res.narrative_paragraphs.append(
        f"SUPPLY FAILURE PROTOCOL: Primary vendor in '{cat}' reported abrupt cancellation. "
        "AuraPulse immediately engaged Google Maps Places API to locate verified top-rated replacement vendors in the target locality."
    )

    top_vendor = await _lookup_replacement_vendor(cat, updated_plan.location_city)
    diffs, matched_any = _replace_matching_boq_items(updated_plan.boq, cat, top_vendor)
    res.boq_diffs.extend(diffs)

    if top_vendor:
        phone = top_vendor.get("phone") or top_vendor.get("nationalPhoneNumber") or "N/A"
        res.mitigations.append(
            f"Contact {top_vendor.get('name', 'listed vendor')} (Phone: {phone}) to confirm availability and quote."
        )
    else:
        res.mitigations.append("No verified vendor found via Maps; search manually.")
    if not matched_any:
        res.mitigations.append(f"No BOQ line items matched category '{cat}'; no line items were modified.")

    return updated_plan, res


CRISIS_STRATEGIES: dict[
    CrisisTriggerType,
    Callable[
        [MasterEventPlan, CrisisTrigger, float], Coroutine[Any, Any, tuple[MasterEventPlan, CrisisExecutionResult]]
    ],
] = {
    CrisisTriggerType.WEATHER_RISK: _handle_weather_risk,
    CrisisTriggerType.BUDGET_COMPRESSION: _handle_budget_compression,
    CrisisTriggerType.TIMELINE_SLIPPAGE: _handle_timeline_slippage,
    CrisisTriggerType.SUPPLY_FAILURE: _handle_supply_failure,
}


async def _generate_crisis_narrative(
    plan: MasterEventPlan,
    trigger: CrisisTrigger,
    original_total: float,
    new_total: float,
    ceiling: float,
    boq_diffs_len: int,
    schedule_diffs_len: int,
) -> str | None:
    api_key = settings.GEMINI_API_KEY
    if not (api_key and _GENAI_AVAILABLE):
        return None
    try:
        prompt = f"""
        You are Pulse Dynamic Engine.
        Event: {plan.title} in {plan.location_city}.
        Crisis Trigger: {trigger.trigger_type} - {trigger.description}.
        Original Cost: INR {original_total:,.2f}. New Cost: INR {new_total:,.2f}. Ceiling: INR {ceiling:,.2f}.
        Diff summary: {boq_diffs_len} line item modifications, {schedule_diffs_len} schedule adjustments.
        Briefly (under 100 words) provide a reassuring executive operational summary for the event planner.
        """
        gemini_res = await generate(
            model=settings.GEMINI_FLASH_MODEL,
            contents=[prompt],
            config=None,
            timeout=CRISIS_NARRATIVE_TIMEOUT,
        )
        if hasattr(gemini_res, "text") and gemini_res.text:
            return gemini_res.text.strip()
    except Exception:  # noqa: BLE001
        pass
    return None


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
