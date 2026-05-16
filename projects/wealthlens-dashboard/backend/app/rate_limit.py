"""Simple in-memory rate limiting middleware.

Uses a sliding window counter per client IP. Suitable for single-process
deployments; for multi-process/multi-node setups, swap for Redis-backed
rate limiting.
"""

from __future__ import annotations

import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

DEFAULT_REQUESTS_PER_MINUTE = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Per-IP rate limiter using a fixed-window counter."""

    def __init__(self, app, requests_per_minute: int = DEFAULT_REQUESTS_PER_MINUTE) -> None:  # noqa: ANN001
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.window_seconds = 60
        self._hits: dict[str, list[float]] = defaultdict(list)

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _clean_window(self, hits: list[float], now: float) -> list[float]:
        cutoff = now - self.window_seconds
        return [t for t in hits if t > cutoff]

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path == "/health":
            return await call_next(request)

        now = time.time()
        client_ip = self._get_client_ip(request)

        self._hits[client_ip] = self._clean_window(self._hits[client_ip], now)

        if len(self._hits[client_ip]) >= self.requests_per_minute:
            retry_after = int(self.window_seconds - (now - self._hits[client_ip][0]))
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again later."},
                headers={"Retry-After": str(max(retry_after, 1))},
            )

        self._hits[client_ip].append(now)
        return await call_next(request)
