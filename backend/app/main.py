"""AuraPulse AI: FastAPI Application Gateway."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import api_router
from .config import settings
from .core.errors import custom_http_exception_handler, global_exception_handler
from .core.middleware import limit_body_size_middleware, rate_limiting_middleware
from .core.rate_limit import SlidingWindowLimiter, get_client_ip

# Re-exports for test suite backward compatibility
__all__ = ["SlidingWindowLimiter", "app", "get_client_ip"]

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Autonomous Multimodal Event Planning & Reactive Contingency Engine",
)

# Global Middlewares
app.middleware("http")(limit_body_size_middleware)
app.middleware("http")(rate_limiting_middleware)

# CORS Configuration
allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
custom_origin = settings.ALLOWED_ORIGIN
if custom_origin:
    allowed_origins.extend([o.strip() for o in custom_origin.split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Exception Handlers
app.add_exception_handler(HTTPException, custom_http_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Include Route Handlers
app.include_router(api_router)
