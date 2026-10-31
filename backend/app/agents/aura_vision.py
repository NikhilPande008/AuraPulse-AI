import uuid
import json
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from ..schemas import (
    MasterEventPlan,
    BOQItem,
    ScheduleBlock,
    PriorityTier,
    PlanningMilestone,
    MilestonePhase,
    MilestoneCategory,
    VendorChecklistItem,
    VendorStatus,
)
from ..config import settings

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None


def get_backwards_date(base_date_str: str, days_before: int) -> str:
    """Helper to calculate milestone due dates backwards from event date."""
    try:
        dt = datetime.strptime(base_date_str, "%Y-%m-%d")
        target = dt - timedelta(days=days_before)
        return target.strftime("%Y-%m-%d")
    except Exception:
        return "2026-11-01"


def create_preset_meadow_wedding(event_date: str = "2026-11-15") -> MasterEventPlan:
    """Preset 1: Boho Sunset Meadow Wedding (Pune, 300 Pax, ₹15,00,000)"""
    return MasterEventPlan(
        event_id=f"evt_{uuid.uuid4().hex[:8]}",
        event_type="wedding",
        title="Boho Sunset Meadow Wedding (Pastel Peach & Sage)",
        location_city="Pune",
        currency="INR",
        total_budget_limit=1500000.0,
        current_estimated_total=1420000.0,
        boq=[
            BOQItem(
                item_id="boq_meadow_01",
                category="Catering",
                name="Farm-to-Table Organic Banquet & Woodfired Live Stations",
                specification="300 Pax, live woodfired sourdough pizza, artisanal pasta & farm salads",
                quantity=300.0,
                unit="pax",
                estimated_rate_inr=1500.0,
                total_cost_inr=450000.0,
                priority=PriorityTier.CRITICAL,
                status="ACTIVE"
            ),
            BOQItem(
                item_id="boq_meadow_02",
                category="Infrastructure",
                name="Weather-Treated Bamboo Pergolas & Meadow Decking",
                specification="100% natural bamboo timber pergolas, raised teak wood ceremony deck (24x20 ft)",
                quantity=1.0,
                unit="lot",
                estimated_rate_inr=180000.0,
                total_cost_inr=180000.0,
                priority=PriorityTier.CRITICAL,
                status="ACTIVE"
            ),
            BOQItem(
                item_id="boq_meadow_03",
                category="Power & Safety",
                name="82.5 kVA Silent DG Set & Eco Earthing Distribution",
                specification="Super silent acoustic enclosure, industrial trip switches, 4x CO2 fire extinguishers",
                quantity=1.0,
                unit="unit",
                estimated_rate_inr=85000.0,
                total_cost_inr=85000.0,
                priority=PriorityTier.CRITICAL,
                status="ACTIVE"
            ),
            BOQItem(
                item_id="boq_meadow_04",
                category="Audio / Visual",
                name="Warm Acoustic Line Array & Shure Wireless Mics",
                specification="Compact column array setup tuned for open meadow acoustics, 4 wireless mics",
                quantity=1.0,
                unit="system",
                estimated_rate_inr=120000.0,
                total_cost_inr=120000.0,
                priority=PriorityTier.OPERATIONAL,
                status="ACTIVE"
            ),
            BOQItem(
                item_id="boq_meadow_05",
                category="Lighting",
                name="2,000 ft Warm Edison Festoon Light Canopy",
                specification="Vintage warm-glow tungsten filament festoon grid suspended over meadow dining",
                quantity=1.0,
                unit="installation",
                estimated_rate_inr=175000.0,
                total_cost_inr=175000.0,
                priority=PriorityTier.OPERATIONAL,
                status="ACTIVE"
            ),
            BOQItem(
                item_id="boq_meadow_06",
                category="Furniture & Seating",
                name="Whitewashed Wooden Benches & Cane Lounge Loungers",
                specification="30 whitewashed rustic dining tables, 250 wooden benches & woven wicker armchairs",
                quantity=280.0,
                unit="units",
                estimated_rate_inr=500.0,
                total_cost_inr=140000.0,
                priority=PriorityTier.OPERATIONAL,
                status="ACTIVE"
            ),
            BOQItem(
                item_id="boq_meadow_07",
                category="Floral Art",
                name="Pampas Grass Arch, Dried Palms & Peach Hydrangeas",
                specification="Organic dried floral ceremony arch, eucalyptus aisle runners & rustic meadow accents",
                quantity=1.0,
                unit="installation",
                estimated_rate_inr=160000.0,
                total_cost_inr=160000.0,
                priority=PriorityTier.DISCRETIONARY,
                status="ACTIVE"
            ),
            BOQItem(
                item_id="boq_meadow_08",
                category="Decor & Ambiance",
                name="Macramé Backdrops & Terracotta Aisle Lanterns",
                specification="Hand-knotted macramé photo wall, 60 brass lanterns with battery pillar candles",
                quantity=1.0,
                unit="lot",
                estimated_rate_inr=75000.0,
                total_cost_inr=75000.0,
                priority=PriorityTier.DISCRETIONARY,
                status="ACTIVE"
            ),
            BOQItem(
                item_id="boq_meadow_09",
                category="Interactive Experience",
                name="Polaroid Guestbook Kiosk & Flower Crown Bar",
                specification="Vintage wooden photo booth station with instant film prints and live floral crown crafter",
                quantity=1.0,
                unit="lot",
                estimated_rate_inr=35000.0,
                total_cost_inr=35000.0,
                priority=PriorityTier.DISCRETIONARY,
                status="ACTIVE"
            ),
        ],
        schedule=[
            ScheduleBlock(
                block_id="sch_m01",
                phase="Setup & Rigging",
                start_time_iso="09:00",
                end_time_iso="13:00",
                activity="Meadow pergola timber assembly & 2,000 ft festoon light stringing",
                responsible_party="EcoScaffold Productions",
                is_outdoor=True
            ),
            ScheduleBlock(
                block_id="sch_m02",
                phase="Guest Arrival",
                start_time_iso="15:30",
                end_time_iso="16:45",
                activity="Sunset meadow welcome, sparkling botanical mocktails & flower crown fitting",
                responsible_party="Meadow Hospitality Team",
                is_outdoor=True
            ),
            ScheduleBlock(
                block_id="sch_m03",
                phase="Main Ceremony",
                start_time_iso="17:00",
                end_time_iso="18:30",
                activity="Vow exchange beneath pampas grass arch during golden hour sunset",
                responsible_party="Celebrant & Family Leads",
                is_outdoor=True
            ),
            ScheduleBlock(
                block_id="sch_m04",
                phase="Sunset Soirée",
                start_time_iso="18:30",
                end_time_iso="19:30",
                activity="Golden hour acoustic guitar & cello performance with woodfired canapés",
                responsible_party="Acoustic Trio",
                is_outdoor=True
            ),
            ScheduleBlock(
                block_id="sch_m05",
                phase="Dinner & Banquet",
                start_time_iso="19:30",
                end_time_iso="22:30",
                activity="Farm-to-table banquet served family-style under warm Edison festoon canopy",
                responsible_party="Artisan Head Chef",
                is_outdoor=True
            ),
            ScheduleBlock(
                block_id="sch_m06",
                phase="Afterparty",
                start_time_iso="22:30",
                end_time_iso="01:00",
                activity="Barnhouse indoor acoustic jam, craft cider bar & midnight bonfire",
                responsible_party="Night Operations Lead",
                is_outdoor=False
            ),
        ],
        planning_milestones=[
            PlanningMilestone(
                id="ms_m01",
                phase=MilestonePhase.T_MINUS_6_MONTHS,
                title="Lock Meadow Estate & Barnhouse Booking",
                description="Finalize signed agreement for private hillside meadow property with wet weather backup barn.",
                due_date=get_backwards_date(event_date, 180),
                category=MilestoneCategory.VENUE,
                completed=True
            ),
            PlanningMilestone(
                id="ms_m02",
                phase=MilestonePhase.T_MINUS_3_MONTHS,
                title="Farm-to-Table Menu Tasting & Live Station Sign-off",
                description="Culinary tasting of woodfired sourdough pizza, pasta, and organic local wines with head chef.",
                due_date=get_backwards_date(event_date, 90),
                category=MilestoneCategory.CATERING,
                completed=True
            ),
            PlanningMilestone(
                id="ms_m03",
                phase=MilestonePhase.T_MINUS_1_MONTH,
                title="Pampas Floral Arch & Festoon Lighting Mockup",
                description="Visual review of dried palm installations, peach hydrangeas, and warm Edison stringing geometry.",
                due_date=get_backwards_date(event_date, 30),
                category=MilestoneCategory.DECOR,
                completed=False
            ),
            PlanningMilestone(
                id="ms_m04",
                phase=MilestonePhase.T_MINUS_2_WEEKS,
                title="Dispatch Linen Digital Invitations & RSVP Lock",
                description="Confirm final dietary requirements (vegan/gluten-free) and headcounts for 300 guests.",
                due_date=get_backwards_date(event_date, 14),
                category=MilestoneCategory.ATTIRE_INVITES,
                completed=False
            ),
            PlanningMilestone(
                id="ms_m05",
                phase=MilestonePhase.T_MINUS_1_WEEK,
                title="Microclimate Check & Generator Earthing Inspection",
                description="Review 7-day weather forecast, test 82.5 kVA silent genset, and review rain contingency protocol.",
                due_date=get_backwards_date(event_date, 7),
                category=MilestoneCategory.LOGISTICS,
                completed=False
            ),
            PlanningMilestone(
                id="ms_m06",
                phase=MilestonePhase.DAY_OF,
                title="Bride Meadow Entry & Sunset Vow Exchange",
                description="Check flower crown bar setup, acoustic trio soundcheck, and golden hour ceremonial cue.",
                due_date=event_date,
                category=MilestoneCategory.RITUALS,
                completed=False
            ),
        ],
        vendor_checklist=[
            VendorChecklistItem(
                id="vc_m01",
                category="Catering & Banquet",
                vendor_name="Artisan Kitchen Pune (Farm-to-Table)",
                estimated_cost=450000.0,
                status=VendorStatus.BOOKED,
                notes="Deposit paid (30%). Woodfired ovens mobilization confirmed for 07:00 AM.",
                google_maps_place_id="ChIJ_pune_artisan_cater"
            ),
            VendorChecklistItem(
                id="vc_m02",
                category="Floral & Stage Decor",
                vendor_name="BloomCraft Botanicals (Pampas & Sage)",
                estimated_cost=160000.0,
                status=VendorStatus.QUOTED,
                notes="Revised quote for dried palms and local marigold garland substitution submitted.",
                google_maps_place_id="ChIJ_pune_bloom_craft"
            ),
            VendorChecklistItem(
                id="vc_m03",
                category="Audio / Visual & Lighting",
                vendor_name="LumenGlow & AcousticPro Rigging",
                estimated_cost=295000.0,
                status=VendorStatus.BOOKED,
                notes="Includes 2,000 ft festoons and waterproof column array audio system.",
                google_maps_place_id="ChIJ_pune_lumenglow"
            ),
            VendorChecklistItem(
                id="vc_m04",
                category="Power & Safety",
                vendor_name="PowerGrid Silent DG Sets",
                estimated_cost=85000.0,
                status=VendorStatus.TO_CONTACT,
                notes="Need to verify local municipal earthing certificate for hillside lawn.",
                google_maps_place_id="ChIJ_pune_powergrid"
            ),
            VendorChecklistItem(
                id="vc_m05",
                category="Photography & Drone",
                vendor_name="GoldenHour Cinematic Studios",
                estimated_cost=85000.0,
                status=VendorStatus.PAID,
                notes="100% advance paid. 2 cinematographers and 1 drone pilot confirmed.",
                google_maps_place_id="ChIJ_pune_goldenhour"
            )
        ]
    )


def create_preset_cyberpunk_birthday(event_date: str = "2026-11-15") -> MasterEventPlan:
    """Preset 2: Cyberpunk Neon 30th Birthday (Mumbai, 60 Pax, ₹2,50,000)"""
    return MasterEventPlan(
        event_id=f"evt_{uuid.uuid4().hex[:8]}",
        event_type="birthday",
        title="Cyberpunk Neon 30th Birthday (Violet & Electric Cyan)",
        location_city="Mumbai",
        currency="INR",
        total_budget_limit=250000.0,
        current_estimated_total=238000.0,
        boq=[
            BOQItem(
                item_id="boq_cyber_01",
                category="Catering & Bar",
                name="Artisanal Tapas, Sliders & Molecular Mocktail Bar",
                specification="60 Pax, gourmet mini burgers, truffle fries, dry ice molecular mocktails",
                quantity=60.0,
                unit="pax",
                estimated_rate_inr=1400.0,
                total_cost_inr=84000.0,
                priority=PriorityTier.CRITICAL,
                status="ACTIVE"
            ),
            BOQItem(
                item_id="boq_cyber_02",
                category="Audio / Visual",
                name="Club-Grade Sound Rig & Subwoofers",
                specification="QSC K12.2 active tops, KW181 18-inch sub, Pioneer DDJ-1000 controller",
                quantity=1.0,
                unit="system",
                estimated_rate_inr=38000.0,
                total_cost_inr=38000.0,
                priority=PriorityTier.CRITICAL,
                status="ACTIVE"
            ),
            BOQItem(
                item_id="boq_cyber_03",
                category="Power & Safety",
                name="Dedicated Line Feeder & Voltage Stabilizer",
                specification="Isolated 15A audio power rail, surge suppressor & CO2 fire safety unit",
                quantity=1.0,
                unit="lot",
                estimated_rate_inr=16000.0,
                total_cost_inr=16000.0,
                priority=PriorityTier.CRITICAL,
                status="ACTIVE"
            ),
            BOQItem(
                item_id="boq_cyber_04",
                category="Lighting",
                name="Pixel Tube Matrix & UV Blacklight Wash Rig",
                specification="16 wireless Astera-style LED pixel tubes, 8 high-output UV blacklights, DMX strobe",
                quantity=24.0,
                unit="fixtures",
                estimated_rate_inr=1458.33,
                total_cost_inr=35000.0,
                priority=PriorityTier.OPERATIONAL,
                status="ACTIVE"
            ),
            BOQItem(
                item_id="boq_cyber_05",
                category="Entertainment",
                name="Pro Electronic/Techno DJ & Live Synth Host",
                specification="4-hour curated techno/synthwave set with live analog synthesizer hooks",
                quantity=1.0,
                unit="session",
                estimated_rate_inr=30000.0,
                total_cost_inr=30000.0,
                priority=PriorityTier.OPERATIONAL,
                status="ACTIVE"
            ),
            BOQItem(
                item_id="boq_cyber_06",
                category="Decor & Styling",
                name="Custom Acrylic Neon Signage ('30 & UNSTOPPABLE')",
                specification="Bespoke dual-tone violet/cyan flex-neon wall piece with acrylic backer",
                quantity=1.0,
                unit="piece",
                estimated_rate_inr=20000.0,
                total_cost_inr=20000.0,
                priority=PriorityTier.DISCRETIONARY,
                status="ACTIVE"
            ),
            BOQItem(
                item_id="boq_cyber_07",
                category="Experience",
                name="Cyberpunk Glow Tattoo Station & Mirror Photo Op",
                specification="UV-reactive temporary body paint artist, neon props, instant digital GIF booth",
                quantity=1.0,
                unit="lot",
                estimated_rate_inr=15000.0,
                total_cost_inr=15000.0,
                priority=PriorityTier.DISCRETIONARY,
                status="ACTIVE"
            ),
        ],
        schedule=[
            ScheduleBlock(
                block_id="sch_c01",
                phase="Setup & Audio Check",
                start_time_iso="18:00",
                end_time_iso="19:30",
                activity="Audio rigging, pixel tube programming & UV blacklight focus",
                responsible_party="Sound & Light Technician",
                is_outdoor=False
            ),
            ScheduleBlock(
                block_id="sch_c02",
                phase="Neon Arrival",
                start_time_iso="20:00",
                end_time_iso="21:00",
                activity="Guest welcome, UV glow tattoo station & molecular signature drinks",
                responsible_party="Bar Lead & Host",
                is_outdoor=False
            ),
            ScheduleBlock(
                block_id="sch_c03",
                phase="Birthday Toast",
                start_time_iso="21:00",
                end_time_iso="21:30",
                activity="Roast & toast, cyberpunk cake cutting with dry ice waterfall",
                responsible_party="MC & Birthday Lead",
                is_outdoor=False
            ),
            ScheduleBlock(
                block_id="sch_c04",
                phase="Prime Dance Set",
                start_time_iso="21:30",
                end_time_iso="23:30",
                activity="Live DJ synthwave and peak-time techno set, passing tapas",
                responsible_party="Featured DJ",
                is_outdoor=False
            ),
            ScheduleBlock(
                block_id="sch_c05",
                phase="After-Hours Club Mix",
                start_time_iso="23:30",
                end_time_iso="01:30",
                activity="Sub-bass after-hours groove, midnight sliders & espresso shots",
                responsible_party="Sound Engineer",
                is_outdoor=False
            ),
        ],
        planning_milestones=[
            PlanningMilestone(
                id="ms_c01",
                phase=MilestonePhase.T_MINUS_1_MONTH,
                title="Lock Industrial Rooftop Loft (Worli Seaface)",
                description="Sign 6-hour exclusive venue rental with private elevator access and sound permit.",
                due_date=get_backwards_date(event_date, 30),
                category=MilestoneCategory.VENUE,
                completed=True
            ),
            PlanningMilestone(
                id="ms_c02",
                phase=MilestonePhase.T_MINUS_2_WEEKS,
                title="Molecular Mocktail & Gourmet Sliders Menu Tasting",
                description="Approve 4 signature cocktails with dry ice smoke cues and vegan slider options.",
                due_date=get_backwards_date(event_date, 14),
                category=MilestoneCategory.CATERING,
                completed=True
            ),
            PlanningMilestone(
                id="ms_c03",
                phase=MilestonePhase.T_MINUS_1_WEEK,
                title="Custom Neon Signage Fabrication & Astera Pixel Mapping",
                description="Inspect '30 & UNSTOPPABLE' acrylic sign and pre-program wireless DMX light show.",
                due_date=get_backwards_date(event_date, 7),
                category=MilestoneCategory.DECOR,
                completed=False
            ),
            PlanningMilestone(
                id="ms_c04",
                phase=MilestonePhase.DAY_OF,
                title="Subwoofer Tuning, UV Blacklight Focus & DJ Tech Check",
                description="Final decibel calibration, smoke machine fluid levels check, and UV body paint artist setup.",
                due_date=event_date,
                category=MilestoneCategory.LOGISTICS,
                completed=False
            ),
        ],
        vendor_checklist=[
            VendorChecklistItem(
                id="vc_c01",
                category="Bar & Molecular Tapas",
                vendor_name="Smoke & Mirrors Mumbai",
                estimated_cost=84000.0,
                status=VendorStatus.BOOKED,
                notes="Molecular bar equipment and dry ice coolers included.",
                google_maps_place_id="ChIJ_mumbai_smoke_mirrors"
            ),
            VendorChecklistItem(
                id="vc_c02",
                category="Sound & Subwoofers",
                vendor_name="SubBass Audio Rentals Bandra",
                estimated_cost=38000.0,
                status=VendorStatus.BOOKED,
                notes="Dual 18-inch subwoofers + sound engineer on-site.",
                google_maps_place_id="ChIJ_mumbai_subbass"
            ),
            VendorChecklistItem(
                id="vc_c03",
                category="Lighting & Neon",
                vendor_name="NeonFlux FX Mumbai",
                estimated_cost=35000.0,
                status=VendorStatus.QUOTED,
                notes="Awaiting final delivery quote for custom acrylic neon crest.",
                google_maps_place_id="ChIJ_mumbai_neonflux"
            ),
            VendorChecklistItem(
                id="vc_c04",
                category="Featured DJ",
                vendor_name="DJ Kinetix (Synthwave/Techno)",
                estimated_cost=30000.0,
                status=VendorStatus.PAID,
                notes="Track list approved. 100% advance cleared.",
                google_maps_place_id="ChIJ_mumbai_dj_kinetix"
            ),
        ]
    )


def create_preset_diwali_mela(event_date: str = "2026-11-15") -> MasterEventPlan:
    """Preset 3: Eco-Friendly Society Diwali Mela (Pune, 800 Pax, ₹5,00,000)"""
    return MasterEventPlan(
        event_id=f"evt_{uuid.uuid4().hex[:8]}",
        event_type="community_festival",
        title="Eco-Friendly Society Diwali Mela (Zero Plastic & Heritage)",
        location_city="Pune",
        currency="INR",
        total_budget_limit=500000.0,
        current_estimated_total=475000.0,
        boq=[
            BOQItem(
                item_id="boq_mela_01",
                category="Security & Compliance",
                name="Municipal Permissions, Fire Extinguishers & First-Aid Desk",
                specification="Local ward clearances, 6x ABC fire safety stations, on-site paramedic desk",
                quantity=1.0,
                unit="lot",
                estimated_rate_inr=45000.0,
                total_cost_inr=45000.0,
                priority=PriorityTier.CRITICAL,
                status="ACTIVE"
            ),
            BOQItem(
                item_id="boq_mela_02",
                category="Waste Management",
                name="Zero-Plastic Segregation & Compostable Cutlery Logistics",
                specification="Areca palm leaf plates, clay kulhads, 10 dry/wet waste segregation stations with 4 marshals",
                quantity=1.0,
                unit="lot",
                estimated_rate_inr=60000.0,
                total_cost_inr=60000.0,
                priority=PriorityTier.CRITICAL,
                status="ACTIVE"
            ),
            BOQItem(
                item_id="boq_mela_03",
                category="Power & Safety",
                name="100 kVA Silent Backup Generator & Main Switchboard",
                specification="Industrial cabling to 25 food stalls and central stage, auto transfer switch",
                quantity=1.0,
                unit="unit",
                estimated_rate_inr=70000.0,
                total_cost_inr=70000.0,
                priority=PriorityTier.CRITICAL,
                status="ACTIVE"
            ),
            BOQItem(
                item_id="boq_mela_04",
                category="Staging & Sound",
                name="Community Cultural Stage (24x16 ft) & PA Sound System",
                specification="Covered podium with stairs, JBL VRX PA setup for speeches and folk dance tracks",
                quantity=1.0,
                unit="setup",
                estimated_rate_inr=80000.0,
                total_cost_inr=80000.0,
                priority=PriorityTier.OPERATIONAL,
                status="ACTIVE"
            ),
            BOQItem(
                item_id="boq_mela_05",
                category="Lighting",
                name="Solar-Powered LED Festoon Array & Terracotta Diya Borders",
                specification="3,000 meters low-voltage LED string lights, 500 earthen mustard oil diyas with safety trays",
                quantity=1.0,
                unit="lot",
                estimated_rate_inr=75000.0,
                total_cost_inr=75000.0,
                priority=PriorityTier.OPERATIONAL,
                status="ACTIVE"
            ),
            BOQItem(
                item_id="boq_mela_06",
                category="Stalls & Canopies",
                name="25 Natural Bamboo & Cotton Fabric Artisan Stalls",
                specification="Octanorm/bamboo stall frames (10x10 ft) with overhead LED lights and table linens",
                quantity=25.0,
                unit="stalls",
                estimated_rate_inr=3800.0,
                total_cost_inr=95000.0,
                priority=PriorityTier.OPERATIONAL,
                status="ACTIVE"
            ),
            BOQItem(
                item_id="boq_mela_07",
                category="Cultural Decor",
                name="Organic Marigold Torans & Natural Petal Rangolis",
                specification="Fresh indigenous orange & yellow marigolds, 4 massive society courtyard rangoli installations",
                quantity=1.0,
                unit="lot",
                estimated_rate_inr=30000.0,
                total_cost_inr=30000.0,
                priority=PriorityTier.DISCRETIONARY,
                status="ACTIVE"
            ),
            BOQItem(
                item_id="boq_mela_08",
                category="Entertainment",
                name="Traditional Puneri Dhol Tasha Troupe (Opening Act)",
                specification="15-member energetic authentic Dhol Tasha performance for grand sunset inauguration",
                quantity=1.0,
                unit="troupe",
                estimated_rate_inr=20000.0,
                total_cost_inr=20000.0,
                priority=PriorityTier.DISCRETIONARY,
                status="ACTIVE"
            ),
        ],
        schedule=[
            ScheduleBlock(
                block_id="sch_dm01",
                phase="Stall Handover",
                start_time_iso="10:00",
                end_time_iso="14:00",
                activity="Bamboo artisan stall erection, zero-plastic waste bin deployment & power tests",
                responsible_party="Society Managing Committee",
                is_outdoor=True
            ),
            ScheduleBlock(
                block_id="sch_dm02",
                phase="Grand Inauguration",
                start_time_iso="16:00",
                end_time_iso="17:00",
                activity="Dhol Tasha procession, ribbon cutting by society elders & diya lighting",
                responsible_party="Cultural Secretary",
                is_outdoor=True
            ),
            ScheduleBlock(
                block_id="sch_dm03",
                phase="Artisan Exhibition",
                start_time_iso="17:00",
                end_time_iso="19:00",
                activity="Handmade crafts, organic sweets, terracotta pottery live demonstrations",
                responsible_party="Stall Coordinators",
                is_outdoor=True
            ),
            ScheduleBlock(
                block_id="sch_dm04",
                phase="Cultural Showcase",
                start_time_iso="19:00",
                end_time_iso="20:30",
                activity="Children's folk dance performances, classical sitar recital on main stage",
                responsible_party="Youth Group Lead",
                is_outdoor=True
            ),
            ScheduleBlock(
                block_id="sch_dm05",
                phase="Diwali Feast & Diya Glow",
                start_time_iso="20:30",
                end_time_iso="22:30",
                activity="500 earthen diyas illuminated across courtyard, food stalls active",
                responsible_party="Food & Safety Marshal",
                is_outdoor=True
            ),
            ScheduleBlock(
                block_id="sch_dm06",
                phase="Eco Teardown",
                start_time_iso="22:30",
                end_time_iso="23:30",
                activity="Waste audit, compostable bag collection & green venue handover",
                responsible_party="Cleanliness Taskforce",
                is_outdoor=True
            ),
        ],
        planning_milestones=[
            PlanningMilestone(
                id="ms_dm01",
                phase=MilestonePhase.T_MINUS_3_MONTHS,
                title="Society General Body Clearance & Ward Permissions",
                description="Pass society resolution for open courtyard mela and obtain local ward noise/fire NOCs.",
                due_date=get_backwards_date(event_date, 90),
                category=MilestoneCategory.VENUE,
                completed=True
            ),
            PlanningMilestone(
                id="ms_dm02",
                phase=MilestonePhase.T_MINUS_1_MONTH,
                title="25 Artisan Stall Allotments & Zero-Plastic Guidelines",
                description="Screen community craft applications and mandate 100% biodegradable leaf plates.",
                due_date=get_backwards_date(event_date, 30),
                category=MilestoneCategory.LOGISTICS,
                completed=True
            ),
            PlanningMilestone(
                id="ms_dm03",
                phase=MilestonePhase.T_MINUS_2_WEEKS,
                title="Bulk Marigold Order & 500 Terracotta Diyas Procurement",
                description="Procure organic local marigolds from wholesale mandi and tested safe earthen diyas.",
                due_date=get_backwards_date(event_date, 14),
                category=MilestoneCategory.DECOR,
                completed=False
            ),
            PlanningMilestone(
                id="ms_dm04",
                phase=MilestonePhase.T_MINUS_1_WEEK,
                title="Emergency Fire Safety Inspection & DG Load Test",
                description="Audit 6x ABC fire safety points, paramedic first aid kit, and silent DG line stability.",
                due_date=get_backwards_date(event_date, 7),
                category=MilestoneCategory.LOGISTICS,
                completed=False
            ),
            PlanningMilestone(
                id="ms_dm05",
                phase=MilestonePhase.DAY_OF,
                title="Puneri Dhol Tasha Procession & Courtyard Diya Lighting",
                description="Grand evening opening ceremony, cultural dance competition, and green clean-up handover.",
                due_date=event_date,
                category=MilestoneCategory.RITUALS,
                completed=False
            ),
        ],
        vendor_checklist=[
            VendorChecklistItem(
                id="vc_dm01",
                category="Cultural Entertainment",
                vendor_name="Swargandhar Dhol Tasha Troupe Pune",
                estimated_cost=20000.0,
                status=VendorStatus.PAID,
                notes="15 drummers booked for 16:00 grand entrance. Full payment cleared.",
                google_maps_place_id="ChIJ_pune_swargandhar"
            ),
            VendorChecklistItem(
                id="vc_dm02",
                category="Zero-Waste Management",
                vendor_name="GreenEarth Composting & Waste Solutions",
                estimated_cost=60000.0,
                status=VendorStatus.BOOKED,
                notes="Includes 10 dual-bin stations and 4 dedicated segregation marshals.",
                google_maps_place_id="ChIJ_pune_greenearth"
            ),
            VendorChecklistItem(
                id="vc_dm03",
                category="Stalls & Canopies",
                vendor_name="Sanskriti Bamboo & Tent Works",
                estimated_cost=95000.0,
                status=VendorStatus.QUOTED,
                notes="25 bamboo kiosk structures with fire-retardant cloth canopies.",
                google_maps_place_id="ChIJ_pune_sanskriti"
            ),
            VendorChecklistItem(
                id="vc_dm04",
                category="Power & Genset",
                vendor_name="Reliable Silent DG Power",
                estimated_cost=70000.0,
                status=VendorStatus.BOOKED,
                notes="100 kVA silent DG with cabling to all 25 artisan stalls.",
                google_maps_place_id="ChIJ_pune_reliable_dg"
            ),
            VendorChecklistItem(
                id="vc_dm05",
                category="First Aid & Safety",
                vendor_name="LifeLine Paramedic Services",
                estimated_cost=45000.0,
                status=VendorStatus.BOOKED,
                notes="On-site paramedic booth with basic trauma and burn kit.",
                google_maps_place_id="ChIJ_pune_lifeline"
            ),
        ]
    )


def create_baseline_wedding_plan(
    headcount: int = 450,
    city: str = "Jaipur",
    budget: float = 3500000.0,
    event_type: str = "wedding"
) -> MasterEventPlan:
    """Default baseline plan calibrated to user constraints."""
    base = create_preset_meadow_wedding()
    base.location_city = city
    base.title = f"Destination {event_type.capitalize()} ({headcount} Guests)"
    base.total_budget_limit = budget
    base.schedule.insert(2, ScheduleBlock(
        block_id="sch_baraat_proc",
        phase="Procession (Baraat)",
        start_time_iso="18:00",
        end_time_iso="19:00",
        activity="Arrival procession with brass band and royal dhol beats",
        responsible_party="Procession Marshal",
        is_outdoor=True
    ))
    return base


async def deconstruct_moodboard(
    image_base64: Optional[str] = None,
    moodboard_preset: Optional[str] = None,
    headcount: int = 400,
    locality: str = "Pune",
    budget_ceiling: float = 1500000.0,
    event_type: str = "wedding"
) -> MasterEventPlan:
    """
    Multimodal Gemini 2.5 Flash agent:
    Parses visual moodboard styling cues (trusses, floral density, lighting, seating)
    and strictly maps them into a MasterEventPlan with categorized BOQ, backwards planning roadmap, and vendor checklist.
    """
    # 1. Check for explicit instant one-click demo presets
    if moodboard_preset == "meadow_wedding" or (event_type == "wedding" and not image_base64 and budget_ceiling <= 1500000):
        return create_preset_meadow_wedding()
    elif moodboard_preset == "cyber_birthday" or (event_type == "birthday" and not image_base64):
        return create_preset_cyberpunk_birthday()
    elif moodboard_preset == "diwali_mela" or (event_type == "community_festival" and not image_base64):
        return create_preset_diwali_mela()

    # 2. Multimodal Gemini 2.5 Flash if API key is configured
    api_key = settings.GEMINI_API_KEY
    if api_key and genai:
        try:
            client = genai.Client(api_key=api_key)
            prompt = f"""
            You are Aura Deconstruct Agent, an expert multimodal event architect and cost engineer.
            Deconstruct the provided mood board image for a high-end {event_type} in {locality} for {headcount} guests.
            Budget Ceiling: INR {budget_ceiling:,.2f}.

            Task:
            1. Extract visual elements: structural staging/trusses, lighting fixtures, botanical density, seating, audio-visual.
            2. Categorize every item into exact Priority Tiers:
               - "Critical": core safety, legal infrastructure, primary power, primary food.
               - "Operational": standard sound, stage lighting, guest comfort seating.
               - "Discretionary": exotic imported florals, cold spark SFX, luxury photo booths.
            3. Produce a complete Bill of Quantities (BOQ) with realistic rates in INR, units, specifications, and total costs.
            4. Formulate a 5-6 block chronological run-of-show schedule marking is_outdoor=True/False for each block.
            5. Generate 4-6 PlanningMilestones backwards from the event date (T-6 Months, T-3 Months, T-1 Month, T-2 Weeks, T-1 Week, Day-Of).
            6. Generate 4-5 VendorChecklistItems with realistic statuses (To Contact, Quoted, Booked, Paid).
            Ensure current_estimated_total equals the exact sum of total_cost_inr across all boq items.
            """
            contents = [prompt]
            if image_base64:
                clean_b64 = image_base64.split(",")[-1] if "," in image_base64 else image_base64
                image_bytes = base64.b64decode(clean_b64)
                contents.append(
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
                )

            response = client.models.generate_content(
                model=settings.GEMINI_FLASH_MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=MasterEventPlan,
                    temperature=0.2
                )
            )
            parsed_json = json.loads(response.text)
            return MasterEventPlan.model_validate(parsed_json)
        except Exception:
            pass

    # 3. Fallback based on event_type selection
    if event_type == "birthday":
        return create_preset_cyberpunk_birthday()
    elif event_type == "community_festival":
        return create_preset_diwali_mela()
    else:
        return create_preset_meadow_wedding()
