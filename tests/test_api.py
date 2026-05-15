"""Tests for the FastAPI backend endpoints."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "projects" / "wealthlens-dashboard" / "backend"))

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_datasets():
    response = client.get("/api/data/")
    assert response.status_code == 200
    data = response.json()
    assert "datasets" in data
    assert "wealth-shares" in data["datasets"]
    assert "housing-affordability" in data["datasets"]
    assert "wealth-by-decile" in data["datasets"]
    assert "cgt-concentration" in data["datasets"]


def test_get_wealth_shares():
    response = client.get("/api/data/wealth-shares")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) > 0
    assert "year" in data["data"][0]
    assert "value" in data["data"][0]


def test_get_housing_affordability():
    response = client.get("/api/data/housing-affordability")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) > 0
    assert "region" in data["data"][0]


def test_get_wealth_by_decile():
    response = client.get("/api/data/wealth-by-decile")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) == 10


def test_get_cgt_concentration():
    response = client.get("/api/data/cgt-concentration")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) > 0


def test_unknown_dataset_returns_404():
    response = client.get("/api/data/nonexistent")
    assert response.status_code == 404


def test_cors_headers_present():
    response = client.get("/health", headers={"Origin": "http://localhost:3000"})
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
