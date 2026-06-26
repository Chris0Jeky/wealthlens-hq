"""Tests for the request timeout middleware.

Uses a minimal FastAPI app with a very short timeout (0.1s) to keep tests fast.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator

import pytest
from app.timeout_middleware import TimeoutMiddleware
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.responses import StreamingResponse

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

    def test_negative_explicit_timeout_does_not_504(self) -> None:
        client = TestClient(_make_app(timeout=-5))
        assert client.get("/fast").status_code == 200

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
    """When headers are already sent, the middleware must not send a second response."""

    def test_streaming_timeout_does_not_corrupt_response(self) -> None:
        """A streaming endpoint that stalls mid-body should not produce a 504 JSON response."""
        client = TestClient(_make_app(timeout=0.1))
        response = client.get("/streaming-slow")
        # Headers were already sent (200) so middleware cannot override to 504.
        # The client sees whatever was sent before the timeout (partial or 200).
        assert response.status_code == 200

    def test_streaming_timeout_no_error_envelope(self) -> None:
        """A streaming timeout must not inject a JSON error envelope into the body."""
        client = TestClient(_make_app(timeout=0.1))
        response = client.get("/streaming-slow")
        assert "Request timed out" not in response.text
        assert "chunk2" not in response.text
