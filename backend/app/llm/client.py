import os
import json
import uuid
import base64
import asyncio
import logging
from typing import Optional, Dict, Any, List
from ..config import settings
from ..schemas import (
    MasterEventPlan,
    BOQItem,
    ScheduleBlock,
    PriorityTier,
    PlanningMilestone,
    VendorChecklistItem,
    PlanRequest,
    EventIdea,
)
from ..services.timeline import build_milestones

logger = logging.getLogger("aurapulse.llm")

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None


def get_genai_client() -> Optional[Any]:
    """Unified GenAI Client initialization using modern google-genai SDK."""
    if not genai:
        logger.error("google-genai package is not installed.")
        return None
    api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        logger.error("GEMINI_API_KEY is not configured.")
        return None
    return genai.Client(api_key=api_key)


async def generate_event_plan(
    request: PlanRequest,
    timeout: float = 30.0
) -> MasterEventPlan:
    """
    Asynchronous Gemini Generation Engine (CR-08):
    Generates tailored MasterEventPlan using Gemini 2.5 Flash with schema-guided
    structured JSON, cultural ritual grounding, deterministic calculation,
    and server-side budget ceiling enforcement.
    """
    client = get_genai_client()
    if not client:
        raise RuntimeError("Gemini Client could not be initialized (missing API key or SDK)")

    system_instruction = f"""
    You are Aura Vision & Planning Engine, the premier AI Event Architect for AuraPulse.
    Construct a comprehensive, highly authentic event plan for a {request.event_type} in {request.city}.
    Headcount: {request.headcount} guests.
    Budget Ceiling: INR {request.budget:,.2f}.
    Culture/Region: {request.culture_region or 'Indian Contemporary'}.
    Theme: {request.theme or 'Elegant Celebration'}.
    Dietary Preferences: {', '.join(request.dietary) if request.dietary else 'Standard Gourmet'}.
    Language Context: {request.language}.

    CRITICAL REQUIREMENTS:
    1. Bill of Quantities (BOQ):
       - Exactly reflect regional/cultural specifics:
         * If Maharashtrian/Marathi: Authentic Puneri Thali, Puran Poli, Ukdiche Modak, Dhol Tasha troupe, Mandap & Sakhar Puda setups.
         * If Birthday: Interactive games, DJ synth sound, customized theme cake, party favors, game coordinator.
         * If Community Event/Festival: Sound & fire permits, clean waste management, stall structures, stage power DG set.
       - Each line item must have: item_id (uuid), category, name, specification, quantity, unit, estimated_rate_inr, total_cost_inr, priority_tier ("Critical", "Operational", "Discretionary").
       - Categorize accurately:
         * Critical: Core safety, stage infrastructure, legal permits, primary food banquet.
         * Operational: Sound line arrays, stage lighting, guest comfort seating.
         * Discretionary: Exotic imported florals, luxury photo booths, cold pyro SFX.
    2. Ideas: Provide 3 to 5 innovative, thematic ideas with title, rationale, and estimated_cost.
    3. Schedule: 5 to 6 chronological blocks marking is_outdoor=True/False.
    4. Vendor Checklist: 4 to 5 vendor entries with realistic categories, estimated costs, and statuses.
    5. The sum of total_cost_inr across all items MUST NOT exceed INR {request.budget:,.2f}.
    """

    user_prompt = f"Generate complete event plan for {request.event_type} in {request.city} for {request.headcount} pax within INR {request.budget:,.2f}."

    contents: List[Any] = [system_instruction, user_prompt]

    if request.image_base64:
        try:
            clean_b64 = request.image_base64.split(",")[-1] if "," in request.image_base64 else request.image_base64
            img_bytes = base64.b64decode(clean_b64)
            contents.append(types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"))
        except Exception as e:
            logger.warning(f"Failed to decode moodboard image bytes: {e}")

    try:
        response = await asyncio.wait_for(
            client.aio.models.generate_content(
                model=settings.GEMINI_FLASH_MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=MasterEventPlan,
                    temperature=0.2,
                )
            ),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        logger.error(f"Gemini generation timed out after {timeout}s")
        raise TimeoutError(f"Gemini plan generation timed out after {timeout} seconds")
    except Exception as e:
        logger.error(f"Gemini API generate_content failed: {e}")
        raise

    if not response or not response.text:
        raise ValueError("Empty response received from Gemini generation engine")

    parsed = json.loads(response.text)
    plan = MasterEventPlan.model_validate(parsed)

    # Server-Side Deterministic Validation & Mathematical Integrity
    plan.total_budget_limit = request.budget
    plan.location_city = request.city
    plan.event_type = request.event_type
    plan.event_date = request.event_date
    plan.culture_region = request.culture_region
    plan.theme = request.theme

    # Recalculate deterministic line totals: quantity * rate
    calc_total = 0.0
    for item in plan.boq:
        item.total_cost_inr = round(float(item.quantity) * float(item.estimated_rate_inr), 2)
        item.rate = item.estimated_rate_inr
        item.total_cost = item.total_cost_inr
        item.priority_tier = item.priority
        calc_total += item.total_cost_inr

    plan.current_estimated_total = round(calc_total, 2)

    # Enforce budget ceiling server-side: trim Discretionary and Operational items if exceeded
    if plan.current_estimated_total > plan.total_budget_limit:
        overage = plan.current_estimated_total - plan.total_budget_limit
        logger.warning(f"Initial generated total ({plan.current_estimated_total}) exceeded budget ({plan.total_budget_limit}). Enforcing ceiling.")
        # Find non-critical items
        non_critical = [it for it in plan.boq if it.priority != PriorityTier.CRITICAL]
        if non_critical:
            factor = max(0.5, (plan.total_budget_limit * 0.95) / plan.current_estimated_total)
            for it in non_critical:
                it.estimated_rate_inr = round(it.estimated_rate_inr * factor, 2)
                it.rate = it.estimated_rate_inr
                it.total_cost_inr = round(it.quantity * it.estimated_rate_inr, 2)
                it.total_cost = it.total_cost_inr
            plan.current_estimated_total = round(sum(it.total_cost_inr for it in plan.boq), 2)

    # Formulate dynamic backwards milestones based on event date
    if request.event_date:
        plan.planning_milestones = build_milestones(
            event_date=request.event_date,
            event_type=request.event_type,
            culture_region=request.culture_region
        )

    return plan
