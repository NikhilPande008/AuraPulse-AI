from enum import Enum
from datetime import datetime, date
from typing import List, Optional, Annotated, Literal, Dict, Any, Union
from pydantic import BaseModel, Field, ConfigDict, BeforeValidator, model_validator, field_validator


class PriorityTier(str, Enum):
    CRITICAL = "Critical"          # Core infrastructure, food, permits
    OPERATIONAL = "Operational"    # Enhanced audio, secondary transport
    DISCRETIONARY = "Discretionary"# Specialized flowers, premium props


def _parse_priority_tier(v):
    return PriorityTier(v) if isinstance(v, str) else v


PriorityTierType = Annotated[PriorityTier, BeforeValidator(_parse_priority_tier)]


class BOQItem(BaseModel):
    model_config = ConfigDict(strict=True)

    item_id: str = Field(description="Unique UUID for state diffing")
    category: str = Field(description="E.g., Floral, Lighting, Structure, Catering")
    name: str = Field(description="Normalized procurement item name")
    specification: str = Field(default="", description="Technical or material detail")
    quantity: float = Field(description="Numerical quantity")
    unit: str = Field(default="lot", description="Measurement unit (e.g. sq ft, units, kg, sets)")
    estimated_rate_inr: float = Field(default=0.0, description="Estimated rate per unit in INR")
    total_cost_inr: float = Field(default=0.0, description="Total cost calculated as quantity * rate in INR")
    rate: float = Field(default=0.0, description="Rate per unit in INR (synonym for estimated_rate_inr)")
    total_cost: float = Field(default=0.0, description="Total cost in INR (synonym for total_cost_inr)")
    priority: PriorityTierType = Field(default=PriorityTier.OPERATIONAL, description="Necessity tier: Critical, Operational, Discretionary")
    priority_tier: PriorityTierType = Field(default=PriorityTier.OPERATIONAL, description="Synonym for priority")
    status: str = Field(default="ACTIVE", description="State: ACTIVE, MODIFIED, DROPPED")

    @model_validator(mode="before")
    @classmethod
    def sync_boq_fields(cls, values: Any) -> Any:
        if isinstance(values, dict):
            # Priority / priority_tier sync
            p = values.get("priority") or values.get("priority_tier")
            if p is not None:
                values["priority"] = p
                values["priority_tier"] = p

            # Rate / estimated_rate_inr sync
            r = values.get("rate") if values.get("rate") is not None else values.get("estimated_rate_inr")
            if r is not None and not isinstance(r, str):
                values["rate"] = float(r)
                values["estimated_rate_inr"] = float(r)

            # Total cost / total_cost_inr sync
            tc = values.get("total_cost") if values.get("total_cost") is not None else values.get("total_cost_inr")
            if tc is not None and not isinstance(tc, str):
                values["total_cost"] = float(tc)
                values["total_cost_inr"] = float(tc)
            elif r is not None and values.get("quantity") is not None and not isinstance(values.get("quantity"), str):
                try:
                    computed = round(float(values["quantity"]) * float(r), 2)
                    values["total_cost"] = computed
                    values["total_cost_inr"] = computed
                except (ValueError, TypeError):
                    pass
        return values


class ScheduleBlock(BaseModel):
    model_config = ConfigDict(strict=True)

    block_id: str = Field(description="Unique UUID for schedule block")
    phase: str = Field(description="Event phase e.g. Setup, Arrival, Main Event, Reception, Teardown")
    start_time_iso: str = Field(description="ISO 8601 or HH:MM start timestamp")
    end_time_iso: str = Field(description="ISO 8601 or HH:MM end timestamp")
    activity: str = Field(description="Description of activity")
    responsible_party: str = Field(description="Assigned vendor or team lead")
    is_outdoor: bool = Field(description="Whether activity is in an outdoor zone vulnerable to weather")


class MilestonePhase(str, Enum):
    DO_IMMEDIATELY = "Do Immediately"
    T_MINUS_6_MONTHS = "T-6 Months"
    T_MINUS_3_MONTHS = "T-3 Months"
    T_MINUS_1_MONTH = "T-1 Month"
    T_MINUS_2_WEEKS = "T-2 Weeks"
    T_MINUS_1_WEEK = "T-1 Week"
    DAY_OF = "Day-Of"


def _parse_milestone_phase(v):
    return MilestonePhase(v) if isinstance(v, str) else v


MilestonePhaseType = Annotated[MilestonePhase, BeforeValidator(_parse_milestone_phase)]


class MilestoneCategory(str, Enum):
    VENUE = "Venue"
    CATERING = "Catering"
    DECOR = "Decor"
    ATTIRE_INVITES = "Attire & Invites"
    LOGISTICS = "Logistics"
    RITUALS = "Rituals"


def _parse_milestone_category(v):
    return MilestoneCategory(v) if isinstance(v, str) else v


MilestoneCategoryType = Annotated[MilestoneCategory, BeforeValidator(_parse_milestone_category)]


class PlanningMilestone(BaseModel):
    model_config = ConfigDict(strict=True)

    id: str = Field(description="Unique UUID for planning milestone")
    phase: MilestonePhaseType = Field(description="Planning horizon phase e.g. T-6 Months or Do Immediately")
    title: str = Field(description="Milestone title e.g. Lock Banquet Venue")
    description: str = Field(description="Key deliverable details")
    due_date: str = Field(description="Target deadline (YYYY-MM-DD)")
    category: MilestoneCategoryType = Field(description="Category domain")
    completed: bool = Field(default=False, description="Milestone completion check")


class VendorStatus(str, Enum):
    TO_CONTACT = "To Contact"
    QUOTED = "Quoted"
    BOOKED = "Booked"
    PAID = "Paid"


def _parse_vendor_status(v):
    return VendorStatus(v) if isinstance(v, str) else v


VendorStatusType = Annotated[VendorStatus, BeforeValidator(_parse_vendor_status)]


class VendorChecklistItem(BaseModel):
    model_config = ConfigDict(strict=True)

    id: str = Field(description="Unique UUID for vendor checklist entry")
    category: str = Field(description="Service category e.g. Catering & Banquet")
    vendor_name: str = Field(description="Company or contractor name")
    estimated_cost: float = Field(description="Estimated contracted cost in INR")
    status: VendorStatusType = Field(default=VendorStatus.TO_CONTACT, description="Workflow stage")
    notes: str = Field(default="", description="Operational notes or quote terms")
    google_maps_place_id: Optional[str] = Field(default=None, description="Linked Google Maps entity")


class EventIdea(BaseModel):
    model_config = ConfigDict(strict=False)

    title: str = Field(description="Idea concept title")
    rationale: str = Field(description="Why this fits the theme, culture, and budget")
    estimated_cost: float = Field(default=0.0, description="Estimated cost in INR")


class MasterEventPlan(BaseModel):
    model_config = ConfigDict(strict=True)

    event_id: str = Field(description="Unique UUID for the overall event")
    event_type: str = Field(description="wedding, birthday, community_event, community_festival")
    title: str = Field(description="High-level event title")
    location_city: str = Field(description="Geographical locality e.g. Mumbai, Bangalore, Delhi")
    currency: str = Field(default="INR", description="Currency code")
    total_budget_limit: float = Field(description="Maximum authorized spending ceiling in currency")
    current_estimated_total: float = Field(description="Sum of all ACTIVE and MODIFIED line items")
    headcount: Optional[int] = Field(default=None, description="Expected guest headcount (pax)")
    event_date: Optional[str] = Field(default=None, description="Event date (YYYY-MM-DD)")
    culture_region: Optional[str] = Field(default=None, description="Cultural context e.g. Maharashtrian, Marwari")
    theme: Optional[str] = Field(default=None, description="Aesthetic theme e.g. Royal Heritage, Cyberpunk")
    ideas: List[EventIdea] = Field(default_factory=list, description="Curated ideas list")
    boq: List[BOQItem] = Field(description="Full Bill of Quantities itemization")
    schedule: List[ScheduleBlock] = Field(description="Sequential timeline and run-of-show")
    planning_milestones: List[PlanningMilestone] = Field(default_factory=list, description="Backwards roadmap from T-6 Months to Day-Of")
    vendor_checklist: List[VendorChecklistItem] = Field(default_factory=list, description="Interactive procurement & vendor status tracker")


DietaryType = Literal["veg", "jain", "vegan", "non_veg", "halal", "no_onion_garlic"]
AccessibilityType = Literal["wheelchair", "elderly", "hearing", "visual", "kids_safe"]


class PlanRequest(BaseModel):
    event_type: Literal["wedding", "birthday", "community_event", "community_festival"] = "wedding"
    event_date: Optional[str] = None
    city: str = Field(min_length=2, max_length=80)
    headcount: int = Field(ge=1, le=10000)
    budget: float = Field(gt=0, le=50000000)
    culture_region: Optional[str] = Field(default=None, max_length=80)
    theme: Optional[str] = Field(default=None, max_length=80)
    dietary: List[DietaryType] = Field(default_factory=list, max_length=6)
    accessibility: List[AccessibilityType] = Field(default_factory=list, max_length=5)
    notes: Optional[str] = Field(default=None, max_length=1000)
    language: Literal["en", "hi", "mr"] = "en"
    image_base64: Optional[str] = Field(default=None, max_length=6000000)
    moodboard_preset: Optional[str] = Field(default=None, max_length=80)

    @field_validator("event_date")
    @classmethod
    def validate_future_date(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            try:
                parsed = datetime.strptime(v, "%Y-%m-%d").date()
            except Exception:
                raise ValueError("event_date must be in YYYY-MM-DD format")
            if parsed <= date.today():
                raise ValueError("event_date must be in the future")
        return v

    @model_validator(mode="before")
    @classmethod
    def handle_legacy_fields(cls, values: Any) -> Any:
        if isinstance(values, dict):
            # Accept locality as city alias
            if "city" not in values and "locality" in values:
                values["city"] = values["locality"]
            # Accept budget_ceiling as budget alias
            if "budget" not in values and "budget_ceiling" in values:
                values["budget"] = values["budget_ceiling"]
        return values


# Alias DeconstructRequest to PlanRequest for backwards compatibility
DeconstructRequest = PlanRequest
