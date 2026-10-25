"""Tests for the request timeout middleware.

Uses a minimal FastAPI app with a very short timeout (0.1s) to keep tests fast.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator

import pytest
from app.timeout_middleware import _DEFAULT_TIMEOUT, StreamAbortedError, StreamAbortGuard, TimeoutMiddleware
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from starlette.types import Receive, Scope, Send


async def _noop_app(scope: Scope, receive: Receive, send: Send) -> None:
    """Minimal ASGI app for unit-testing TimeoutMiddleware construction."""


async def _passthrough(request: Request, call_next: RequestResponseEndpoint) -> Response:
    """Stand-in for app.main's BaseHTTPMiddleware layers (logging, security headers)."""
    return await call_next(request)


# ---------------------------------------------------------------------------
# Test app with a deliberately short timeout for fast tests.
# ---------------------------------------------------------------------------


def _make_app(timeout: float = 0.1) -> FastAPI:
    """Create a minimal FastAPI app with TimeoutMiddleware configured."""
    test_app = FastAPI()
    test_app.add_middleware(TimeoutMiddleware, timeout_seconds=timeout)

    @test_app.get("/fast")
    async def fast_endpoint() -> dict[str, str]:
        """Returns immediately — should never trigger timeout."""
        return {"status": "ok"}

    @test_app.get("/slow")
    async def slow_endpoint() -> dict[str, str]:
        """Sleeps longer than the timeout — should trigger 504."""
        await asyncio.sleep(1.0)
        return {"status": "done"}

    @test_app.get("/streaming-slow")
    async def streaming_slow() -> StreamingResponse:
        """Starts sending chunks then stalls — tests partial-send timeout."""

        async def generate() -> AsyncGenerator[str, None]:
            yield "chunk1"
            await asyncio.sleep(1.0)
            yield "chunk2"

        return StreamingResponse(generate(), media_type="text/plain")

    @test_app.get("/health")
    async def health() -> dict[str, str]:
        """Exempt health endpoint."""
        return {"status": "ok"}

    @test_app.get("/api/health/data")
    async def health_data() -> dict[str, str]:
        """Exempt health data endpoint."""
        return {"status": "ok"}

    return test_app


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestFastRequestCompletes:
    """Fast requests should pass through without being affected by timeout."""

    def test_fast_request_returns_200(self) -> None:
        """A fast endpoint should return 200 with its normal body."""
        client = TestClient(_make_app())
        response = client.get("/fast")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestInvalidTimeoutFallsBack:
    """A non-positive/non-finite timeout must fall back to the default, not 504 all."""

    def test_zero_explicit_timeout_does_not_504(self) -> None:
        # timeout_seconds=0 would make asyncio.wait_for fire immediately -> 504 on
        # every request; the guard must fall back to the 30s default instead.
        client = TestClient(_make_app(timeout=0))
        assert client.get("/fast").status_code == 200

    @pytest.mark.parametrize("bad", [0.0, -5.0, float("inf"), float("nan")])
    def test_invalid_explicit_timeout_resolves_to_default(self, bad: float) -> None:
        # Assert the RESOLVED value, so the math.isfinite() guard is covered: a
        # bare `> 0` check would leave inf as the timeout (disabling the guard).
        mw = TimeoutMiddleware(_noop_app, timeout_seconds=bad)
        assert mw.timeout_seconds == _DEFAULT_TIMEOUT

    def test_valid_explicit_timeout_is_kept(self) -> None:
        assert TimeoutMiddleware(_noop_app, timeout_seconds=2.5).timeout_seconds == 2.5

    @pytest.mark.parametrize("bad", ["0", "-5", "inf", "nan", "abc", ""])
    def test_invalid_env_timeout_resolves_to_default(self, bad: str, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("REQUEST_TIMEOUT", bad)
        assert TimeoutMiddleware(_noop_app).timeout_seconds == _DEFAULT_TIMEOUT

    def test_zero_env_timeout_does_not_504(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("REQUEST_TIMEOUT", "0")
        app = FastAPI()
        app.add_middleware(TimeoutMiddleware)  # no explicit arg -> reads REQUEST_TIMEOUT

        @app.get("/fast")
        async def fast() -> dict[str, str]:
            return {"status": "ok"}

        assert TestClient(app).get("/fast").status_code == 200


class TestSlowRequestTimesOut:
    """Requests exceeding the timeout should receive a 504 response."""

    def test_slow_request_returns_504(self) -> None:
        """A slow endpoint should be killed and return 504."""
        client = TestClient(_make_app(timeout=0.1))
        response = client.get("/slow")
        assert response.status_code == 504

    def test_error_envelope_format(self) -> None:
        """The 504 response body must match the standard error envelope."""
        client = TestClient(_make_app(timeout=0.1))
        response = client.get("/slow")
        body = response.json()
        assert "error" in body
        assert body["error"]["code"] == 504
        assert body["error"]["message"] == "Request timed out"
        assert body["error"]["type"] == "timeout"


class TestHealthEndpointsExempt:
    """Health endpoints should not be subject to timeout enforcement."""

    def test_health_endpoint_not_timed_out(self) -> None:
        """/health should respond normally regardless of timeout config."""
        client = TestClient(_make_app(timeout=0.1))
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_health_data_endpoint_not_timed_out(self) -> None:
        """/api/health/data should respond normally regardless of timeout config."""
        client = TestClient(_make_app(timeout=0.1))
        response = client.get("/api/health/data")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestStreamingTimeout:
    """When headers are already sent, the timeout must abort the transfer, not end it cleanly."""

    def test_streaming_timeout_does_not_inject_error_envelope(self) -> None:
        """Without the guard, the middleware alone must not append a JSON 504 to the body."""
        response = TestClient(_make_app(timeout=0.1)).get("/streaming-slow")
        assert response.status_code == 200
        assert "Request timed out" not in response.text
        assert "chunk2" not in response.text

    def test_guard_aborts_behind_base_http_middleware(self) -> None:
        """BaseHTTPMiddleware between guard and timeout (as in app.main) ends the body cleanly.

        The guard must still abort: this is the case that produced a truncated 200.
        """
        app = _make_app(timeout=0.1)
        app.add_middleware(BaseHTTPMiddleware, dispatch=_passthrough)
        app.add_middleware(StreamAbortGuard)
        with pytest.raises(StreamAbortedError):
            TestClient(app).get("/streaming-slow")

    def test_pre_header_timeout_still_returns_504_with_guard(self) -> None:
        """Aborting only applies once headers are sent; a slow handler still gets a 504."""
        app = _make_app(timeout=0.1)
        app.add_middleware(BaseHTTPMiddleware, dispatch=_passthrough)
        app.add_middleware(StreamAbortGuard)
        assert TestClient(app).get("/slow").status_code == 504

    def test_guard_passes_normal_streams_through(self) -> None:
        app = _make_app(timeout=5.0)
        app.add_middleware(StreamAbortGuard)
        assert TestClient(app).get("/fast").json() == {"status": "ok"}

    def test_main_app_has_guard_outermost(self) -> None:
        from app.main import app as main_app

        assert main_app.user_middleware[0].cls is StreamAbortGuard
