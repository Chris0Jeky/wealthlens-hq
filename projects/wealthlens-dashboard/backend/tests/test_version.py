"""Tests for the /api/version and /api/version/debug endpoints."""

from __future__ import annotations

import os
import platform
from unittest.mock import patch

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


# ---------------------------------------------------------------------------
# /api/version — public, safe for unauthenticated access
# ---------------------------------------------------------------------------


def test_version_returns_200() -> None:
    response = client.get("/api/version")
    assert response.status_code == 200


def test_version_contains_only_public_keys() -> None:
    response = client.get("/api/version")
    data = response.json()
    expected_keys = {"version", "datasets_available", "status"}
    assert set(data.keys()) == expected_keys


def test_version_is_0_2_0() -> None:
    response = client.get("/api/version")
    data = response.json()
    assert data["version"] == "0.2.0"


def test_version_datasets_available_is_positive_int() -> None:
    response = client.get("/api/version")
    data = response.json()
    assert isinstance(data["datasets_available"], int)
    assert data["datasets_available"] > 0


def test_version_status_is_ok() -> None:
    response = client.get("/api/version")
    data = response.json()
    assert data["status"] == "ok"


# ---------------------------------------------------------------------------
# /api/version/debug — only available in non-production environments
# ---------------------------------------------------------------------------


def test_version_debug_returns_200_in_dev() -> None:
    with patch.dict(os.environ, {"APP_ENV": "development"}):
        response = client.get("/api/version/debug")
    assert response.status_code == 200


def test_version_debug_contains_all_expected_keys() -> None:
    with patch.dict(os.environ, {"APP_ENV": "development"}):
        response = client.get("/api/version/debug")
    data = response.json()
    expected_keys = {
        "version",
        "commit",
        "environment",
        "python_version",
        "datasets_available",
        "uptime_seconds",
    }
    assert set(data.keys()) == expected_keys


def test_version_debug_python_version_is_safe() -> None:
    """python_version must be just the version number, no build paths."""
    with patch.dict(os.environ, {"APP_ENV": "development"}):
        response = client.get("/api/version/debug")
    data = response.json()
    assert data["python_version"] == platform.python_version()
    # Should not contain filesystem paths
    assert "/" not in data["python_version"]
    assert "\\" not in data["python_version"]


def test_version_debug_commit_is_string() -> None:
    with patch.dict(os.environ, {"APP_ENV": "development"}):
        response = client.get("/api/version/debug")
    data = response.json()
    assert isinstance(data["commit"], str)
    assert len(data["commit"]) > 0


def test_version_debug_uptime_is_non_negative_float() -> None:
    with patch.dict(os.environ, {"APP_ENV": "development"}):
        response = client.get("/api/version/debug")
    data = response.json()
    assert isinstance(data["uptime_seconds"], float)
    assert data["uptime_seconds"] >= 0


def test_version_debug_returns_404_in_production() -> None:
    with patch.dict(os.environ, {"APP_ENV": "production"}):
        response = client.get("/api/version/debug")
    assert response.status_code == 404


def test_version_debug_closed_for_production_variants() -> None:
    """Any production-like value (case-insensitive) is 404 — not just exact 'production'."""
    for value in ("Production", "PRODUCTION", "PROD", "prod"):
        with patch.dict(os.environ, {"APP_ENV": value}):
            response = client.get("/api/version/debug")
        assert response.status_code == 404, f"APP_ENV={value!r} should be closed"


def test_version_debug_closed_for_unknown_env() -> None:
    """An unrecognised APP_ENV fails CLOSED (not open)."""
    with patch.dict(os.environ, {"APP_ENV": "totally-unknown"}):
        response = client.get("/api/version/debug")
    assert response.status_code == 404


def test_version_debug_open_for_unset_app_env() -> None:
    """APP_ENV unset defaults to development -> open (local dev still works)."""
    with patch.dict(os.environ):
        os.environ.pop("APP_ENV", None)
        response = client.get("/api/version/debug")
    assert response.status_code == 200


def test_version_debug_open_for_staging() -> None:
    with patch.dict(os.environ, {"APP_ENV": "staging"}):
        response = client.get("/api/version/debug")
    assert response.status_code == 200


def test_version_debug_uses_git_commit_env_var() -> None:
    """GIT_COMMIT env var should be preferred over local Git metadata."""
    with patch.dict(os.environ, {"GIT_COMMIT": "abc1234567890", "APP_ENV": "development"}):
        # Need to reimport to pick up the env var — but since _git_commit
        # is resolved at import time, we test the function directly.
        from app.main import _get_git_commit

        commit = _get_git_commit()
    assert commit == "abc1234"
