"""Tests for rate limiting middleware."""

from __future__ import annotations

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


class TestRateLimit:
    """Rate limiting middleware should restrict excessive requests."""

    def test_normal_request_includes_rate_limit_headers(self) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        assert "x-ratelimit-limit" not in response.headers

    def test_api_request_includes_rate_limit_headers(self) -> None:
        response = client.get("/api/data/")
        assert response.status_code == 200
        assert "x-ratelimit-limit" in response.headers
        assert "x-ratelimit-remaining" in response.headers

    def test_rate_limit_remaining_decreases(self) -> None:
        r1 = client.get("/api/data/")
        r2 = client.get("/api/data/")
        remaining1 = int(r1.headers["x-ratelimit-remaining"])
        remaining2 = int(r2.headers["x-ratelimit-remaining"])
        assert remaining2 < remaining1
