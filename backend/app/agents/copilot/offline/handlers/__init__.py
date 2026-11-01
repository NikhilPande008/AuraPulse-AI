"""Intent handlers for offline deterministic copilot operations."""

from .base import IntentHandler
from .budget import BudgetScaleIntentHandler
from .catering import CateringIntentHandler
from .date_move import DateMoveIntentHandler
from .decline import DeclineIntentHandler
from .default import DefaultIntentHandler
from .floral_sax import FloralSaxIntentHandler
from .games import GamesIntentHandler
from .headcount import HeadcountIntentHandler
from .rituals import RitualIntentHandler

__all__ = [
    "BudgetScaleIntentHandler",
    "CateringIntentHandler",
    "DateMoveIntentHandler",
    "DeclineIntentHandler",
    "DefaultIntentHandler",
    "FloralSaxIntentHandler",
    "GamesIntentHandler",
    "HeadcountIntentHandler",
    "IntentHandler",
    "RitualIntentHandler",
]
