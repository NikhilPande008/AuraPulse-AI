"""AuraPulse Co-Pilot package providing multi-turn conversational replanning and tools."""

from ...config import settings
from ...llm.client import generate
from .dispatch import TOOL_REGISTRY, apply_tool_call
from .models import CopilotResponse, CopilotResult
from .offline import (
    _execute_deterministic_copilot,
    _generate_suggested_ideas,
    run_offline,
)
from .offline.language import _detect_language, detect_language
from .service import chat_copilot
from .tools import (
    COPILOT_TOOLS,
    add_item,
    change_headcount,
    decline_off_topic,
    execute_add_item,
    execute_change_headcount,
    execute_decline_off_topic,
    execute_remove_item,
    execute_scale_budget,
    execute_set_event_date,
    execute_set_headcount,
    execute_update_item,
    remove_item,
    scale_budget,
    set_event_date,
    set_headcount,
    update_item,
)

__all__ = [
    "COPILOT_TOOLS",
    "TOOL_REGISTRY",
    "CopilotResponse",
    "CopilotResult",
    "_detect_language",
    "_execute_deterministic_copilot",
    "_generate_suggested_ideas",
    "add_item",
    "apply_tool_call",
    "change_headcount",
    "chat_copilot",
    "decline_off_topic",
    "detect_language",
    "execute_add_item",
    "execute_change_headcount",
    "execute_decline_off_topic",
    "execute_remove_item",
    "execute_scale_budget",
    "execute_set_event_date",
    "execute_set_headcount",
    "execute_update_item",
    "generate",
    "remove_item",
    "run_offline",
    "scale_budget",
    "set_event_date",
    "set_headcount",
    "settings",
    "update_item",
]
