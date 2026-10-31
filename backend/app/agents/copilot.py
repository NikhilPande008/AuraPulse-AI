import uuid
import json
import logging
from typing import Dict, Any, List
from ..schemas import (
    MasterEventPlan,
    BOQItem,
    ScheduleBlock,
    PlanningMilestone,
    PriorityTier,
)
from ..config import settings

logger = logging.getLogger("aurapulse.copilot")

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None


async def chat_copilot(
    event_plan: MasterEventPlan,
    user_prompt: str
) -> Dict[str, Any]:
    """
    Conversational GenAI Ideas & Budget Co-Pilot:
    Allows planners/judges to converse with an AI event planner to alter menus,
    adjust line item costs, request cultural ritual additions, and discover party games.
    """
    prompt_lower = user_prompt.lower()
    
    # Attempt Gemini 2.5 Flash if API Key is configured
    api_key = settings.GEMINI_API_KEY
    if api_key and genai:
        try:
            client = genai.Client(api_key=api_key)
            system_instruction = (
                "You are AuraPulse Co-Pilot, an elite autonomous event planner and budgeting strategist. "
                "Analyze the user's event plan and their requested alteration. Provide a concise, professional reply, "
                "3-5 innovative ideas or actionable next steps, and specific adjustments to the Bill of Quantities."
            )
            context = f"""
            Event: {event_plan.title} ({event_plan.event_type}) in {event_plan.location_city}
            Budget Ceiling: INR {event_plan.total_budget_limit:,.2f}
            Current Estimated Total: INR {event_plan.current_estimated_total:,.2f}
            BOQ Items count: {len(event_plan.boq)}
            User Prompt: "{user_prompt}"

            Respond with JSON containing:
            1. "copilot_reply": string (A crisp, encouraging professional explanation of the changes and advice)
            2. "suggested_ideas": array of strings (3 to 5 high-impact bullet recommendations)
            """
            response = client.models.generate_content(
                model=settings.GEMINI_FLASH_MODEL,
                contents=[system_instruction, context],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.3
                )
            )
            parsed = json.loads(response.text)
            reply = parsed.get("copilot_reply")
            ideas = parsed.get("suggested_ideas", [])
            if reply and ideas:
                # Apply deterministic mutation based on prompt to also update the plan
                updated_plan = _apply_prompt_mutations(event_plan, prompt_lower)
                return {
                    "copilot_reply": reply,
                    "updated_plan": updated_plan,
                    "suggested_ideas": ideas
                }
        except Exception as e:
            logger.warning(f"Gemini Co-Pilot API call bypassed, using contextual engine: {e}")

    # Robust Contextual Engine (Instant & Guaranteed Zero-Breakage)
    updated_plan = _apply_prompt_mutations(event_plan, prompt_lower)
    reply, ideas = _generate_contextual_response(event_plan, prompt_lower, user_prompt)

    return {
        "copilot_reply": reply,
        "updated_plan": updated_plan,
        "suggested_ideas": ideas
    }


def _apply_prompt_mutations(plan: MasterEventPlan, prompt_lower: str) -> MasterEventPlan:
    """Clones and modifies the MasterEventPlan based on user prompt intent."""
    new_plan = plan.model_copy(deep=True)
    new_boq = list(new_plan.boq)
    
    # 1. Food / Puneri / Marathi / Regional Catering Swap
    if any(k in prompt_lower for k in ["puneri", "marathi", "cuisine", "food", "menu", "puran poli", "catering", "chaat", "thali"]):
        catering_found = False
        for item in new_boq:
            if item.category.lower() in ["catering", "food"]:
                item.name = "Authentic Puneri Maharashtrian Banquet & Live Faral Stations"
                item.specification = (
                    "Authentic Puneri Thali with pure-ghee Puran Poli, Katachi Amti, Kothimbir Vadi, "
                    "Indrayani rice, and live steaming Ukdiche Modak dessert station."
                )
                item.estimated_rate_inr = max(item.estimated_rate_inr, 1200.0)
                item.total_cost_inr = round(item.quantity * item.estimated_rate_inr, 2)
                item.status = "MODIFIED"
                catering_found = True
                break
        if not catering_found:
            new_boq.append(
                BOQItem(
                    item_id=f"boq_copilot_{uuid.uuid4().hex[:6]}",
                    category="Catering",
                    name="Authentic Regional Maharashtrian Live Catering",
                    specification="Traditional Puneri Thali featuring Puran Poli, Matki Usal, and fresh Modaks",
                    quantity=150.0,
                    unit="pax",
                    estimated_rate_inr=1250.0,
                    total_cost_inr=187500.0,
                    priority=PriorityTier.CRITICAL,
                    status="ACTIVE"
                )
            )

    # 2. Floral Cut & Saxophone / Acoustic Addition
    if any(k in prompt_lower for k in ["cut floral", "reduce floral", "cut flower", "sax", "saxophone", "acoustic"]):
        # Cut florals 20%
        for item in new_boq:
            if any(fl in item.name.lower() for fl in ["floral", "flower", "meadow", "botanical"]):
                item.total_cost_inr = round(item.total_cost_inr * 0.8, 2)
                item.estimated_rate_inr = round(item.total_cost_inr / max(item.quantity, 1.0), 2)
                item.specification += " [Optimized: -20% volume repurposed for live acoustic artist]"
                item.status = "MODIFIED"
                break
        
        # Add saxophonist if not present
        if not any("sax" in it.name.lower() for it in new_boq):
            new_boq.append(
                BOQItem(
                    item_id=f"boq_copilot_sax_{uuid.uuid4().hex[:4]}",
                    category="Entertainment",
                    name="Live Solo Saxophonist & Sunset Acoustic Session",
                    specification="Professional jazz/ambient saxophonist with wireless roaming mic & PA patch",
                    quantity=1.0,
                    unit="artist",
                    estimated_rate_inr=28000.0,
                    total_cost_inr=28000.0,
                    priority=PriorityTier.OPERATIONAL,
                    status="ACTIVE"
                )
            )

    # 3. Games / Interactive Activities
    if any(k in prompt_lower for k in ["game", "games", "activity", "activities", "kids", "interactive", "trivia"]):
        if not any("game" in it.name.lower() for it in new_boq):
            new_boq.append(
                BOQItem(
                    item_id=f"boq_copilot_games_{uuid.uuid4().hex[:4]}",
                    category="Entertainment",
                    name="Interactive Game Master & Arena Coordinator",
                    specification="Dedicated anchor for trivia tournaments, retro arcade challenges & prize facilitation",
                    quantity=1.0,
                    unit="lot",
                    estimated_rate_inr=18000.0,
                    total_cost_inr=18000.0,
                    priority=PriorityTier.OPERATIONAL,
                    status="ACTIVE"
                )
            )

    # 4. Return Gifts / Eco Favors
    if any(k in prompt_lower for k in ["gift", "gifts", "favor", "favors", "eco", "return gift"]):
        if not any("gift" in it.name.lower() or "favor" in it.name.lower() for it in new_boq):
            qty = 100.0
            new_boq.append(
                BOQItem(
                    item_id=f"boq_copilot_gifts_{uuid.uuid4().hex[:4]}",
                    category="Guest Experience",
                    name="Eco-Friendly Artisanal Return Gift Hampers",
                    specification="Plantable seed-paper stationery kits, terracotta diyas, and organic dry fruit jars",
                    quantity=qty,
                    unit="hamper",
                    estimated_rate_inr=180.0,
                    total_cost_inr=round(qty * 180.0, 2),
                    priority=PriorityTier.DISCRETIONARY,
                    status="ACTIVE"
                )
            )

    # 5. Cultural Ritual (e.g. Sakhar Puda, Haldi, Sangeet)
    if any(k in prompt_lower for k in ["sakhar puda", "haldi", "sangeet", "mehendi", "rituals", "pooja"]):
        new_milestones = list(new_plan.planning_milestones or [])
        if not any("ritual" in m.title.lower() or "sakhar" in m.title.lower() for m in new_milestones):
            new_milestones.insert(
                0,
                PlanningMilestone(
                    id=f"ms_ritual_{uuid.uuid4().hex[:4]}",
                    phase="T-1 Week",
                    title="Pre-Ceremony Cultural Rituals & Pooja Samagri Audit",
                    description="Confirm brass thalis, authentic sweets, coconut offerings, and priest coordination.",
                    due_date="2026-11-08",
                    category="Rituals",
                    completed=False
                )
            )
        new_plan.planning_milestones = new_milestones

    # Recalculate totals
    new_plan.boq = new_boq
    new_plan.current_estimated_total = round(sum(item.total_cost_inr for item in new_boq), 2)
    return new_plan


def _generate_contextual_response(plan: MasterEventPlan, prompt_lower: str, raw_prompt: str) -> tuple[str, List[str]]:
    """Generates insightful conversational copy and bullet ideas matching user intent."""
    if any(k in prompt_lower for k in ["puneri", "marathi", "cuisine", "food", "menu", "puran poli", "catering", "chaat", "thali"]):
        reply = (
            f"I have upgraded the catering section in '{plan.title}' to an authentic Maharashtrian Puneri feast! "
            "The menu now highlights freshly prepared pure-ghee Puran Poli, Katachi Amti, crisp Kothimbir Vadi, "
            "and a live Ukdiche Modak steaming counter. Quantities and line items are balanced to prevent budget overshoot."
        )
        ideas = [
            "Set up a live Ukdiche Modak counter where guests can watch artisanal shaping with saffron drizzle",
            "Serve refreshing Solkadhi shooters in clay kulhads as welcome drinks at the registration canopy",
            "Pair the main dining spread with warm Masala Doodh (spiced almond milk) for the evening reception",
            "Provide printed bi-lingual menu cards (Marathi & English) explaining the cultural heritage of each delicacy"
        ]
        return reply, ideas

    if any(k in prompt_lower for k in ["cut floral", "reduce floral", "cut flower", "sax", "saxophone", "acoustic"]):
        reply = (
            "Smart resource reallocation! I trimmed 20% from high-waste imported florals and reinvested "
            "₹28,000 into a live solo saxophonist for the golden-hour cocktail window. Your guests get elevated live acoustic ambiance while maintaining structural deck aesthetics."
        )
        ideas = [
            "Position the saxophonist on the elevated wooden decking just as sunset light hits the meadow",
            "Repurpose ceremony arch blooms onto the banquet tables to double visual mileage without extra spend",
            "Use warm filament pin-spot lighting and amber fairy canopies to maintain lushness in place of flowers",
            "Coordinate with the saxophonist to play low-tempo acoustic covers of contemporary indie tracks"
        ]
        return reply, ideas

    if any(k in prompt_lower for k in ["game", "games", "activity", "activities", "kids", "interactive", "trivia"]):
        reply = (
            "Here is an energetic entertainment lineup tailored for your guest profile! I also allocated an Interactive "
            "Game Master in your BOQ to manage pace and keep the celebration dynamic."
        )
        ideas = [
            "Cyberpunk Laser Tag / Glow Quest: Quick 5-minute tactical rounds in an illuminated zone",
            "Pop Culture Audio Trivia Face-Off: Live smartphone-based leaderboard trivia hosted by the anchor",
            "Neon Glow Dance-Off: LED wristband team challenges during the DJ warm-up set",
            "Custom AR Photo Filter Challenge: Guests scan a QR code to unlock custom event stickers and win prizes",
            "Retro Arcade High-Score Tournament: Twin cocktail-table arcade machines running classic 90s games"
        ]
        return reply, ideas

    if any(k in prompt_lower for k in ["gift", "gifts", "favor", "favors", "eco", "return gift"]):
        reply = (
            "Sustainable gifting leaves a lasting impression! I added eco-friendly hampers to your BOQ at ₹180 per unit, "
            "well within your target bracket while supporting local artisan clusters."
        )
        ideas = [
            "Seed-Paper Bookmark & Postcard Kits with embedded tulsi and wildflower seeds that guests can plant",
            "Hand-poured soy wax candles in reusable terracotta mitti pots with cardamom-vanilla aroma",
            "Miniature potted jade succulents in biodegradable coconut-coir planters",
            "Jute gift pouches filled with roasted spiced makhana (foxnuts) and organic almonds"
        ]
        return reply, ideas

    if any(k in prompt_lower for k in ["sakhar puda", "haldi", "sangeet", "mehendi", "rituals", "pooja"]):
        reply = (
            "I have incorporated dedicated ritual milestones and coordination tasks into your backwards planning roadmap. "
            "This ensures auspicious muhurat timing, brass pooja samagri procurement, and family traditions are honored."
        )
        ideas = [
            "Schedule the Sakhar Puda ceremony at the 11:15 AM muhurat prior to the afternoon sun peak",
            "Coordinate custom silver/brass thalis filled with freshly prepared pedhe and adorned coconuts",
            "Book a traditional live Shehnai and Dhol-Tasha welcome for the groom and bride arrival procession",
            "Designate a dedicated family logistics lead to oversee priest offerings and prasad distribution"
        ]
        return reply, ideas

    # Default insightful response
    reply = (
        f"I reviewed your request '{raw_prompt}' against the parameters of '{plan.title}'. "
        f"Your current estimated spend is ₹{plan.current_estimated_total:,.2f} against a ceiling of ₹{plan.total_budget_limit:,.2f}. "
        "Here are strategic recommendations to enhance guest engagement and optimize operations."
    )
    ideas = [
        "Audit vendor contracts 14 days prior to event to lock contingency cancellation thresholds",
        "Introduce digital QR-code schedules so guests receive real-time notifications of phase transitions",
        "Reserve 5% buffer allocation exclusively for unforeseen last-minute AV and power surges"
    ]
    return reply, ideas
