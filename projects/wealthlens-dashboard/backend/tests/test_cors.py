"""Tests for CORS middleware configuration.

Verifies that:
- CORS headers are present for allowed origins.
- The CORS_ORIGINS env var overrides the default origins list.
- Default origins include the local Vite dev server addresses.
"""

from __future__ import annotations

import os
from unittest.mock import patch

from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Helpers — each test that needs a custom CORS_ORIGINS value must reimport
# app.main so that module-level code re-evaluates the env var.
# ---------------------------------------------------------------------------

def _make_client(env_overrides: dict[str, str] | None = None) -> TestClient:
    """Return a TestClient with optional env-var overrides.

    Because ``cors_origins`` is computed at import time we need to reload the
    module whenever we change the env.
    """
    import importlib

    import app.main as main_mod

    if env_overrides:
        with patch.dict(os.environ, env_overrides):
            importlib.reload(main_mod)
            return TestClient(main_mod.app)
    else:
        importlib.reload(main_mod)
        return TestClient(main_mod.app)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCorsHeadersPresent:
    """CORS headers must appear for requests from allowed origins."""

    def test_cors_headers_present(self) -> None:
        """GET /health from localhost:3000 should include CORS allow header."""
        client = _make_client()
        response = client.get(
            "/health",
            headers={"Origin": "http://localhost:3000"},
        )
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"

    def test_cors_headers_for_127(self) -> None:
        """GET /health from 127.0.0.1:3000 should also be allowed by default."""
        client = _make_client()
        response = client.get(
            "/health",
            headers={"Origin": "http://127.0.0.1:3000"},
        )
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "http://127.0.0.1:3000"

    def test_cors_rejects_unknown_origin(self) -> None:
        """Requests from unlisted origins should not receive CORS headers."""
        client = _make_client()
        response = client.get(
            "/health",
            headers={"Origin": "http://evil.example.com"},
        )
        assert response.status_code == 200
        assert "access-control-allow-origin" not in response.headers


class TestCorsEnvOverride:
    """CORS_ORIGINS env var should override the default origins."""

    def test_custom_origin_via_env(self) -> None:
        """Setting CORS_ORIGINS should allow the specified origin."""
        client = _make_client({"CORS_ORIGINS": "https://wealthlens.uk"})
        response = client.get(
            "/health",
            headers={"Origin": "https://wealthlens.uk"},
        )
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "https://wealthlens.uk"

    def test_custom_origin_replaces_defaults(self) -> None:
        """When CORS_ORIGINS is set, the default localhost origins should no longer be allowed."""
        client = _make_client({"CORS_ORIGINS": "https://wealthlens.uk"})
        response = client.get(
            "/health",
            headers={"Origin": "http://localhost:3000"},
        )
        assert response.status_code == 200
        # localhost should NOT be in the allow header when overridden
        assert response.headers.get("access-control-allow-origin") != "http://localhost:3000"

    def test_multiple_custom_origins(self) -> None:
        """CORS_ORIGINS can contain multiple comma-separated origins."""
        client = _make_client({
            "CORS_ORIGINS": "https://wealthlens.uk, https://staging.wealthlens.uk",
        })
        for origin in ("https://wealthlens.uk", "https://staging.wealthlens.uk"):
            response = client.get(
                "/health",
                headers={"Origin": origin},
            )
            assert response.status_code == 200
            assert response.headers.get("access-control-allow-origin") == origin


class TestCorsEdgeCases:
    """Edge-case CORS_ORIGINS values should fall back to defaults."""

    def test_empty_cors_origins_falls_back(self) -> None:
        """CORS_ORIGINS="" should fall back to default localhost origins."""
        client = _make_client({"CORS_ORIGINS": ""})
        response = client.get(
            "/health",
            headers={"Origin": "http://localhost:3000"},
        )
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"

    def test_trailing_comma_filtered(self) -> None:
        """CORS_ORIGINS="https://a.com," should allow a.com and not produce empty entry."""
        client = _make_client({"CORS_ORIGINS": "https://a.com,"})
        # The valid origin should work
        response = client.get(
            "/health",
            headers={"Origin": "https://a.com"},
        )
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "https://a.com"
        # An empty-string origin must not be allowed
        response = client.get(
            "/health",
            headers={"Origin": "http://evil.example.com"},
        )
        assert "access-control-allow-origin" not in response.headers

    def test_whitespace_only_falls_back(self) -> None:
        """CORS_ORIGINS="  " should fall back to default localhost origins."""
        client = _make_client({"CORS_ORIGINS": "  "})
        response = client.get(
            "/health",
            headers={"Origin": "http://localhost:3000"},
        )
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"


class TestCorsDefaults:
    """Module-level defaults should be sensible."""

    def test_default_origins_include_localhost(self) -> None:
        """Without CORS_ORIGINS env var, localhost:3000 should be allowed."""
        # Ensure CORS_ORIGINS is not set
        env = os.environ.copy()
        env.pop("CORS_ORIGINS", None)
        with patch.dict(os.environ, env, clear=True):
            client = _make_client()
        response = client.get(
            "/health",
            headers={"Origin": "http://localhost:3000"},
        )
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
