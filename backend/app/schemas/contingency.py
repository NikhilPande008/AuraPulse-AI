"""Pydantic schemas and types for crisis simulation and contingency diffs."""

from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

from .event_plan import BOQItem, MasterEventPlan, ScheduleBlock


class CrisisTriggerType(StrEnum):
    WEATHER_RISK = "WEATHER_RISK"
    BUDGET_COMPRESSION = "BUDGET_COMPRESSION"
    SUPPLY_FAILURE = "SUPPLY_FAILURE"
    TIMELINE_SLIPPAGE = "TIMELINE_SLIPPAGE"


def _parse_trigger_type(v: object) -> object:
    return CrisisTriggerType(v) if isinstance(v, str) else v


CrisisTriggerTypeModel = Annotated[CrisisTriggerType, BeforeValidator(_parse_trigger_type)]


class CrisisTrigger(BaseModel):
    model_config = ConfigDict(strict=True)

    trigger_type: CrisisTriggerTypeModel = Field(description="Category of crisis trigger")
    description: str = Field(description="Human readable description of the triggering event")
    budget_cut_percent: float | None = Field(default=None, description="Percentage budget cut (e.g. 20.0 for 20%)")
    weather_condition: str | None = Field(default=None, description="e.g. Rain Downpour, Windstorm, Heatwave")
    delay_minutes: int | None = Field(default=None, description="Minutes delayed for timeline slippage")
    affected_vendor_category: str | None = Field(
        default=None, description="Category of vendor cancelled e.g. Catering, Sound"
    )


class DiffAction(StrEnum):
    ADDED = "ADDED"
    MODIFIED = "MODIFIED"
    REMOVED = "REMOVED"
    UNCHANGED = "UNCHANGED"


def _parse_diff_action(v: object) -> object:
    return DiffAction(v) if isinstance(v, str) else v


DiffActionModel = Annotated[DiffAction, BeforeValidator(_parse_diff_action)]


class BOQDiffItem(BaseModel):
    model_config = ConfigDict(strict=True)

    item_id: str
    action: DiffActionModel
    original_item: BOQItem | None = None
    updated_item: BOQItem | None = None
    reason: str = Field(description="Gemini reasoning for why this line item was added, trimmed, or adjusted")


class ScheduleDiffItem(BaseModel):
    model_config = ConfigDict(strict=True)

    block_id: str
    action: DiffActionModel
    original_block: ScheduleBlock | None = None
    updated_block: ScheduleBlock | None = None
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
    boq_diffs: list[BOQDiffItem]
    schedule_diffs: list[ScheduleDiffItem]
    updated_plan: MasterEventPlan
    actionable_mitigations: list[str]


class SimulationRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    plan: MasterEventPlan
    trigger: CrisisTrigger
