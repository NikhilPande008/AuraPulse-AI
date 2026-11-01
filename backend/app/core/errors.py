"""Centralized error handlers and exception mapping for AuraPulse AI."""

import logging

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

from ..llm.client import (
    GeminiBadOutputError,
    GeminiQuotaError,
    GeminiUnavailableError,
)

logger = logging.getLogger("aurapulse.errors")


async def custom_http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle HTTPException while preserving structured error payloads.

    Args:
        request: Incoming FastAPI Request.
        exc: Raised HTTPException or Exception.

    Returns:
        JSONResponse with appropriate status code and structured JSON body.
    """
    if isinstance(exc, HTTPException):
        if isinstance(exc.detail, dict) and "code" in exc.detail:
            return JSONResponse(status_code=exc.status_code, content=exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": "HTTP_ERROR", "message": str(exc.detail)},
        )
    return JSONResponse(
        status_code=500,
        content={"code": "HTTP_ERROR", "message": str(exc)},
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Sanitize unhandled exceptions to avoid leaking internal tracebacks.

    Maps typed Gemini errors to standard HTTP status codes (503, 429, 502) and unknown
    exceptions to generic HTTP 500 responses.

    Args:
        request: Incoming FastAPI Request.
        exc: Unhandled exception.

    Returns:
        JSONResponse with mapped status code and sanitized error payload.
    """
    logger.error(
        f"Unhandled error handling {request.method} {request.url.path}: {exc}",
        exc_info=True,
    )
    if isinstance(exc, GeminiUnavailableError):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "code": "GEMINI_UNAVAILABLE",
                "message": "Gemini service is currently unavailable. Try again shortly.",
            },
        )
    if isinstance(exc, GeminiQuotaError):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "code": "GEMINI_QUOTA_EXCEEDED",
                "message": "Gemini API quota exceeded. Please wait a minute.",
            },
        )
    if isinstance(exc, GeminiBadOutputError):
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={
                "code": "GEMINI_BAD_OUTPUT",
                "message": "Gemini model produced an invalid response. Try again.",
            },
        )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": "INTERNAL_ERROR",
            "message": "An internal error occurred while processing your request. Please try again.",
        },
    )
