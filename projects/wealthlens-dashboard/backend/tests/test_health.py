"""Tests for health check endpoints."""

from __future__ import annotations

from pathlib import Path

from app.main import app
from app.routers import data as data_mod
from fastapi.testclient import TestClient

client = TestClient(app)


class TestLivenessProbe:
    """GET /health should always return ok."""

    def test_returns_ok(self) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestDataHealth:
    """GET /api/health/data should report dataset availability."""

    def test_returns_status_field(self) -> None:
        response = client.get("/api/health/data")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] in ("healthy", "degraded", "unavailable")

    def test_returns_dataset_counts(self) -> None:
        response = client.get("/api/health/data")
        body = response.json()
        assert "available_count" in body
        assert "total_count" in body
        assert body["total_count"] == len(data_mod.DATASETS)

    def test_returns_per_dataset_detail(self) -> None:
        response = client.get("/api/health/data")
        body = response.json()
        assert "datasets" in body
        for name in data_mod.DATASETS:
            assert name in body["datasets"]
            entry = body["datasets"][name]
            assert "available" in entry
            assert "file" in entry

    def test_healthy_when_all_files_exist(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.setattr(data_mod, "DATA_DIR", tmp_path)
        for filename in data_mod.DATASETS.values():
            (tmp_path / filename).write_text("col\n1\n")
        response = client.get("/api/health/data")
        assert response.json()["status"] == "healthy"
        assert response.json()["available_count"] == len(data_mod.DATASETS)

    def test_unavailable_when_no_files(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.setattr(data_mod, "DATA_DIR", tmp_path)
        response = client.get("/api/health/data")
        assert response.json()["status"] == "unavailable"
        assert response.json()["available_count"] == 0

    def test_degraded_when_partial_files(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.setattr(data_mod, "DATA_DIR", tmp_path)
        first_file = next(iter(data_mod.DATASETS.values()))
        (tmp_path / first_file).write_text("col\n1\n")
        response = client.get("/api/health/data")
        assert response.json()["status"] == "degraded"
        assert response.json()["available_count"] == 1
