"""Tests for rate limiting middleware.

Verifies that the RateLimitMiddleware correctly:
- Allows requests under the limit
- Returns 429 with Retry-After when limit is exceeded
- Exempts health endpoints
- Skips rate limiting when client IP is None
- Respects the trust_forwarded_for flag
"""

from __future__ import annotations

import asyncio
import importlib
import time

import pytest
from app.rate_limit import MAX_TRACKED_IPS, RateLimitMiddleware
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest import MonkeyPatch
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import Receive, Scope, Send


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

    def test_health_with_trailing_slash_is_exempt(self) -> None:
        # "/health/" is 307-redirected to "/health" (and the redirect is itself
        # counted); both forms must be exempt — matching TimeoutMiddleware — so
        # well beyond the limit never yields a 429. (Exact-match exemption missed
        # the trailing-slash form.)
        client = TestClient(_create_app(requests_per_minute=3))
        for _ in range(10):
            assert client.get("/health/").status_code == 200

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

    def test_uses_rightmost_forwarded_for_so_spoofed_leftmost_cannot_bypass(self) -> None:
        """The RIGHTMOST X-Forwarded-For entry (appended by the trusted proxy)
        identifies the client; rotating the spoofable LEFTMOST value must NOT mint
        a fresh rate-limit bucket. Before the fix (leftmost), each distinct first
        value bypassed the limit; now all three share the same real client.
        """
        client = TestClient(_create_app(requests_per_minute=2, trust_forwarded_for=True))
        # Same real client (rightmost 9.9.9.9); attacker rotates the leftmost.
        client.get("/test", headers={"X-Forwarded-For": "1.1.1.1, 9.9.9.9"})
        client.get("/test", headers={"X-Forwarded-For": "2.2.2.2, 9.9.9.9"})
        response = client.get("/test", headers={"X-Forwarded-For": "3.3.3.3, 9.9.9.9"})
        assert response.status_code == 429


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

    def test_invalid_rate_limit_rpm_defaults_to_safe_limit(
        self,
        monkeypatch: MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("RATE_LIMIT_ENABLED", "true")
        monkeypatch.setenv("RATE_LIMIT_RPM", "not-a-number")

        import app.main as main

        reloaded_main = importlib.reload(main)
        client = TestClient(reloaded_main.app)

        for _ in range(60):
            assert client.get("/openapi.json").status_code == 200
        assert client.get("/openapi.json").status_code == 429


async def _noop_asgi(scope: Scope, receive: Receive, send: Send) -> None:
    """Placeholder downstream ASGI app for direct dispatch() tests (never run)."""
    return None


def _make_request(client_ip: str) -> Request:
    """Build a minimal GET request scope with a fixed client IP."""
    scope: Scope = {
        "type": "http",
        "http_version": "1.1",
        "method": "GET",
        "path": "/test",
        "headers": [],
        "query_string": b"",
        "scheme": "http",
        "server": ("testserver", 80),
        "client": (client_ip, 12345),
    }
    return Request(scope)


async def _call_next(request: Request) -> Response:
    """Stand-in downstream handler; returns 200 like a normal route would."""
    return Response("ok", status_code=200)


def _fill_to_cap(mw: RateLimitMiddleware, count: int, now: float) -> None:
    """Seed the limiter's IP table with `count` distinct synthetic IPs.

    Each gets one recent timestamp so it survives the 60s sliding-window clean
    and counts toward MAX_TRACKED_IPS. IPs are 10.x.x.x, distinct for any count
    up to 256**3 (~16.7M, well above the cap) and disjoint from the public test
    IPs (203.0.113.*, 192.0.2.*).
    """
    for i in range(count):
        ip = f"10.{(i // 65536) % 256}.{(i // 256) % 256}.{i % 256}"
        mw._hits[ip] = [now]


class TestRateLimitOverflow:
    """Keep memory bounded and enforce limits at MAX_TRACKED_IPS.

    Drive dispatch() directly to avoid 10k HTTP round-trips through TestClient.
    """

    def test_expired_idle_buckets_free_capacity(self, monkeypatch: MonkeyPatch) -> None:
        mw = RateLimitMiddleware(_noop_asgi, requests_per_minute=1)
        now = 10_000.0
        monkeypatch.setattr("app.rate_limit.time.time", lambda: now)
        _fill_to_cap(mw, MAX_TRACKED_IPS, now - 3600)

        async def run() -> None:
            new_ip = "203.0.113.5"
            assert (await mw.dispatch(_make_request(new_ip), _call_next)).status_code == 200
            assert new_ip in mw._hits
            assert len(mw._hits) == 1
            assert not mw._overflow_hits
            assert (await mw.dispatch(_make_request(new_ip), _call_next)).status_code == 429

        asyncio.run(run())
        # The purge must run again after another idle period, not just at startup.
        now += 3600
        _fill_to_cap(mw, MAX_TRACKED_IPS - 1, now - 3600)
        asyncio.run(run())

    @pytest.mark.parametrize("failure", [None, TimeoutError, RuntimeError])
    def test_overflow_downstream_does_not_hold_limiter_lock(self, failure: type[Exception] | None) -> None:
        mw = RateLimitMiddleware(_noop_asgi, requests_per_minute=2)
        _fill_to_cap(mw, MAX_TRACKED_IPS, time.time())

        async def run() -> None:
            started = asyncio.Event()
            release = asyncio.Event()
            known_reached = asyncio.Event()

            async def slow_handler(request: Request) -> Response:
                started.set()
                await release.wait()
                if failure is not None:
                    raise failure("downstream failed")
                return Response("ok")

            async def known_handler(request: Request) -> Response:
                known_reached.set()
                return Response("ok")

            overflow = asyncio.create_task(mw.dispatch(_make_request("203.0.113.99"), slow_handler))
            try:
                await asyncio.wait_for(started.wait(), timeout=1)
                response = await asyncio.wait_for(mw.dispatch(_make_request("10.0.0.0"), known_handler), timeout=1)
                assert response.status_code == 200
                assert known_reached.is_set()
                assert not release.is_set()
                assert (await mw.dispatch(_make_request("10.0.0.0"), known_handler)).status_code == 429
            finally:
                release.set()
                if failure is None:
                    assert (await overflow).status_code == 200
                else:
                    with pytest.raises(failure, match="downstream failed"):
                        await overflow
            assert not mw._lock.locked()

        asyncio.run(run())

    def test_below_cap_new_ip_is_tracked_and_limited(self) -> None:
        """Below the cap the normal sliding-window limit still applies."""
        mw = RateLimitMiddleware(_noop_asgi, requests_per_minute=3)
        now = time.time()
        _fill_to_cap(mw, MAX_TRACKED_IPS - 1, now)
        assert len(mw._hits) == MAX_TRACKED_IPS - 1

        async def run() -> None:
            new_ip = "203.0.113.5"
            # First 3 requests are allowed and the IP becomes tracked.
            for _ in range(3):
                resp = await mw.dispatch(_make_request(new_ip), _call_next)
                assert resp.status_code == 200
            assert new_ip in mw._hits
            # 4th request over the per-minute limit is rejected.
            resp = await mw.dispatch(_make_request(new_ip), _call_next)
            assert resp.status_code == 429

        asyncio.run(run())

    def test_at_cap_new_ip_is_rate_limited(self, monkeypatch: MonkeyPatch) -> None:
        """A full active-IP table must not leave a new client unlimited."""
        mw = RateLimitMiddleware(_noop_asgi, requests_per_minute=1)
        now = 10_000.0
        monkeypatch.setattr("app.rate_limit.time.time", lambda: now)
        _fill_to_cap(mw, MAX_TRACKED_IPS, now)
        assert len(mw._hits) == MAX_TRACKED_IPS

        async def run() -> None:
            new_ip = "203.0.113.99"
            responses = [await mw.dispatch(_make_request(new_ip), _call_next) for _ in range(3)]
            assert [response.status_code for response in responses] == [200, 429, 429]
            for response in responses[1:]:
                assert response.headers["Retry-After"] == "60"
                assert response.body == b'{"detail":"Rate limit exceeded. Try again later."}'
            assert new_ip not in mw._hits
            assert len(mw._hits) == MAX_TRACKED_IPS
            assert mw._overflow_hits == [now]

            # Rotating to another untracked IP shares the same bounded limit.
            assert (await mw.dispatch(_make_request("203.0.113.100"), _call_next)).status_code == 429
            assert len(mw._hits) == MAX_TRACKED_IPS
            assert mw._overflow_hits == [now]

        asyncio.run(run())
        # Keep the per-IP table active while the overflow window expires.
        now += mw.window_seconds
        _fill_to_cap(mw, MAX_TRACKED_IPS, now)
        asyncio.run(run())

    def test_at_cap_known_under_limit_ip_is_tracked_and_limited(self) -> None:
        """Known clients retain independent per-IP limits when the table is full."""
        mw = RateLimitMiddleware(_noop_asgi, requests_per_minute=3)
        now = time.time()
        _fill_to_cap(mw, MAX_TRACKED_IPS - 1, now)
        existing_ip = "192.0.2.7"
        mw._hits[existing_ip] = [now]  # KNOWN, 1 hit (under limit); table now full
        assert len(mw._hits) == MAX_TRACKED_IPS

        async def run() -> None:
            # Known clients keep their own bucket at capacity.
            for _ in range(2):
                resp = await mw.dispatch(_make_request(existing_ip), _call_next)
                assert resp.status_code == 200
            assert len(mw._hits[existing_ip]) == 3  # 1 seeded + 2 appended
            # Now at the per-minute limit -> 429.
            resp = await mw.dispatch(_make_request(existing_ip), _call_next)
            assert resp.status_code == 429

        asyncio.run(run())
