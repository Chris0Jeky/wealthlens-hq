"""Request timeout middleware for the WealthLens backend.

Wraps each incoming request with an asyncio timeout to prevent long-running
handlers from tying up workers indefinitely.  Returns a 504 Gateway Timeout
JSON response if the handler exceeds the configured threshold.

Configuration:
    REQUEST_TIMEOUT env var — timeout in seconds (float).  Default: 30.0

Health endpoints (/health, /api/health/data) are exempt from the timeout so
that liveness probes always respond even under load.
"""

from __future__ import annotations

import asyncio
import os

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

# Paths that should never be subject to timeout enforcement.
_EXEMPT_PATHS: set[str] = {"/health", "/api/health/data"}


class TimeoutMiddleware(BaseHTTPMiddleware):
    """Enforce a per-request timeout on all non-exempt endpoints."""

    def __init__(self, app: ASGIApp, timeout_seconds: float | None = None) -> None:
        super().__init__(app)
        if timeout_seconds is not None:
            self.timeout_seconds = timeout_seconds
        else:
            self.timeout_seconds = float(
                os.environ.get("REQUEST_TIMEOUT", "30.0")
            )

    async def dispatch(self, request: Request, call_next) -> Response:  # noqa: ANN001
        """Wrap the downstream handler with an asyncio timeout."""
        if request.url.path in _EXEMPT_PATHS:
            return await call_next(request)

        try:
            response: Response = await asyncio.wait_for(
                call_next(request),
                timeout=self.timeout_seconds,
            )
        except asyncio.TimeoutError:
            return JSONResponse(
                status_code=504,
                content={
                    "error": {
                        "code": 504,
                        "message": "Request timed out",
                        "type": "timeout",
                    }
                },
            )

        return response
