"""Simple in-memory rate limiter middleware.

Uses a sliding window counter per client IP. No external dependencies.
Suitable for a low-traffic open-data API; for production at scale,
replace with Redis-backed rate limiting.
"""

from __future__ import annotations

import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

DEFAULT_LIMIT = 60
DEFAULT_WINDOW = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_window: int = DEFAULT_LIMIT, window_seconds: int = DEFAULT_WINDOW) -> None:
        super().__init__(app)
        self.limit = requests_per_window
        self.window = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)

    def _client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _prune(self, timestamps: list[float], now: float) -> list[float]:
        cutoff = now - self.window
        return [t for t in timestamps if t > cutoff]

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path == "/health":
            return await call_next(request)

        ip = self._client_ip(request)
        now = time.time()

        self._hits[ip] = self._prune(self._hits[ip], now)

        if len(self._hits[ip]) >= self.limit:
            retry_after = int(self.window - (now - self._hits[ip][0]))
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again later."},
                headers={"Retry-After": str(max(1, retry_after))},
            )

        self._hits[ip].append(now)

        response = await call_next(request)
        remaining = self.limit - len(self._hits[ip])
        response.headers["X-RateLimit-Limit"] = str(self.limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
