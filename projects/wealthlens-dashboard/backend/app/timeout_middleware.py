"""Request timeout middleware for the WealthLens backend.

Pure ASGI middleware that wraps each incoming request with an asyncio timeout
to prevent long-running handlers from tying up workers indefinitely.  Returns
a 504 Gateway Timeout JSON response if the handler exceeds the configured
threshold.

Configuration:
    REQUEST_TIMEOUT env var — timeout in seconds (float).  Default: 30.0

Health endpoints (/health, /api/health/data) are exempt from the timeout so
that liveness probes always respond even under load.
"""

from __future__ import annotations

import asyncio
import logging
import math
import os

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger(__name__)

_EXEMPT_PATHS: frozenset[str] = frozenset({"/health", "/api/health/data"})
_DEFAULT_TIMEOUT = 30.0


class TimeoutMiddleware:
    """Enforce a per-request timeout on all non-exempt endpoints."""

    def __init__(self, app: ASGIApp, timeout_seconds: float | None = None) -> None:
        self.app = app
        # A non-positive timeout would 504 EVERY request, and a non-finite one
        # (inf/nan) would break the guard entirely, so validate both the explicit
        # arg and the REQUEST_TIMEOUT env var and fall back LOUDLY to the default
        # — mirroring main.py's RATE_LIMIT_RPM flooring.
        source: object = timeout_seconds if timeout_seconds is not None else os.environ.get("REQUEST_TIMEOUT", "30.0")
        try:
            parsed = float(source)  # type: ignore[arg-type]
        except (ValueError, TypeError):
            parsed = math.nan
        if math.isfinite(parsed) and parsed > 0:
            self.timeout_seconds = parsed
        else:
            logger.warning("Invalid request timeout %r; defaulting to %.1fs", source, _DEFAULT_TIMEOUT)
            self.timeout_seconds = _DEFAULT_TIMEOUT

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if path.rstrip("/") in _EXEMPT_PATHS:
            await self.app(scope, receive, send)
            return

        response_started = False

        async def send_wrapper(message: dict) -> None:  # type: ignore[type-arg]
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            await asyncio.wait_for(
                self.app(scope, receive, send_wrapper),  # type: ignore[arg-type]
                timeout=self.timeout_seconds,
            )
        except TimeoutError:
            if not response_started:
                response = JSONResponse(
                    status_code=504,
                    content={
                        "error": {
                            "code": 504,
                            "message": "Request timed out",
                            "type": "timeout",
                        }
                    },
                )
                await response(scope, receive, send)
