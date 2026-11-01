"""Supply failure contingency handler for Pulse Engine."""

import copy
from typing import Any

import google.api_core.exceptions
import httpx

from ...schemas import (
    BOQDiffItem,
    BOQItem,
    CrisisTrigger,
    DiffAction,
    MasterEventPlan,
)
from .. import pulse_engine
from .models import CrisisExecutionResult


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
        result = await pulse_engine.fetch_verified_vendors(query=f"{category} contractor", city=city, min_rating=4.0)
        vendor_list = result.get("vendors", []) if isinstance(result, dict) else (result or [])
        return vendor_list[0] if vendor_list else None
    except (httpx.HTTPError, google.api_core.exceptions.GoogleAPIError, ValueError, KeyError, OSError, RuntimeError):
        return None


def _is_category_match(item_cat: str, cat_lower: str) -> bool:
    return item_cat == cat_lower or cat_lower in item_cat or item_cat in cat_lower


def _replace_matching_boq_items(
    boq: list[BOQItem], cat: str, top_vendor: dict[str, Any] | None
) -> tuple[list[BOQDiffItem], bool]:
    diffs: list[BOQDiffItem] = []
    cat_lower = cat.lower()
    matched_any = False
    for item in boq:
        if item.status != "DROPPED" and _is_category_match(item.category.lower(), cat_lower):
            matched_any = True
            diffs.append(_apply_vendor_replacement(item, top_vendor))
    return diffs, matched_any


def _build_supply_mitigations(cat: str, top_vendor: dict[str, Any] | None, matched_any: bool) -> list[str]:
    mitigations = [f"Automated vendor hot-swap for failed {cat} supplier via Google Maps Places API"]
    if top_vendor:
        phone = top_vendor.get("phone") or top_vendor.get("nationalPhoneNumber") or "N/A"
        mitigations.append(
            f"Contact {top_vendor.get('name', 'listed vendor')} (Phone: {phone}) to confirm availability and quote."
        )
    else:
        mitigations.append("No verified vendor found via Maps; search manually.")
    if not matched_any:
        mitigations.append(f"No BOQ line items matched category '{cat}'; no line items were modified.")
    return mitigations


async def _handle_supply_failure(
    updated_plan: MasterEventPlan, trigger: CrisisTrigger, original_total: float
) -> tuple[MasterEventPlan, CrisisExecutionResult]:
    res = CrisisExecutionResult()
    cat = trigger.affected_vendor_category or "Catering"
    res.narrative_paragraphs.append(
        f"SUPPLY FAILURE PROTOCOL: Primary vendor in '{cat}' reported abrupt cancellation. "
        "AuraPulse immediately engaged Google Maps Places API to locate verified top-rated replacement vendors in the target locality."
    )

    top_vendor = await _lookup_replacement_vendor(cat, updated_plan.location_city)
    diffs, matched_any = _replace_matching_boq_items(updated_plan.boq, cat, top_vendor)
    res.boq_diffs.extend(diffs)
    res.mitigations.extend(_build_supply_mitigations(cat, top_vendor, matched_any))

    return updated_plan, res
