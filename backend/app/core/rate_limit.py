"""Rate limiting and client IP extraction infrastructure."""

import time
from collections import defaultdict

from fastapi import Request

from ..config import settings
from .constants import RATE_LIMIT_PER_DAY, RATE_LIMIT_PER_MINUTE


def get_client_ip(request: Request) -> str:
    """Extract client IP address using TRUSTED_PROXY_HOPS from X-Forwarded-For header.

    Args:
        request: Incoming FastAPI Request.

    Returns:
        The extracted client IP address as a string.
    """
    xff = request.headers.get("x-forwarded-for")
    if xff:
        parts = [p.strip() for p in xff.split(",") if p.strip()]
        if parts:
            trusted_hops = settings.TRUSTED_PROXY_HOPS
            idx = max(0, len(parts) - trusted_hops)
            return parts[idx]
    if request.client and request.client.host:
        return request.client.host
    return "127.0.0.1"


class SlidingWindowLimiter:
    """In-memory sliding-window rate limiter per client IP."""

    def __init__(
        self,
        per_minute: int = RATE_LIMIT_PER_MINUTE,
        per_day: int = RATE_LIMIT_PER_DAY,
    ) -> None:
        self.per_minute = per_minute
        self.per_day = per_day
        self._minute_buckets: dict[str, list[float]] = defaultdict(list)
        self._day_buckets: dict[str, list[float]] = defaultdict(list)
        self._last_prune = time.time()

    def _prune_dict(self, buckets: dict[str, list[float]], cutoff: float) -> None:
        empty_keys = [k for k, v in buckets.items() if not any(t > cutoff for t in v)]
        for k in empty_keys:
            del buckets[k]
        for k in list(buckets.keys()):
            buckets[k] = [t for t in buckets[k] if t > cutoff]

    def prune(self, now: float | None = None) -> None:
        """Prune timestamps older than active windows and purge empty client buckets.

        Args:
            now: Current epoch timestamp (defaults to time.time()).
        """
        if now is None:
            now = time.time()
        self._prune_dict(self._minute_buckets, now - 60.0)
        self._prune_dict(self._day_buckets, now - 86400.0)

    def _is_bucket_full(self, buckets: dict[str, list[float]], key: str, cutoff: float, limit: int) -> bool:
        buckets[key] = [t for t in buckets[key] if t > cutoff]
        return len(buckets[key]) >= limit

    def check_and_record(self, key: str) -> bool:
        """Check if request within rate limits and record current request timestamp.

        Args:
            key: Client identifier key (typically IP address).

        Returns:
            True if request is allowed, False if rate limit is exceeded.
        """
        now = time.time()
        if now - self._last_prune > 60.0:
            self.prune(now)
            self._last_prune = now

        if self._is_bucket_full(self._minute_buckets, key, now - 60.0, self.per_minute):
            return False
        if self._is_bucket_full(self._day_buckets, key, now - 86400.0, self.per_day):
            return False

        self._minute_buckets[key].append(now)
        self._day_buckets[key].append(now)
        return True


rate_limiter = SlidingWindowLimiter(per_minute=RATE_LIMIT_PER_MINUTE, per_day=RATE_LIMIT_PER_DAY)

AI_RATE_LIMITED_PATHS = {
    "/api/v1/aura/deconstruct",
    "/api/v1/aura/chat-copilot",
    "/api/v1/pulse/simulate",
    "/api/v1/studio/render-alternative",
    "/api/v1/integrations/vendors",
}
