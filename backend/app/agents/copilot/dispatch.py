"""Copilot tool dispatch registry and typed argument validation."""

from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, Field

from backend.app.agents.copilot.tools import (
    execute_add_item,
    execute_change_headcount,
    execute_decline_off_topic,
    execute_remove_item,
    execute_scale_budget,
    execute_set_event_date,
    execute_set_headcount,
    execute_update_item,
)
from backend.app.schemas.contingency import ContingencyDiff
from backend.app.schemas.event_plan import MasterEventPlan


class ScaleBudgetArgs(BaseModel):
    percentage: float = Field(default=-20.0, ge=-90.0, le=100.0)

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "ScaleBudgetArgs":
        val = raw.get("percentage")
        if val is None:
            val = raw.get("pct", -20.0)
        return cls(percentage=float(val))


class AddItemArgs(BaseModel):
    category: str = "General"
    name: str = "New Item"
    specification: str = "Added via Co-Pilot"
    quantity: float = Field(default=1.0, gt=0.0)
    unit: str = "lot"
    rate_inr: float = Field(default=10000.0, ge=0.0)
    priority: str = "Operational"

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "AddItemArgs":
        rate = raw.get("rate_inr")
        if rate is None:
            rate = raw.get("cost") or raw.get("rate") or 10000.0
        return cls(
            category=str(raw.get("category", "General")),
            name=str(raw.get("name", "New Item")),
            specification=str(raw.get("specification", "Added via Co-Pilot")),
            quantity=float(raw.get("quantity") or 1.0),
            unit=str(raw.get("unit", "lot")),
            rate_inr=float(rate),
            priority=str(raw.get("priority", "Operational")),
        )


class RemoveItemArgs(BaseModel):
    item_id: str

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "RemoveItemArgs":
        return cls(item_id=str(raw.get("item_id", "")))


class UpdateItemArgs(BaseModel):
    item_id: str
    quantity: float | None = None
    rate_inr: float | None = None
    name: str | None = None

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "UpdateItemArgs":
        qty = raw.get("quantity")
        rate = raw.get("rate_inr")
        name = raw.get("name")
        return cls(
            item_id=str(raw.get("item_id", "")),
            quantity=float(qty) if qty is not None else None,
            rate_inr=float(rate) if rate is not None else None,
            name=str(name) if name is not None else None,
        )


class SetEventDateArgs(BaseModel):
    new_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "SetEventDateArgs":
        return cls(new_date=str(raw.get("new_date", "")))


class SetHeadcountArgs(BaseModel):
    new_total: int = Field(default=100, ge=1, le=10000)

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "SetHeadcountArgs":
        cnt = raw.get("new_total") or raw.get("count") or raw.get("headcount") or 100
        return cls(new_total=int(cnt))


class ChangeHeadcountArgs(BaseModel):
    delta: int = 0

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "ChangeHeadcountArgs":
        return cls(delta=int(raw.get("delta", 0)))


class DeclineOffTopicArgs(BaseModel):
    reason: str = "Query is off-topic."

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "DeclineOffTopicArgs":
        return cls(reason=str(raw.get("reason", "Query is off-topic.")))


# Tool Handler Signature: (plan, raw_args) -> (plan, diff, reply, is_declined)
ToolHandler = Callable[[MasterEventPlan, dict[str, Any]], tuple[MasterEventPlan, ContingencyDiff | None, str, bool]]


def _handle_scale_budget(
    plan: MasterEventPlan, raw: dict[str, Any]
) -> tuple[MasterEventPlan, ContingencyDiff | None, str, bool]:
    args = ScaleBudgetArgs.from_raw(raw)
    p, d = execute_scale_budget(plan, args.percentage)
    return p, d, f"Scaled budget by {args.percentage}%.", False


def _handle_add_item(
    plan: MasterEventPlan, raw: dict[str, Any]
) -> tuple[MasterEventPlan, ContingencyDiff | None, str, bool]:
    args = AddItemArgs.from_raw(raw)
    p, d = execute_add_item(
        plan,
        category=args.category,
        name=args.name,
        specification=args.specification,
        quantity=args.quantity,
        unit=args.unit,
        rate_inr=args.rate_inr,
        priority=args.priority,
    )
    return p, d, f"Added {args.name} to BOQ.", False


def _handle_remove_item(
    plan: MasterEventPlan, raw: dict[str, Any]
) -> tuple[MasterEventPlan, ContingencyDiff | None, str, bool]:
    args = RemoveItemArgs.from_raw(raw)
    p, d = execute_remove_item(plan, args.item_id)
    return p, d, f"Removed item {args.item_id}.", False


def _handle_update_item(
    plan: MasterEventPlan, raw: dict[str, Any]
) -> tuple[MasterEventPlan, ContingencyDiff | None, str, bool]:
    args = UpdateItemArgs.from_raw(raw)
    p, d = execute_update_item(
        plan, item_id=args.item_id, quantity=args.quantity, rate_inr=args.rate_inr, name=args.name
    )
    return p, d, f"Updated item {args.item_id}.", False


def _handle_set_event_date(
    plan: MasterEventPlan, raw: dict[str, Any]
) -> tuple[MasterEventPlan, ContingencyDiff | None, str, bool]:
    args = SetEventDateArgs.from_raw(raw)
    p = execute_set_event_date(plan, args.new_date)
    return p, None, f"Set event date to {args.new_date}.", False


def _handle_set_headcount(
    plan: MasterEventPlan, raw: dict[str, Any]
) -> tuple[MasterEventPlan, ContingencyDiff | None, str, bool]:
    args = SetHeadcountArgs.from_raw(raw)
    p, d = execute_set_headcount(plan, args.new_total)
    return p, d, f"Set headcount to {args.new_total}.", False


def _handle_change_headcount(
    plan: MasterEventPlan, raw: dict[str, Any]
) -> tuple[MasterEventPlan, ContingencyDiff | None, str, bool]:
    args = ChangeHeadcountArgs.from_raw(raw)
    p, d = execute_change_headcount(plan, args.delta)
    return p, d, f"Changed headcount by {args.delta}.", False


def _handle_decline_off_topic(
    plan: MasterEventPlan, raw: dict[str, Any]
) -> tuple[MasterEventPlan, ContingencyDiff | None, str, bool]:
    args = DeclineOffTopicArgs.from_raw(raw)
    reply = execute_decline_off_topic(args.reason)
    return plan, None, reply, True


TOOL_REGISTRY: dict[str, ToolHandler] = {
    "scale_budget": _handle_scale_budget,
    "add_item": _handle_add_item,
    "remove_item": _handle_remove_item,
    "update_item": _handle_update_item,
    "set_event_date": _handle_set_event_date,
    "set_headcount": _handle_set_headcount,
    "change_headcount": _handle_change_headcount,
    "decline_off_topic": _handle_decline_off_topic,
}


def apply_tool_call(
    plan: MasterEventPlan, tool_name: str, args: dict[str, Any]
) -> tuple[MasterEventPlan, ContingencyDiff | None, str]:
    """Executes a copilot tool via TOOL_REGISTRY lookup."""
    handler = TOOL_REGISTRY.get(tool_name)
    if not handler:
        return plan, None, f"Unknown tool '{tool_name}'."
    try:
        p, d, r, _ = handler(plan, args)
        return p, d, r
    except Exception as e:  # noqa: BLE001
        return plan, None, f"Error executing tool '{tool_name}': {e}"
