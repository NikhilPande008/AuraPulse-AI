import uuid
from datetime import date, datetime, timedelta
from typing import List, Optional

from ..schemas import (
    MilestoneCategory,
    MilestonePhase,
    PlanningMilestone,
)


def default_event_date(days_ahead: int = 90) -> str:
    """Return an ISO formatted date string for `days_ahead` days from today."""
    return (date.today() + timedelta(days=days_ahead)).isoformat()


def get_backwards_date(base_date_str: str, days_before: int) -> str:
    """
    Helper to calculate milestone due dates backwards from event date.
    Preserves exact calendar arithmetic including leap years.
    Raises ValueError on malformed date input (CR-16).
    """
    try:
        dt = datetime.strptime(base_date_str, "%Y-%m-%d").date()
    except Exception as e:
        raise ValueError(f"Invalid date string '{base_date_str}'; expected YYYY-MM-DD") from e
    target = dt - timedelta(days=days_before)
    return target.strftime("%Y-%m-%d")


def build_milestones(
    event_date: Optional[str] = None,
    event_type: str = "wedding",
    culture_region: Optional[str] = None
) -> List[PlanningMilestone]:
    """
    Dynamic Backwards Planning Timeline:
    Calculates target dates dynamically backwards from event_date:
    - T-6 Months (-180 days)
    - T-3 Months (-90 days)
    - T-1 Month (-30 days)
    - T-2 Weeks (-14 days)
    - T-1 Week (-7 days)
    - Day-Of (0 days)

    If scheduled in a short horizon, automatically compresses earlier milestones
    into 'Do Immediately' phase with today's date so no past dates are emitted.
    Default event_date = today + 90 days if omitted.
    """
    today = date.today()
    if not event_date:
        event_date = default_event_date(90)
        ev_dt = datetime.strptime(event_date, "%Y-%m-%d").date()
    else:
        try:
            ev_dt = datetime.strptime(event_date, "%Y-%m-%d").date()
        except Exception as e:
            raise ValueError(f"Invalid event_date '{event_date}'; expected YYYY-MM-DD") from e

    culture_lower = (culture_region or "").lower()
    is_marathi = any(k in culture_lower for k in ["marathi", "maharashtrian", "pune", "mumbai", "nashik"])

    # Milestone template definitions
    phases_config = [
        {"phase": MilestonePhase.T_MINUS_6_MONTHS, "days": 180},
        {"phase": MilestonePhase.T_MINUS_3_MONTHS, "days": 90},
        {"phase": MilestonePhase.T_MINUS_1_MONTH, "days": 30},
        {"phase": MilestonePhase.T_MINUS_2_WEEKS, "days": 14},
        {"phase": MilestonePhase.T_MINUS_1_WEEK, "days": 7},
        {"phase": MilestonePhase.DAY_OF, "days": 0},
    ]

    milestones: List[PlanningMilestone] = []

    for cfg in phases_config:
        days = cfg["days"]
        nominal_phase = cfg["phase"]
        target_date = ev_dt - timedelta(days=days)

        # Compress to 'Do Immediately' if target date is in the past
        if target_date < today and nominal_phase != MilestonePhase.DAY_OF:
            assigned_phase = MilestonePhase.DO_IMMEDIATELY
            due_date_str = today.strftime("%Y-%m-%d")
        else:
            assigned_phase = nominal_phase
            due_date_str = target_date.strftime("%Y-%m-%d")

        # Category and task formulation
        if event_type == "wedding":
            if days == 180:
                title = "Lock Banquet Venue & Wet Weather Backup"
                desc = "Finalize contract with main wedding hall/lawn, verify backup banquet permissions."
                cat = MilestoneCategory.VENUE
            elif days == 90:
                if is_marathi:
                    title = "Sakhar Puda Booking & Maharashtrian Menu Tasting"
                    desc = "Lock engagement / Sakhar Puda rituals and conduct Puran Poli & Modak tasting."
                    cat = MilestoneCategory.RITUALS
                else:
                    title = "Menu Tasting & Caterer Selection"
                    desc = "Sample culinary spread, finalize live counter menus and dietary accommodations."
                    cat = MilestoneCategory.CATERING
            elif days == 30:
                title = "Floral Stage & Mandap Mockup Sign-off"
                desc = "Review 3D floral installations, lighting angles, and bride/groom stage elevations."
                cat = MilestoneCategory.DECOR
            elif days == 14:
                title = "RSVP Lock & Seating Chart Finalization"
                desc = "Confirm exact guest count across all functions and distribute digital invitations."
                cat = MilestoneCategory.ATTIRE_INVITES
            elif days == 7:
                if is_marathi:
                    title = "Muhurt Patrika & Samagri Audit"
                    desc = "Coordinate with Guruji, finalize muhurt timings, Antarpat, and ritual samagri."
                    cat = MilestoneCategory.RITUALS
                else:
                    title = "Final Vendor Briefing & Rehearsal Walkthrough"
                    desc = "Align decorators, sound engineers, photographers and procession leads on run-of-show."
                    cat = MilestoneCategory.LOGISTICS
            else:
                title = "Ceremony Execution & Vendor Dispatch"
                desc = "Orchestrate Baraat ingress, Mandap rituals, and dinner banquet coordination."
                cat = MilestoneCategory.LOGISTICS

        elif event_type == "birthday":
            if days == 180:
                title = "Reserve Party Venue or Rooftop Lounge"
                desc = "Secure venue deposit, confirm AV and DJ decibel restrictions."
                cat = MilestoneCategory.VENUE
            elif days == 90:
                title = "Book Entertainment, DJ & Theme Stylist"
                desc = "Lock music artist, host / emcee, and thematic lighting setup."
                cat = MilestoneCategory.DECOR
            elif days == 30:
                title = "Custom Cake Tasting & Party Food Curation"
                desc = "Design multi-tier celebration cake and lock finger food / mocktail counters."
                cat = MilestoneCategory.CATERING
            elif days == 14:
                title = "Dispatch Digital RSVPs & Party Favors Procurement"
                desc = "Track guest confirmations and package personalized return gifts."
                cat = MilestoneCategory.ATTIRE_INVITES
            elif days == 7:
                title = "Game Master Briefing & Playlist Lock"
                desc = "Finalize interactive group games, scorecards, and entry music cues."
                cat = MilestoneCategory.LOGISTICS
            else:
                title = "Party Execution & Cake Cutting"
                desc = "Host arrival, interactive games, live DJ set, and celebration finale."
                cat = MilestoneCategory.LOGISTICS

        else: # community_event / festival
            if days == 180:
                title = "Secure Community Grounds & Municipal Ward Filings"
                desc = "Book central plaza/grounds and initiate local ward authority permissions."
                cat = MilestoneCategory.VENUE
            elif days == 90:
                title = "Vendor Stall Allocations & Sponsor Partnerships"
                desc = "Assign food, craft, and commercial stalls; lock green power / DG set vendors."
                cat = MilestoneCategory.CATERING
            elif days == 30:
                title = "Police, Sound & Fire Safety Clearances"
                desc = "Obtain loud-speaker permits, fire safety certifications, and medical paramedic desk."
                cat = MilestoneCategory.LOGISTICS
            elif days == 14:
                title = "Publicity Campaign & Volunteer Coordination"
                desc = "Deploy entry banners, print festival passes, and brief resident safety marshals."
                cat = MilestoneCategory.ATTIRE_INVITES
            elif days == 7:
                title = "Electrical Grounding, Sound Check & Ingress Drill"
                desc = "Audit generator safety, stage line arrays, and emergency crowd flow lanes."
                cat = MilestoneCategory.LOGISTICS
            else:
                title = "Festival Operations & Crowd Marshaling"
                desc = "Manage stage performances, food zone hygiene, and safe crowd egress."
                cat = MilestoneCategory.LOGISTICS

        milestones.append(
            PlanningMilestone(
                id=f"ms_{uuid.uuid4().hex[:6]}",
                phase=assigned_phase,
                title=title,
                description=desc,
                due_date=due_date_str,
                category=cat,
                completed=False,
            )
        )

    return milestones
