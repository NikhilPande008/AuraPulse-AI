"""Sample preset event plans for deterministic offline demonstrations and tests.

This module re-exports sample plans from backend.app.fixtures for backward compatibility.
"""

from . import (
    SAMPLE_PRESETS,
    create_baseline_wedding_plan,
    create_preset_cyberpunk_birthday,
    create_preset_diwali_mela,
    create_preset_meadow_wedding,
)

__all__ = [
    "SAMPLE_PRESETS",
    "create_baseline_wedding_plan",
    "create_preset_cyberpunk_birthday",
    "create_preset_diwali_mela",
    "create_preset_meadow_wedding",
]
