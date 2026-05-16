"""Tests for the /health endpoint."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_200() -> None:
    response = client.get("/health")
    assert response.status_code == 200


def test_health_contains_expected_keys() -> None:
    response = client.get("/health")
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "started_at_utc" in data
    assert "uptime_seconds" in data


def test_health_version_is_correct() -> None:
    response = client.get("/health")
    data = response.json()
    assert data["version"] == "0.1.0"


def test_health_uptime_is_non_negative_int() -> None:
    response = client.get("/health")
    data = response.json()
    assert isinstance(data["uptime_seconds"], int)
    assert data["uptime_seconds"] >= 0


def test_health_started_at_is_valid_iso_datetime() -> None:
    response = client.get("/health")
    data = response.json()
    # Should parse without raising
    parsed = datetime.fromisoformat(data["started_at_utc"])
    assert parsed.tzinfo == timezone.utc
