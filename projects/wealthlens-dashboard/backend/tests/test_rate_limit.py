"""Tests for rate limiting middleware.

Verifies that the RateLimitMiddleware correctly:
- Allows requests under the limit
- Returns 429 with Retry-After when limit is exceeded
- Exempts health endpoints
- Skips rate limiting when client IP is None
- Respects the trust_forwarded_for flag
"""

from __future__ import annotations

import importlib

from app.rate_limit import RateLimitMiddleware
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest import MonkeyPatch


def _create_app(requests_per_minute: int = 5, trust_forwarded_for: bool = False) -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=requests_per_minute,
        trust_forwarded_for=trust_forwarded_for,
    )

    @app.get("/test")
    def test_endpoint() -> dict:
        return {"ok": True}

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    @app.get("/api/health/data")
    def health_data() -> dict:
        return {"status": "healthy"}

    return app


class TestRateLimitBasic:
    """Basic rate limiting behavior."""

    def test_allows_requests_under_limit(self) -> None:
        client = TestClient(_create_app(requests_per_minute=5))
        for _ in range(5):
            response = client.get("/test")
            assert response.status_code == 200

    def test_returns_429_when_limit_exceeded(self) -> None:
        client = TestClient(_create_app(requests_per_minute=3))
        for _ in range(3):
            client.get("/test")
        response = client.get("/test")
        assert response.status_code == 429

    def test_429_includes_retry_after_header(self) -> None:
        client = TestClient(_create_app(requests_per_minute=1))
        client.get("/test")
        response = client.get("/test")
        assert response.status_code == 429
        assert "retry-after" in response.headers
        assert int(response.headers["retry-after"]) >= 1

    def test_429_response_body(self) -> None:
        client = TestClient(_create_app(requests_per_minute=1))
        client.get("/test")
        response = client.get("/test")
        assert response.json() == {"detail": "Rate limit exceeded. Try again later."}


class TestRateLimitExemptions:
    """Health endpoints are exempt from rate limiting."""

    def test_health_endpoint_exempt(self) -> None:
        client = TestClient(_create_app(requests_per_minute=1))
        client.get("/test")
        client.get("/test")
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_data_endpoint_exempt(self) -> None:
        client = TestClient(_create_app(requests_per_minute=1))
        client.get("/test")
        client.get("/test")
        response = client.get("/api/health/data")
        assert response.status_code == 200


class TestForwardedFor:
    """X-Forwarded-For header handling."""

    def test_ignores_forwarded_for_by_default(self) -> None:
        client = TestClient(_create_app(requests_per_minute=2))
        client.get("/test", headers={"X-Forwarded-For": "1.1.1.1"})
        client.get("/test", headers={"X-Forwarded-For": "2.2.2.2"})
        response = client.get("/test", headers={"X-Forwarded-For": "3.3.3.3"})
        assert response.status_code == 429

    def test_respects_forwarded_for_when_trusted(self) -> None:
        client = TestClient(_create_app(requests_per_minute=2, trust_forwarded_for=True))
        client.get("/test", headers={"X-Forwarded-For": "1.1.1.1"})
        client.get("/test", headers={"X-Forwarded-For": "1.1.1.1"})
        response = client.get("/test", headers={"X-Forwarded-For": "2.2.2.2"})
        assert response.status_code == 200


class TestRateLimitAppConfig:
    """Application-level rate limit toggle behavior."""

    def test_rate_limit_default_off(self, monkeypatch: MonkeyPatch) -> None:
        monkeypatch.delenv("RATE_LIMIT_ENABLED", raising=False)
        monkeypatch.setenv("RATE_LIMIT_RPM", "1")

        import app.main as main

        reloaded_main = importlib.reload(main)
        client = TestClient(reloaded_main.app)

        assert client.get("/openapi.json").status_code == 200
        assert client.get("/openapi.json").status_code == 200

    def test_rate_limit_enabled_explicitly(self, monkeypatch: MonkeyPatch) -> None:
        monkeypatch.setenv("RATE_LIMIT_ENABLED", "true")
        monkeypatch.setenv("RATE_LIMIT_RPM", "1")

        import app.main as main

        reloaded_main = importlib.reload(main)
        client = TestClient(reloaded_main.app)

        assert client.get("/openapi.json").status_code == 200
        assert client.get("/openapi.json").status_code == 429
