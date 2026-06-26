"""Simple in-memory rate limiting middleware.

Uses a sliding window counter per client IP. Suitable for single-process
deployments; for multi-process/multi-node setups, swap for Redis-backed
rate limiting.
"""

from __future__ import annotations

import asyncio
import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

DEFAULT_REQUESTS_PER_MINUTE = 60
MAX_TRACKED_IPS = 10_000
EXEMPT_PATHS = frozenset({"/health", "/api/health/data"})


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Per-IP rate limiter using a sliding-window counter."""

    def __init__(
        self,
        app,
        requests_per_minute: int = DEFAULT_REQUESTS_PER_MINUTE,
        trust_forwarded_for: bool = False,
    ) -> None:
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.trust_forwarded_for = trust_forwarded_for
        self.window_seconds = 60
        self._hits: dict[str, list[float]] = defaultdict(list)
        self._lock = asyncio.Lock()

    def _get_client_ip(self, request: Request) -> str | None:
        if self.trust_forwarded_for:
            forwarded = request.headers.get("x-forwarded-for")
            if forwarded:
                return forwarded.split(",")[0].strip()
        return request.client.host if request.client else None

    def _clean_window(self, hits: list[float], now: float) -> list[float]:
        cutoff = now - self.window_seconds
        return [t for t in hits if t > cutoff]

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Normalise a trailing slash before the exemption check so "/health/"
        # (FastAPI 307-redirects it to "/health", and that redirect is itself
        # counted) is exempt too — matching TimeoutMiddleware. rstrip("/") maps
        # "/" -> "" which is not in the set, so the root path is unaffected.
        if request.url.path.rstrip("/") in EXEMPT_PATHS:
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        if client_ip is None:
            return await call_next(request)

        now = time.time()

        async with self._lock:
            cleaned = self._clean_window(self._hits[client_ip], now)
            if not cleaned:
                del self._hits[client_ip]
            else:
                self._hits[client_ip] = cleaned

            if len(self._hits.get(client_ip, [])) >= self.requests_per_minute:
                retry_after = int(self.window_seconds - (now - self._hits[client_ip][0]))
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded. Try again later."},
                    headers={"Retry-After": str(max(retry_after, 1))},
                )

            if len(self._hits) >= MAX_TRACKED_IPS and client_ip not in self._hits:
                return await call_next(request)

            self._hits[client_ip].append(now)

        return await call_next(request)
