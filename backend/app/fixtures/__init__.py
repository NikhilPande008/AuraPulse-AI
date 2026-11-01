"""Fixtures package for sample event plans and test assets."""

from typing import Protocol

from ..schemas import MasterEventPlan, ScheduleBlock
from .cyber_birthday import create_preset_cyberpunk_birthday
from .diwali_mela import create_preset_diwali_mela
from .meadow_wedding import create_preset_meadow_wedding


class PresetBuilder(Protocol):
    def __call__(self, event_date: str | None = ...) -> MasterEventPlan: ...


def create_baseline_wedding_plan(
    headcount: int = 450, city: str = "Jaipur", budget: float = 3500000.0, event_type: str = "wedding"
) -> MasterEventPlan:
    """Default baseline plan calibrated to user constraints."""
    base = create_preset_meadow_wedding()
    base.headcount = headcount
    base.location_city = city
    base.title = f"Destination {event_type.capitalize()} ({headcount} Guests)"
    base.total_budget_limit = budget
    base.schedule.insert(
        2,
        ScheduleBlock(
            block_id="sch_baraat_proc",
            phase="Procession (Baraat)",
            start_time_iso="18:00",
            end_time_iso="19:00",
            activity="Arrival procession with brass band and royal dhol beats",
            responsible_party="Procession Marshal",
            is_outdoor=True,
        ),
    )
    return base


SAMPLE_PRESETS: dict[str, PresetBuilder] = {
    "meadow_wedding": create_preset_meadow_wedding,
    "cyber_birthday": create_preset_cyberpunk_birthday,
    "diwali_mela": create_preset_diwali_mela,
}

__all__ = [
    "SAMPLE_PRESETS",
    "create_baseline_wedding_plan",
    "create_preset_cyberpunk_birthday",
    "create_preset_diwali_mela",
    "create_preset_meadow_wedding",
]
