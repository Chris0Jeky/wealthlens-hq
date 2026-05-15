"""Tests for the WealthLens UK API — /api/health/data endpoint."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers import data as data_module

client = TestClient(app)


# ---------------------------------------------------------------------------
# /api/health/data
# ---------------------------------------------------------------------------


def test_health_data_returns_status():
    """Basic response structure check — all required keys are present."""
    response = client.get("/api/health/data")
    assert response.status_code == 200

    body = response.json()
    assert "status" in body
    assert body["status"] in ("healthy", "degraded", "unavailable")
    assert "datasets" in body
    assert "available_count" in body
    assert "total_count" in body
    assert body["total_count"] == len(data_module.DATASETS)

    # Every configured dataset must appear in the response.
    for name in data_module.DATASETS:
        assert name in body["datasets"]
        ds = body["datasets"][name]
        assert "file" in ds
        assert "available" in ds


def test_health_data_missing_csvs(tmp_path, monkeypatch):
    """All datasets unavailable when DATA_DIR points to an empty directory."""
    monkeypatch.setattr(data_module, "DATA_DIR", tmp_path)

    response = client.get("/api/health/data")
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "unavailable"
    assert body["available_count"] == 0
    assert body["total_count"] == len(data_module.DATASETS)

    for ds in body["datasets"].values():
        assert ds["available"] is False
        assert "error" in ds


def test_health_data_partial(tmp_path, monkeypatch):
    """Degraded status when only some CSVs exist."""
    monkeypatch.setattr(data_module, "DATA_DIR", tmp_path)

    # Create just the first dataset file so there's a mix of found/missing.
    first_name = next(iter(data_module.DATASETS))
    first_file = tmp_path / data_module.DATASETS[first_name]
    first_file.write_text("col1,col2\n1,2\n")

    response = client.get("/api/health/data")
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "degraded"
    assert body["available_count"] == 1
    assert body["total_count"] == len(data_module.DATASETS)

    # The file we created should be available with a size.
    assert body["datasets"][first_name]["available"] is True
    assert body["datasets"][first_name]["size_bytes"] > 0

    # The rest should be unavailable.
    for name in data_module.DATASETS:
        if name != first_name:
            assert body["datasets"][name]["available"] is False
