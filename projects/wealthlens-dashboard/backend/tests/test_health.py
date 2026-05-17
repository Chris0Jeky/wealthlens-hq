"""Tests for the /health endpoint."""

from __future__ import annotations

from datetime import UTC, datetime

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health_returns_200() -> None:
    response = client.get("/health")
    assert response.status_code == 200


def test_health_contains_expected_keys() -> None:
    response = client.get("/health")
    data = response.json()
    assert "status" in data
    assert "datasets_loaded" in data
    assert "timestamp" in data


def test_health_status_is_ok() -> None:
    response = client.get("/health")
    data = response.json()
    assert data["status"] == "ok"


def test_health_datasets_loaded_is_positive_int() -> None:
    response = client.get("/health")
    data = response.json()
    assert isinstance(data["datasets_loaded"], int)
    assert data["datasets_loaded"] > 0


def test_health_timestamp_is_valid_iso_datetime() -> None:
    response = client.get("/health")
    data = response.json()
    # Should parse without raising
    parsed = datetime.fromisoformat(data["timestamp"])
    assert parsed.tzinfo == UTC
