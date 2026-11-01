"""HTTP middleware components for payload size enforcement and rate limiting."""

import os
from collections.abc import Callable
from typing import Any

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse

from .constants import MAX_BODY_BYTES
from .rate_limit import AI_RATE_LIMITED_PATHS, get_client_ip, rate_limiter


async def limit_body_size_middleware(request: Request, call_next: Callable[[Request], Any]) -> Response:
    """Enforce maximum request body size limit of 6MB.

    Args:
        request: Incoming FastAPI Request.
        call_next: Next middleware or route handler in chain.

    Returns:
        HTTP 413 JSONResponse if payload exceeds MAX_BODY_BYTES, else downstream response.
    """
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > MAX_BODY_BYTES:
                return JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={
                        "code": "PAYLOAD_TOO_LARGE",
                        "message": "Request body exceeds the maximum permitted size of 6MB.",
                    },
                )
        except ValueError:
            pass

    return await call_next(request)


async def rate_limiting_middleware(request: Request, call_next: Callable[[Request], Any]) -> Response:
    """Enforce sliding-window rate limit on intensive AI and integration endpoints.

    Args:
        request: Incoming FastAPI Request.
        call_next: Next middleware or route handler in chain.

    Returns:
        HTTP 429 JSONResponse if client limit exceeded, else downstream response.
    """
    if (
        request.url.path in AI_RATE_LIMITED_PATHS
        and (request.method == "POST" or request.url.path == "/api/v1/integrations/vendors")
        and os.getenv("DISABLE_RATE_LIMIT", "false").lower() != "true"
    ):
        client_ip = get_client_ip(request)
        if not rate_limiter.check_and_record(client_ip):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "code": "RATE_LIMITED",
                    "message": "Too many requests. Please wait a moment before trying again.",
                },
            )

    return await call_next(request)
