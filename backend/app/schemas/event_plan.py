from enum import Enum
from typing import List, Optional, Annotated, Literal
from pydantic import BaseModel, Field, ConfigDict, BeforeValidator


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
    specification: str = Field(description="Technical or material detail")
    quantity: float = Field(description="Numerical quantity")
    unit: str = Field(description="Measurement unit (e.g. sq ft, units, kg, sets)")
    estimated_rate_inr: float = Field(description="Estimated rate per unit in INR")
    total_cost_inr: float = Field(description="Total cost calculated as quantity * rate in INR")
    priority: PriorityTierType = Field(description="Necessity tier: Critical, Operational, Discretionary")
    status: str = Field(default="ACTIVE", description="State: ACTIVE, MODIFIED, DROPPED")


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
    phase: MilestonePhaseType = Field(description="Planning horizon phase e.g. T-6 Months")
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


class MasterEventPlan(BaseModel):
    model_config = ConfigDict(strict=True)

    event_id: str = Field(description="Unique UUID for the overall event")
    event_type: str = Field(description="wedding, birthday, community_festival, corporate_gala")
    title: str = Field(description="High-level event title")
    location_city: str = Field(description="Geographical locality e.g. Mumbai, Bangalore, Delhi")
    currency: str = Field(default="INR", description="Currency code")
    total_budget_limit: float = Field(description="Maximum authorized spending ceiling in currency")
    current_estimated_total: float = Field(description="Sum of all ACTIVE and MODIFIED line items")
    boq: List[BOQItem] = Field(description="Full Bill of Quantities itemization")
    schedule: List[ScheduleBlock] = Field(description="Sequential timeline and run-of-show")
    planning_milestones: List[PlanningMilestone] = Field(default_factory=list, description="Backwards roadmap from T-6 Months to Day-Of")
    vendor_checklist: List[VendorChecklistItem] = Field(default_factory=list, description="Interactive procurement & vendor status tracker")
