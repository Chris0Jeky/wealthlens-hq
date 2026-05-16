"""Tests for the /api/version endpoint."""

from __future__ import annotations

import sys

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_version_returns_200() -> None:
    response = client.get("/api/version")
    assert response.status_code == 200


def test_version_contains_all_expected_keys() -> None:
    response = client.get("/api/version")
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


def test_version_is_0_2_0() -> None:
    response = client.get("/api/version")
    data = response.json()
    assert data["version"] == "0.2.0"


def test_version_commit_is_string() -> None:
    response = client.get("/api/version")
    data = response.json()
    assert isinstance(data["commit"], str)
    assert len(data["commit"]) > 0


def test_version_environment_defaults_to_development() -> None:
    response = client.get("/api/version")
    data = response.json()
    # In test context, APP_ENV is not set, so defaults to 'development'
    assert data["environment"] == "development"


def test_version_python_version_matches_runtime() -> None:
    response = client.get("/api/version")
    data = response.json()
    assert data["python_version"] == sys.version


def test_version_datasets_available_is_positive_int() -> None:
    response = client.get("/api/version")
    data = response.json()
    assert isinstance(data["datasets_available"], int)
    assert data["datasets_available"] > 0


def test_version_uptime_is_non_negative_float() -> None:
    response = client.get("/api/version")
    data = response.json()
    assert isinstance(data["uptime_seconds"], float)
    assert data["uptime_seconds"] >= 0
