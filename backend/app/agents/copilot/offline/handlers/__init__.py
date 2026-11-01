"""Intent handlers for offline deterministic copilot operations."""

from backend.app.agents.copilot.offline.handlers.base import IntentHandler
from backend.app.agents.copilot.offline.handlers.budget import BudgetScaleIntentHandler
from backend.app.agents.copilot.offline.handlers.catering import CateringIntentHandler
from backend.app.agents.copilot.offline.handlers.date_move import DateMoveIntentHandler
from backend.app.agents.copilot.offline.handlers.decline import DeclineIntentHandler
from backend.app.agents.copilot.offline.handlers.default import DefaultIntentHandler
from backend.app.agents.copilot.offline.handlers.floral_sax import FloralSaxIntentHandler
from backend.app.agents.copilot.offline.handlers.games import GamesIntentHandler
from backend.app.agents.copilot.offline.handlers.headcount import HeadcountIntentHandler
from backend.app.agents.copilot.offline.handlers.rituals import RitualIntentHandler

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
