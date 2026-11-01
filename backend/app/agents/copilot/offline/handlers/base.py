from abc import ABC, abstractmethod

from .....schemas.event_plan import MasterEventPlan
from ...models import CopilotResult


class IntentHandler(ABC):
    """Abstract base class for deterministic intent handling."""

    @abstractmethod
    def matches(self, prompt: str) -> bool:
        """Determines if the prompt matches this intent."""

    @abstractmethod
    def apply(self, plan: MasterEventPlan, prompt: str, lang: str) -> CopilotResult:
        """Applies modifications and returns a typed CopilotResult."""
