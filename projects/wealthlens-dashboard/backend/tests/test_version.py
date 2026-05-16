"""Tests for the /api/version endpoint."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_version_returns_200() -> None:
    client = TestClient(app)
    resp = client.get("/api/version")
    assert resp.status_code == 200


def test_version_contains_version_field() -> None:
    client = TestClient(app)
    body = client.get("/api/version").json()
    assert "version" in body
    assert body["version"] == "0.1.0"


def test_version_contains_project_name() -> None:
    client = TestClient(app)
    body = client.get("/api/version").json()
    assert body["project"] == "WealthLens UK"


def test_version_contains_title() -> None:
    client = TestClient(app)
    body = client.get("/api/version").json()
    assert body["title"] == "WealthLens UK API"
