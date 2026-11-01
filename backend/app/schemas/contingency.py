from enum import Enum
from typing import Annotated, List, Optional

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

from .event_plan import BOQItem, MasterEventPlan, ScheduleBlock


class CrisisTriggerType(str, Enum):
    WEATHER_RISK = "WEATHER_RISK"
    BUDGET_COMPRESSION = "BUDGET_COMPRESSION"
    SUPPLY_FAILURE = "SUPPLY_FAILURE"
    TIMELINE_SLIPPAGE = "TIMELINE_SLIPPAGE"


def _parse_trigger_type(v):
    return CrisisTriggerType(v) if isinstance(v, str) else v


CrisisTriggerTypeModel = Annotated[CrisisTriggerType, BeforeValidator(_parse_trigger_type)]


class CrisisTrigger(BaseModel):
    model_config = ConfigDict(strict=True)

    trigger_type: CrisisTriggerTypeModel = Field(description="Category of crisis trigger")
    description: str = Field(description="Human readable description of the triggering event")
    budget_cut_percent: Optional[float] = Field(default=None, description="Percentage budget cut (e.g. 20.0 for 20%)")
    weather_condition: Optional[str] = Field(default=None, description="e.g. Rain Downpour, Windstorm, Heatwave")
    delay_minutes: Optional[int] = Field(default=None, description="Minutes delayed for timeline slippage")
    affected_vendor_category: Optional[str] = Field(default=None, description="Category of vendor cancelled e.g. Catering, Sound")


class DiffAction(str, Enum):
    ADDED = "ADDED"
    MODIFIED = "MODIFIED"
    REMOVED = "REMOVED"
    UNCHANGED = "UNCHANGED"


def _parse_diff_action(v):
    return DiffAction(v) if isinstance(v, str) else v


DiffActionModel = Annotated[DiffAction, BeforeValidator(_parse_diff_action)]


class BOQDiffItem(BaseModel):
    model_config = ConfigDict(strict=True)

    item_id: str
    action: DiffActionModel
    original_item: Optional[BOQItem] = None
    updated_item: Optional[BOQItem] = None
    reason: str = Field(description="Gemini reasoning for why this line item was added, trimmed, or adjusted")


class ScheduleDiffItem(BaseModel):
    model_config = ConfigDict(strict=True)

    block_id: str
    action: DiffActionModel
    original_block: Optional[ScheduleBlock] = None
    updated_block: Optional[ScheduleBlock] = None
    reason: str = Field(description="Reason for schedule adjustment or indoor reassignment")


class ContingencyDiff(BaseModel):
    model_config = ConfigDict(strict=True)

    diff_id: str
    trigger: CrisisTrigger
    timestamp_iso: str
    summary_narrative: str = Field(description="Deterministic + Gemini multi-turn reasoning explaining the rebalance")
    original_total_inr: float
    new_total_inr: float
    budget_delta_inr: float
    boq_diffs: List[BOQDiffItem]
    schedule_diffs: List[ScheduleDiffItem]
    updated_plan: MasterEventPlan
    actionable_mitigations: List[str]


class SimulationRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    plan: MasterEventPlan
    trigger: CrisisTrigger
