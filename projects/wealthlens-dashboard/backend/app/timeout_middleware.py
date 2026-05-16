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
import os

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

_EXEMPT_PATHS: frozenset[str] = frozenset({"/health", "/api/health/data"})


class TimeoutMiddleware:
    """Enforce a per-request timeout on all non-exempt endpoints."""

    def __init__(self, app: ASGIApp, timeout_seconds: float | None = None) -> None:
        self.app = app
        if timeout_seconds is not None:
            self.timeout_seconds = timeout_seconds
        else:
            raw = os.environ.get("REQUEST_TIMEOUT", "30.0")
            try:
                self.timeout_seconds = float(raw)
            except ValueError:
                self.timeout_seconds = 30.0

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
                self.app(scope, receive, send_wrapper),
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
