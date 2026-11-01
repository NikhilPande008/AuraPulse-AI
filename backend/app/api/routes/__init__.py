"""AuraPulse API routes package aggregating all endpoint routers."""

from fastapi import APIRouter

from .aura import router as aura_router
from .export import router as export_router
from .health import router as health_router
from .integrations import router as integrations_router
from .pulse import router as pulse_router
from .studio import router as studio_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(aura_router)
api_router.include_router(pulse_router)
api_router.include_router(integrations_router)
api_router.include_router(export_router)
api_router.include_router(studio_router)

__all__ = ["api_router"]
