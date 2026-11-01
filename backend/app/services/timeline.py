"""Timeline milestone calculation service for backwards event planning."""

import uuid
from datetime import date, datetime, timedelta
from typing import NamedTuple

from ..schemas import (
    MilestoneCategory,
    MilestonePhase,
    PlanningMilestone,
)


class PhaseConfig(NamedTuple):
    phase: MilestonePhase
    days: int


class MilestoneTemplate(NamedTuple):
    title: str
    description: str
    category: MilestoneCategory


PHASES_CONFIG: tuple[PhaseConfig, ...] = (
    PhaseConfig(MilestonePhase.T_MINUS_6_MONTHS, 180),
    PhaseConfig(MilestonePhase.T_MINUS_3_MONTHS, 90),
    PhaseConfig(MilestonePhase.T_MINUS_1_MONTH, 30),
    PhaseConfig(MilestonePhase.T_MINUS_2_WEEKS, 14),
    PhaseConfig(MilestonePhase.T_MINUS_1_WEEK, 7),
    PhaseConfig(MilestonePhase.DAY_OF, 0),
)

MILESTONE_TEMPLATES: dict[str, dict[int, MilestoneTemplate]] = {
    "wedding": {
        180: MilestoneTemplate(
            "Lock Banquet Venue & Wet Weather Backup",
            "Finalize contract with main wedding hall/lawn, verify backup banquet permissions.",
            MilestoneCategory.VENUE,
        ),
        90: MilestoneTemplate(
            "Menu Tasting & Caterer Selection",
            "Sample culinary spread, finalize live counter menus and dietary accommodations.",
            MilestoneCategory.CATERING,
        ),
        30: MilestoneTemplate(
            "Floral Stage & Mandap Mockup Sign-off",
            "Review 3D floral installations, lighting angles, and bride/groom stage elevations.",
            MilestoneCategory.DECOR,
        ),
        14: MilestoneTemplate(
            "RSVP Lock & Seating Chart Finalization",
            "Confirm exact guest count across all functions and distribute digital invitations.",
            MilestoneCategory.ATTIRE_INVITES,
        ),
        7: MilestoneTemplate(
            "Final Vendor Briefing & Rehearsal Walkthrough",
            "Align decorators, sound engineers, photographers and procession leads on run-of-show.",
            MilestoneCategory.LOGISTICS,
        ),
        0: MilestoneTemplate(
            "Ceremony Execution & Vendor Dispatch",
            "Orchestrate Baraat ingress, Mandap rituals, and dinner banquet coordination.",
            MilestoneCategory.LOGISTICS,
        ),
    },
    "birthday": {
        180: MilestoneTemplate(
            "Reserve Party Venue or Rooftop Lounge",
            "Secure venue deposit, confirm AV and DJ decibel restrictions.",
            MilestoneCategory.VENUE,
        ),
        90: MilestoneTemplate(
            "Book Entertainment, DJ & Theme Stylist",
            "Lock music artist, host / emcee, and thematic lighting setup.",
            MilestoneCategory.DECOR,
        ),
        30: MilestoneTemplate(
            "Custom Cake Tasting & Party Food Curation",
            "Design multi-tier celebration cake and lock finger food / mocktail counters.",
            MilestoneCategory.CATERING,
        ),
        14: MilestoneTemplate(
            "Dispatch Digital RSVPs & Party Favors Procurement",
            "Track guest confirmations and package personalized return gifts.",
            MilestoneCategory.ATTIRE_INVITES,
        ),
        7: MilestoneTemplate(
            "Game Master Briefing & Playlist Lock",
            "Finalize interactive group games, scorecards, and entry music cues.",
            MilestoneCategory.LOGISTICS,
        ),
        0: MilestoneTemplate(
            "Party Execution & Cake Cutting",
            "Host arrival, interactive games, live DJ set, and celebration finale.",
            MilestoneCategory.LOGISTICS,
        ),
    },
    "community_event": {
        180: MilestoneTemplate(
            "Secure Community Grounds & Municipal Ward Filings",
            "Book central plaza/grounds and initiate local ward authority permissions.",
            MilestoneCategory.VENUE,
        ),
        90: MilestoneTemplate(
            "Vendor Stall Allocations & Sponsor Partnerships",
            "Assign food, craft, and commercial stalls; lock green power / DG set vendors.",
            MilestoneCategory.CATERING,
        ),
        30: MilestoneTemplate(
            "Police, Sound & Fire Safety Clearances",
            "Obtain loud-speaker permits, fire safety certifications, and medical paramedic desk.",
            MilestoneCategory.LOGISTICS,
        ),
        14: MilestoneTemplate(
            "Publicity Campaign & Volunteer Coordination",
            "Deploy entry banners, print festival passes, and brief resident safety marshals.",
            MilestoneCategory.ATTIRE_INVITES,
        ),
        7: MilestoneTemplate(
            "Electrical Grounding, Sound Check & Ingress Drill",
            "Audit generator safety, stage line arrays, and emergency crowd flow lanes.",
            MilestoneCategory.LOGISTICS,
        ),
        0: MilestoneTemplate(
            "Festival Operations & Crowd Marshaling",
            "Manage stage performances, food zone hygiene, and safe crowd egress.",
            MilestoneCategory.LOGISTICS,
        ),
    },
}

MARATHI_WEDDING_OVERRIDES: dict[int, MilestoneTemplate] = {
    90: MilestoneTemplate(
        "Sakhar Puda Booking & Maharashtrian Menu Tasting",
        "Lock engagement / Sakhar Puda rituals and conduct Puran Poli & Modak tasting.",
        MilestoneCategory.RITUALS,
    ),
    7: MilestoneTemplate(
        "Muhurt Patrika & Samagri Audit",
        "Coordinate with Guruji, finalize muhurt timings, Antarpat, and ritual samagri.",
        MilestoneCategory.RITUALS,
    ),
}

MARATHI_KEYWORDS = ("marathi", "maharashtrian", "pune", "mumbai", "nashik")


def default_event_date(days_ahead: int = 90) -> str:
    """Return an ISO formatted date string for `days_ahead` days from today."""
    return (date.today() + timedelta(days=days_ahead)).isoformat()


def get_backwards_date(base_date_str: str, days_before: int) -> str:
    """Calculate milestone due dates backwards from an event date.

    Args:
        base_date_str: The reference date formatted as YYYY-MM-DD.
        days_before: Number of days prior to the reference date.

    Returns:
        The computed date string in YYYY-MM-DD format.

    Raises:
        ValueError: If base_date_str does not match YYYY-MM-DD.
    """
    try:
        dt = datetime.strptime(base_date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid date string '{base_date_str}'; expected YYYY-MM-DD") from e
    target = dt - timedelta(days=days_before)
    return target.strftime("%Y-%m-%d")


def _resolve_template(event_type: str, days: int, is_marathi: bool) -> MilestoneTemplate:
    if event_type == "wedding" and is_marathi and days in MARATHI_WEDDING_OVERRIDES:
        return MARATHI_WEDDING_OVERRIDES[days]
    type_templates = MILESTONE_TEMPLATES.get(event_type, MILESTONE_TEMPLATES["community_event"])
    return type_templates.get(days, MILESTONE_TEMPLATES["community_event"][0])


def _calculate_milestone_date(ev_dt: date, today: date, cfg: PhaseConfig) -> tuple[MilestonePhase, str]:
    target_date = ev_dt - timedelta(days=cfg.days)
    if target_date < today and cfg.phase != MilestonePhase.DAY_OF:
        return MilestonePhase.DO_IMMEDIATELY, today.strftime("%Y-%m-%d")
    return cfg.phase, target_date.strftime("%Y-%m-%d")


def build_milestones(
    event_date: str | None = None,
    event_type: str = "wedding",
    culture_region: str | None = None,
) -> list[PlanningMilestone]:
    """Dynamically generates backwards planning timeline milestones.

    Calculates target due dates based on the event date, adjusting past milestones
    to DO_IMMEDIATELY and applying cultural overrides where applicable.

    Args:
        event_date: Event date formatted as YYYY-MM-DD. Defaults to +90 days if None.
        event_type: Type of event ("wedding", "birthday", "community_event").
        culture_region: Cultural or regional modifier (e.g., "Marathi", "Maharashtrian").

    Returns:
        List of generated PlanningMilestone objects.

    Raises:
        ValueError: If event_date cannot be parsed as YYYY-MM-DD.
    """
    today = date.today()
    if not event_date:
        event_date = default_event_date(90)
    try:
        ev_dt = datetime.strptime(event_date, "%Y-%m-%d").date()
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid event_date '{event_date}'; expected YYYY-MM-DD") from e

    culture_lower = (culture_region or "").lower()
    is_marathi = any(k in culture_lower for k in MARATHI_KEYWORDS)

    milestones: list[PlanningMilestone] = []
    for cfg in PHASES_CONFIG:
        assigned_phase, due_date_str = _calculate_milestone_date(ev_dt, today, cfg)
        tmpl = _resolve_template(event_type, cfg.days, is_marathi)

        milestones.append(
            PlanningMilestone(
                id=f"ms_{uuid.uuid4().hex[:6]}",
                phase=assigned_phase,
                title=tmpl.title,
                description=tmpl.description,
                due_date=due_date_str,
                category=tmpl.category,
                completed=False,
            )
        )

    return milestones
