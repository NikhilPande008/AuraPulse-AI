"""Pulse Engine simulation and contingency evaluation endpoint."""

import logging

from fastapi import APIRouter, HTTPException

from ...agents import evaluate_contingency
from ...schemas import ContingencyDiff, SimulationRequest

logger = logging.getLogger("aurapulse.routes.pulse")
router = APIRouter(prefix="/api/v1/pulse", tags=["Pulse Engine"])


@router.post("/simulate", response_model=ContingencyDiff)
async def api_simulate_contingency(request: SimulationRequest) -> ContingencyDiff:
    """Evaluate crisis triggers deterministically and return contingency diffs.

    Args:
        request: Simulation request containing the plan and crisis trigger.

    Returns:
        ContingencyDiff with updated plan, budget delta, and schedule adjustments.

    Raises:
        HTTPException: On simulation failures.
    """
    try:
        return await evaluate_contingency(plan=request.plan, trigger=request.trigger)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Pulse Engine evaluation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"code": "SIMULATION_FAILED", "message": "Contingency simulation failed."},
        ) from e
