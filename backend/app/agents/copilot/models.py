"""Data models and response structures for the Co-Pilot agent."""

from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, Field

from ...schemas.contingency import ContingencyDiff
from ...schemas.event_plan import MasterEventPlan


@dataclass
class CopilotResult:
    """Internal result container returned by intent handlers and tool dispatches."""

    updated_plan: MasterEventPlan
    diff: ContingencyDiff | None
    reply: str
    suggested_ideas: list[str] = field(default_factory=list)
    declined: bool = False
    mode: str = "offline_rules"

    def to_dict(self) -> dict[str, Any]:
        """Converts result to dictionary matching legacy wire format."""
        return {
            "copilot_reply": self.reply,
            "updated_plan": self.updated_plan,
            "suggested_ideas": self.suggested_ideas,
            "diff": self.diff.model_dump() if self.diff else None,
            "mode": self.mode,
            "declined": self.declined,
        }


class CopilotResponse(BaseModel):
    """Pydantic response model for the chat-copilot endpoint."""

    copilot_reply: str
    updated_plan: MasterEventPlan
    suggested_ideas: list[str] = Field(default_factory=list)
    diff: dict[str, Any] | None = None
    mode: str = "offline_rules"
    declined: bool = False
