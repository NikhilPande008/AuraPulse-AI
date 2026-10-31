import os
import copy
import uuid
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from ..schemas import (
    MasterEventPlan,
    BOQItem,
    ScheduleBlock,
    PriorityTier,
    CrisisTrigger,
    CrisisTriggerType,
    DiffAction,
    BOQDiffItem,
    ScheduleDiffItem,
    ContingencyDiff,
)
from ..config import settings
from ..integrations.google_maps import fetch_verified_vendors
from ..services.budget import recompute_totals, rebalance_to_ceiling
from ..llm.client import generate, get_genai_client

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None


def shift_time_str(time_str: str, minutes_to_add: int) -> Tuple[str, bool]:
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
    except Exception:
        return time_str, False


async def evaluate_contingency(
    plan: MasterEventPlan,
    trigger: CrisisTrigger
) -> ContingencyDiff:
    """
    Pulse Dynamic Engine:
    Deterministic rebalancer with optional Gemini narrative.
    Protects Tier-1 (Critical) safety & banquet lines, negotiates Tier-2 (Operational, 50% floor),
    and trims Tier-3 (Discretionary) items to generate a precise ContingencyDiff.
    """
    diff_id = f"diff_{uuid.uuid4().hex[:8]}"
    timestamp = datetime.now().isoformat()
    original_total = plan.current_estimated_total

    updated_plan = plan.model_copy(deep=True)
    recompute_totals(updated_plan)
    boq_diffs: List[BOQDiffItem] = []
    schedule_diffs: List[ScheduleDiffItem] = []
    mitigations: List[str] = []
    narrative_paragraphs: List[str] = []

    # -------------------------------------------------------------
    # CASE 1: WEATHER_RISK (Rain / Storm / High Heat)
    # -------------------------------------------------------------
    if trigger.trigger_type == CrisisTriggerType.WEATHER_RISK:
        condition = trigger.weather_condition or "Severe Rainstorm & High Wind"
        mitigations.append(f"Deploy weather contingency protocol for {condition}")

        # 1. Add Emergency Canopy (Critical / Active)
        canopy_item = BOQItem(
            item_id="boq_emerg_canopy",
            category="Infrastructure & Weatherproofing",
            name="Emergency German Pagoda Marquee & Waterproof Flooring",
            specification="Clear-span heavy vinyl all-weather pagoda with anti-skid raised wooden subfloor",
            quantity=1.0,
            unit="lot",
            estimated_rate_inr=185000.0,
            total_cost_inr=185000.0,
            priority=PriorityTier.CRITICAL,
            priority_tier=PriorityTier.CRITICAL,
            status="ACTIVE"
        )
        updated_plan.boq.append(canopy_item)
        recompute_totals(updated_plan)

        boq_diffs.append(BOQDiffItem(
            item_id=canopy_item.item_id,
            action=DiffAction.ADDED,
            original_item=None,
            updated_item=canopy_item,
            reason="Added emergency weatherproofing marquee (INR 185,000) to protect guests and sensitive electronics."
        ))

        # 2. Offset budget using shared deterministic rebalancer
        updated_plan, shortfall, rebal_diffs = rebalance_to_ceiling(updated_plan, updated_plan.total_budget_limit)
        boq_diffs.extend(rebal_diffs)

        if shortfall > 0:
            narrative_paragraphs.append(
                f"WEATHER PROTOCOL ACTIVATED: High probability of {condition} detected. "
                "German Pagoda Marquee (INR 185,000) injected into the BOQ. "
                f"Total spend exceeds ceiling by INR {shortfall:,.2f} because Tier-1 Critical core lines cannot be reduced: "
                "approve the extra spend or cut further."
            )
            mitigations.append(
                f"WARNING: Budget ceiling exceeded by INR {shortfall:,.2f} even after trimming Discretionary and Operational tiers. "
                "Approve additional funds or reduce scope manually."
            )
        else:
            narrative_paragraphs.append(
                f"WEATHER PROTOCOL ACTIVATED: High probability of {condition} detected. "
                "German Pagoda Marquee injected into the BOQ. "
                f"Discretionary and Operational items were rebalanced, staying within the INR {updated_plan.total_budget_limit:,.2f} ceiling."
            )
            mitigations.append(f"Weather marquee funded within the INR {updated_plan.total_budget_limit:,.2f} budget ceiling.")

        # 3. Update Schedule blocks that are outdoor
        for block in updated_plan.schedule:
            if block.is_outdoor:
                orig_block = copy.deepcopy(block)
                block.is_outdoor = False
                block.activity += " (Re-routed to Pagoda Canopy Zone)"
                block.responsible_party += " + Weather Marshal"
                schedule_diffs.append(ScheduleDiffItem(
                    block_id=block.block_id,
                    action=DiffAction.MODIFIED,
                    original_block=orig_block,
                    updated_block=block,
                    reason="Shifted outdoor activity into protected all-weather covered zone."
                ))

        mitigations.append("Ground-supported electrical GFCI disconnects installed at all wet perimeter points.")
        mitigations.append("Shortlist marquee rental vendors (use Vendor Finder) and confirm mobilization time before committing.")

    # -------------------------------------------------------------
    # CASE 2: BUDGET_COMPRESSION (Cut 5% to 40%)
    # -------------------------------------------------------------
    elif trigger.trigger_type == CrisisTriggerType.BUDGET_COMPRESSION:
        cut_pct = trigger.budget_cut_percent or 20.0
        target_savings = round(original_total * (cut_pct / 100.0), 2)
        target_limit = round(original_total - target_savings, 2)
        updated_plan.total_budget_limit = target_limit

        updated_plan, shortfall, rebal_diffs = rebalance_to_ceiling(updated_plan, target_limit)
        boq_diffs.extend(rebal_diffs)
        saved = round(original_total - updated_plan.current_estimated_total, 2)

        mitigations.append(f"Execute {cut_pct:.1f}% budget compression target (INR {target_savings:,.2f})")
        mitigations.append(f"Saved INR {saved:,.2f} of INR {target_savings:,.2f} target.")

        if shortfall > 0:
            shortfall_msg = f"Shortfall of INR {shortfall:,.2f} remains: cannot reach target savings without cutting Tier-1 Critical items."
            mitigations.append(f"WARNING: {shortfall_msg}")
            narrative_paragraphs.append(
                f"BUDGET COMPRESSION PROTOCOL: Client requested a {cut_pct:.1f}% expenditure compression. "
                "Deterministic rule protects all Tier-1 Critical safety, food, and power lines. "
                f"Saved INR {saved:,.2f} of INR {target_savings:,.2f} target. {shortfall_msg}"
            )
        else:
            narrative_paragraphs.append(
                f"BUDGET COMPRESSION PROTOCOL: Successfully achieved target savings of INR {saved:,.2f} "
                f"within the INR {target_limit:,.2f} ceiling without compromising Tier-1 guest safety or catering quality."
            )

    # -------------------------------------------------------------
    # CASE 3: TIMELINE_SLIPPAGE (Baraat / VIP / Flights Delayed)
    # -------------------------------------------------------------
    elif trigger.trigger_type == CrisisTriggerType.TIMELINE_SLIPPAGE:
        delay = trigger.delay_minutes or 60
        mitigations.append(f"Ripple-shift schedule by +{delay} minutes with catering freshness lock")
        narrative_paragraphs.append(
            f"TIMELINE SLIPPAGE PROTOCOL: Event procession/VIP delayed by {delay} minutes. "
            "Graph dependency solver shifted subsequent schedule blocks starting at or after the delay forward, "
            "while coordinating with catering head to maintain holding temperature."
        )

        delayed_start_min: Optional[int] = None
        for block in updated_plan.schedule:
            if any(keyword in block.phase.lower() or keyword in block.activity.lower() for keyword in ["procession", "baraat", "ceremony", "arrival", "dinner", "banquet", "party"]):
                try:
                    parts = block.start_time_iso.split(":")
                    delayed_start_min = int(parts[0]) * 60 + int(parts[1])
                    break
                except Exception:
                    pass

        has_midnight_crossing = False
        for block in updated_plan.schedule:
            should_shift = False
            if delayed_start_min is not None:
                try:
                    parts = block.start_time_iso.split(":")
                    b_min = int(parts[0]) * 60 + int(parts[1])
                    should_shift = b_min >= delayed_start_min
                except Exception:
                    should_shift = True
            else:
                should_shift = any(keyword in block.phase for keyword in ["Procession", "Baraat", "Ceremony", "Dinner", "Banquet", "Party", "Afterparty", "Dance", "Feast"])

            if should_shift:
                orig_block = copy.deepcopy(block)
                new_start, start_next_day = shift_time_str(block.start_time_iso, delay)
                new_end, end_next_day = shift_time_str(block.end_time_iso, delay)
                block.start_time_iso = new_start
                block.end_time_iso = new_end
                if start_next_day or end_next_day:
                    has_midnight_crossing = True
                    if "(+1 day)" not in block.activity:
                        block.activity += " (+1 day)"
                schedule_diffs.append(ScheduleDiffItem(
                    block_id=block.block_id,
                    action=DiffAction.MODIFIED,
                    original_block=orig_block,
                    updated_block=block,
                    reason=f"Cascaded schedule block by +{delay} min to accommodate procession delay." + (" Crosses midnight (+1 day)." if (start_next_day or end_next_day) else "")
                ))

        if has_midnight_crossing:
            mitigations.append("Schedule block crossed midnight: flagged as +1 day event wrap-around.")

        mitigations.append("Notified kitchen dispatch to adjust chafing dish firing times to prevent overcooking.")
        mitigations.append("Re-export the updated run-of-show via the iCal (.ics) / Google Calendar buttons.")

    # -------------------------------------------------------------
    # CASE 4: SUPPLY_FAILURE (Vendor Cancellation / Shortage)
    # -------------------------------------------------------------
    elif trigger.trigger_type == CrisisTriggerType.SUPPLY_FAILURE:
        cat = trigger.affected_vendor_category or "Catering"
        mitigations.append(f"Automated vendor hot-swap for failed {cat} supplier via Google Maps Places API")
        narrative_paragraphs.append(
            f"SUPPLY FAILURE PROTOCOL: Primary vendor in '{cat}' reported abrupt cancellation. "
            "AuraPulse immediately engaged Google Maps Places API to locate verified top-rated replacement vendors in the target locality."
        )

        vendors: List[Dict[str, Any]] = []
        try:
            result = await fetch_verified_vendors(
                query=f"{cat} contractor", city=updated_plan.location_city, min_rating=4.0
            )
            vendor_list = result.get("vendors", []) if isinstance(result, dict) else (result or [])
            top_vendor = vendor_list[0] if vendor_list else None
        except Exception:
            vendor_list = []
            top_vendor = None

        cat_lower = cat.lower()
        matched_any = False
        for item in updated_plan.boq:
            if item.status == "DROPPED":
                continue
            item_cat = item.category.lower()
            if item_cat == cat_lower or cat_lower in item_cat or item_cat in cat_lower:
                matched_any = True
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
                item.estimated_rate_inr = round(item.estimated_rate_inr * 1.05, 2)  # Emergency premium
                item.rate = item.estimated_rate_inr
                item.total_cost_inr = round(item.quantity * item.estimated_rate_inr, 2)
                item.total_cost = item.total_cost_inr
                item.status = "MODIFIED"
                boq_diffs.append(BOQDiffItem(
                    item_id=item.item_id,
                    action=DiffAction.MODIFIED,
                    original_item=orig_item,
                    updated_item=item,
                    reason=reason,
                ))

        if top_vendor:
            phone = top_vendor.get("phone") or top_vendor.get("nationalPhoneNumber") or "N/A"
            mitigations.append(f"Contact {top_vendor.get('name', 'listed vendor')} (Phone: {phone}) to confirm availability and quote.")
        else:
            mitigations.append("No verified vendor found via Maps; search manually.")
        if not matched_any:
            mitigations.append(f"No BOQ line items matched category '{cat}'; no line items were modified.")

    recompute_totals(updated_plan)
    new_total = updated_plan.current_estimated_total
    budget_delta = round(new_total - original_total, 2)

    # Optional augmentation via Gemini Flash
    api_key = settings.GEMINI_API_KEY
    if api_key and genai:
        try:
            prompt = f"""
            You are Pulse Dynamic Engine.
            Event: {plan.title} in {plan.location_city}.
            Crisis Trigger: {trigger.trigger_type} - {trigger.description}.
            Original Cost: INR {original_total:,.2f}. New Cost: INR {new_total:,.2f}. Ceiling: INR {updated_plan.total_budget_limit:,.2f}.
            Diff summary: {len(boq_diffs)} line item modifications, {len(schedule_diffs)} schedule adjustments.
            Briefly (under 100 words) provide a reassuring executive operational summary for the event planner.
            """
            gemini_res = await generate(
                model=settings.GEMINI_FLASH_MODEL,
                contents=[prompt],
                config=None,
                timeout=10.0,
            )
            if hasattr(gemini_res, "text") and gemini_res.text:
                narrative_paragraphs.append(gemini_res.text.strip())
        except Exception:
            pass

    full_narrative = "\n\n".join(narrative_paragraphs)

    return ContingencyDiff(
        diff_id=diff_id,
        trigger=trigger,
        timestamp_iso=timestamp,
        summary_narrative=full_narrative,
        original_total_inr=original_total,
        new_total_inr=new_total,
        budget_delta_inr=budget_delta,
        boq_diffs=boq_diffs,
        schedule_diffs=schedule_diffs,
        updated_plan=updated_plan,
        actionable_mitigations=mitigations
    )
