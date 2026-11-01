"""Intent handler registry for offline deterministic conversational planning."""

from .handlers import (
    BudgetScaleIntentHandler,
    CateringIntentHandler,
    DateMoveIntentHandler,
    DeclineIntentHandler,
    DefaultIntentHandler,
    FloralSaxIntentHandler,
    GamesIntentHandler,
    HeadcountIntentHandler,
    IntentHandler,
    RitualIntentHandler,
)

INTENT_HANDLERS: list[IntentHandler] = [
    DeclineIntentHandler(),
    DateMoveIntentHandler(),
    BudgetScaleIntentHandler(),
    HeadcountIntentHandler(),
    CateringIntentHandler(),
    FloralSaxIntentHandler(),
    GamesIntentHandler(),
    RitualIntentHandler(),
    DefaultIntentHandler(),
]

__all__ = [
    "INTENT_HANDLERS",
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
