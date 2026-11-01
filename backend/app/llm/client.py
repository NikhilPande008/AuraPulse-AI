"""LLM Client: Google GenAI API client with resilience, retry backoff, and error mapping."""

import asyncio
import base64
import json
import logging
import os
from enum import Enum, auto
from typing import Any

import google.api_core.exceptions
import httpx
from fastapi import HTTPException

from ..config import settings
from ..core.constants import MAX_IMAGE_BYTES, PLAN_GENERATION_TIMEOUT
from ..prompts import load_prompt
from ..schemas import (
    MasterEventPlan,
    PlanRequest,
)
from ..services.budget import rebalance_to_ceiling, recompute_totals
from ..services.timeline import build_milestones

logger = logging.getLogger("aurapulse.llm")

genai: Any = None
types: Any = None
_GENAI_AVAILABLE = False

try:
    import google.genai as _genai
    import google.genai.types as _types

    genai = _genai
    types = _types
    _GENAI_AVAILABLE = True
except (ImportError, KeyError):
    pass


# --- Custom Typed Exceptions ---


class ErrorKind(Enum):
    QUOTA = auto()
    UNAVAILABLE = auto()
    BAD_OUTPUT = auto()
    TIMEOUT = auto()


class GeminiError(Exception):
    """Base exception for Gemini LLM failures."""


class GeminiUnavailableError(GeminiError):
    """Raised on 5xx or connection/timeout failures."""


class GeminiQuotaError(GeminiError):
    """Raised on 429 Resource Exhausted / Quota errors."""


class GeminiBadOutputError(GeminiError):
    """Raised when Gemini returns malformed or invalid schema output."""


# Aliases for backward compatibility
GeminiUnavailable = GeminiUnavailableError
GeminiQuota = GeminiQuotaError
GeminiBadOutput = GeminiBadOutputError

RETRY_DELAYS: tuple[float, float] = (1.0, 3.0)

# Module-level lazy singleton client
_CLIENT_HOLDER: dict[str, Any] = {}


def get_genai_client() -> object | None:
    """Unified GenAI Client lazy singleton using modern google-genai SDK."""
    if "client" in _CLIENT_HOLDER:
        return _CLIENT_HOLDER["client"]
    if not _GENAI_AVAILABLE or genai is None:
        logger.error("google-genai package is not installed.")
        return None
    api_key = str(settings.GEMINI_API_KEY) or os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        logger.error("GEMINI_API_KEY is not configured.")
        return None
    client_instance = genai.Client(api_key=api_key)
    _CLIENT_HOLDER["client"] = client_instance
    return client_instance


def _classify_error(exc: Exception) -> ErrorKind:
    if isinstance(exc, TimeoutError | asyncio.TimeoutError):
        return ErrorKind.TIMEOUT
    err_str = str(exc).lower()
    if any(q in err_str for q in ("429", "resource_exhausted", "quota")):
        return ErrorKind.QUOTA
    if any(u in err_str for u in ("500", "503", "unavailable")):
        return ErrorKind.UNAVAILABLE
    return ErrorKind.BAD_OUTPUT


def _raise_typed_gemini_error(exc: Exception) -> None:
    kind = _classify_error(exc)
    err_msg = str(exc)
    if kind == ErrorKind.QUOTA:
        raise GeminiQuotaError(f"Gemini API quota exceeded: {err_msg}") from exc
    if kind in (ErrorKind.UNAVAILABLE, ErrorKind.TIMEOUT):
        raise GeminiUnavailableError(f"Gemini API service temporarily unavailable: {err_msg}") from exc
    raise GeminiBadOutputError(f"Gemini API call failed: {err_msg}") from exc


async def _attempt_generate(
    client: object, model: str, contents: object, config: object, timeout: float
) -> tuple[object | None, Exception | None, bool]:
    try:
        aio = getattr(client, "aio", None)
        runner = getattr(aio, "models", None)
        if runner is None or not hasattr(runner, "generate_content"):
            raise RuntimeError("Invalid GenAI client instance: missing aio.models.generate_content")

        response = await asyncio.wait_for(
            runner.generate_content(
                model=model,
                contents=contents,
                config=config,
            ),
            timeout=timeout,
        )
        return response, None, False
    except TimeoutError as e:
        logger.warning("Gemini call timed out")
        return None, e, True
    except (google.api_core.exceptions.GoogleAPIError, httpx.HTTPError, OSError, ValueError, RuntimeError) as e:
        kind = _classify_error(e)
        retryable = kind in (ErrorKind.QUOTA, ErrorKind.UNAVAILABLE, ErrorKind.TIMEOUT)
        if retryable:
            logger.warning("Gemini retryable error: %s", e)
        return None, e, retryable


async def generate(model: str, contents: object, config: object, timeout: float = 30.0) -> object:
    """Execute Gemini generation with exponential backoff and typed error mapping.

    Args:
        model: Target Gemini model identifier.
        contents: Input contents (text, multimodal parts, or structured objects).
        config: Generation configuration options.
        timeout: Operation timeout in seconds.

    Returns:
        The response object returned from the Gemini API.

    Raises:
        GeminiUnavailableError: If SDK or client is uninitialized, or 503 from upstream.
        GeminiQuotaError: If upstream quota or rate limits are exceeded (429).
        GeminiBadOutputError: If model output is malformed or invalid.
    """
    client = get_genai_client()
    if not client:
        raise GeminiUnavailableError("Gemini Client could not be initialized (missing API key or SDK)")

    last_err: Exception | None = None
    for attempt in range(len(RETRY_DELAYS) + 1):
        response, err, retryable = await _attempt_generate(client, model, contents, config, timeout)
        if response is not None:
            return response
        last_err = err
        if not retryable or attempt >= len(RETRY_DELAYS):
            break
        await asyncio.sleep(RETRY_DELAYS[attempt])

    if last_err is not None:
        _raise_typed_gemini_error(last_err)
    raise GeminiBadOutputError("Gemini call failed with unknown error")


def _detect_image_mime(b64_str: str) -> str:
    """Detects MIME type from image magic bytes and enforces a 4 MB decoded limit."""
    clean_b64 = b64_str.rsplit(",", maxsplit=1)[-1] if "," in b64_str else b64_str
    try:
        raw_bytes = base64.b64decode(clean_b64)
    except (ValueError, TypeError):
        raise HTTPException(status_code=422, detail="Invalid base64 encoding for moodboard image") from None

    if len(raw_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=422, detail="Upload a JPEG, PNG or WebP image under 4 MB")

    if raw_bytes.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if raw_bytes.startswith(b"\x89PNG\r\n\x1a\n") or raw_bytes.startswith(b"\x89PNG"):
        return "image/png"
    if raw_bytes.startswith(b"RIFF") and len(raw_bytes) > 12 and raw_bytes[8:12] == b"WEBP":
        return "image/webp"

    raise HTTPException(status_code=422, detail="Upload a JPEG, PNG or WebP image under 4 MB")


def _build_plan_contents(request: PlanRequest) -> list[Any]:
    dietary_str = ", ".join(request.dietary) if request.dietary else "Standard Gourmet"
    accessibility_str = (
        ", ".join(getattr(request, "accessibility", [])) if getattr(request, "accessibility", None) else "Standard"
    )

    template = load_prompt("plan_user_payload.v1.md")
    user_data_payload = template.format(
        event_type=request.event_type,
        city=request.city,
        headcount=request.headcount,
        budget=request.budget,
        culture_region=request.culture_region or "Indian Contemporary",
        theme=request.theme or "Elegant Celebration",
        dietary=dietary_str,
        accessibility=accessibility_str,
        notes=getattr(request, "notes", "") or "None",
        language=request.language,
    )

    contents: list[Any] = [user_data_payload]
    if request.image_base64 and _GENAI_AVAILABLE and types is not None:
        mime = _detect_image_mime(request.image_base64)
        clean_b64 = request.image_base64.split(",")[-1] if "," in request.image_base64 else request.image_base64
        raw_bytes = base64.b64decode(clean_b64)
        contents.append(types.Part.from_bytes(data=raw_bytes, mime_type=mime))
    return contents


def _hydrate_plan(plan: MasterEventPlan, request: PlanRequest) -> MasterEventPlan:
    plan.total_budget_limit = request.budget
    plan.location_city = request.city
    plan.event_type = request.event_type
    plan.event_date = request.event_date
    plan.culture_region = request.culture_region
    plan.theme = request.theme
    plan.headcount = request.headcount

    recompute_totals(plan)

    if plan.current_estimated_total > plan.total_budget_limit:
        plan, _, _ = rebalance_to_ceiling(plan, plan.total_budget_limit)

    if request.event_date:
        plan.planning_milestones = build_milestones(
            event_date=request.event_date,
            event_type=request.event_type,
            culture_region=request.culture_region,
        )
    return plan


async def generate_event_plan(request: PlanRequest, timeout: float = PLAN_GENERATION_TIMEOUT) -> MasterEventPlan:
    """Generate a structured MasterEventPlan from user requirements via Gemini.

    Hydrates user preferences, formats prompt payload with system instructions,
    enforces JSON schema output, balances against budget ceilings, and computes timeline milestones.

    Args:
        request: Validated user PlanRequest input.
        timeout: Generation timeout in seconds.

    Returns:
        A validated, hydrated, and budget-balanced MasterEventPlan.

    Raises:
        GeminiUnavailableError: If Gemini is unreachable or unconfigured.
        GeminiQuotaError: If Gemini quota is exceeded.
        GeminiBadOutputError: If response parsing or schema validation fails.
    """
    contents = _build_plan_contents(request)
    system_instruction = load_prompt("plan_generation.v1.md")
    config = (
        types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=MasterEventPlan,
            temperature=0.2,
        )
        if _GENAI_AVAILABLE and types is not None
        else None
    )

    try:
        response = await generate(model=settings.GEMINI_FLASH_MODEL, contents=contents, config=config, timeout=timeout)
    except Exception:
        logger.exception("Gemini API plan generation failed")
        raise

    resp_text = getattr(response, "text", "") or ""
    if not response or not resp_text:
        raise GeminiBadOutputError("Empty response received from Gemini generation engine")

    try:
        parsed = json.loads(resp_text)
        plan = MasterEventPlan.model_validate(parsed)
    except Exception as e:
        raise GeminiBadOutputError(f"Failed to parse plan schema from Gemini response: {e}") from e

    return _hydrate_plan(plan, request)
