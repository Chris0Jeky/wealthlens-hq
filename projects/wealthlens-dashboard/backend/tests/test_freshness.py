"""Tests for the /api/data/freshness endpoint.

Tests freshness status classification, response shape, and edge cases
using a temporary data directory with controlled file modification times.
"""

from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import patch

import pytest
from app.main import app
from app.routers.data import (
    DATA_DIR,
    DATASETS,
    FRESHNESS_FRESH_HOURS,
    FRESHNESS_STALE_HOURS,
    _freshness_status,
)
from fastapi.testclient import TestClient

client = TestClient(app)


class TestFreshnessStatus:
    """Unit tests for the _freshness_status helper."""

    def test_fresh_within_threshold(self) -> None:
        assert _freshness_status(0) == "fresh"
        assert _freshness_status(100) == "fresh"
        assert _freshness_status(FRESHNESS_FRESH_HOURS) == "fresh"

    def test_stale_beyond_fresh(self) -> None:
        assert _freshness_status(FRESHNESS_FRESH_HOURS + 1) == "stale"
        assert _freshness_status(500) == "stale"
        assert _freshness_status(FRESHNESS_STALE_HOURS) == "stale"

    def test_expired_beyond_stale(self) -> None:
        assert _freshness_status(FRESHNESS_STALE_HOURS + 1) == "expired"
        assert _freshness_status(10000) == "expired"


class TestFreshnessEndpoint:
    """Integration tests for GET /api/data/freshness."""

    def test_returns_200(self) -> None:
        response = client.get("/api/data/freshness")
        assert response.status_code == 200

    def test_response_has_datasets_and_thresholds(self) -> None:
        response = client.get("/api/data/freshness")
        body = response.json()
        assert "datasets" in body
        assert "thresholds" in body
        assert isinstance(body["datasets"], dict)

    def test_thresholds_match_constants(self) -> None:
        response = client.get("/api/data/freshness")
        thresholds = response.json()["thresholds"]
        assert thresholds["fresh_hours"] == FRESHNESS_FRESH_HOURS
        assert thresholds["stale_hours"] == FRESHNESS_STALE_HOURS

    def test_all_datasets_present(self) -> None:
        response = client.get("/api/data/freshness")
        datasets = response.json()["datasets"]
        for name in DATASETS:
            assert name in datasets

    def test_each_entry_has_required_fields(self) -> None:
        response = client.get("/api/data/freshness")
        datasets = response.json()["datasets"]
        for name, entry in datasets.items():
            assert "last_updated" in entry
            assert "age_hours" in entry
            assert "status" in entry
            assert entry["status"] in ("fresh", "stale", "expired", "unknown")

    def test_missing_file_returns_unknown(self, tmp_path: Path) -> None:
        """When a CSV file does not exist, status should be 'unknown'."""
        with patch("app.routers.data.DATA_DIR", tmp_path):
            response = client.get("/api/data/freshness")
        body = response.json()
        # All files are missing in tmp_path
        for entry in body["datasets"].values():
            assert entry["last_updated"] is None
            assert entry["age_hours"] is None
            assert entry["status"] == "unknown"

    def test_fresh_file_status(self, tmp_path: Path) -> None:
        """A file modified just now should be classified as fresh."""
        # Create a fake CSV file for one dataset
        csv_file = tmp_path / DATASETS["wealth-shares"]
        csv_file.write_text("year,value\n2020,0.5\n")

        with patch("app.routers.data.DATA_DIR", tmp_path):
            response = client.get("/api/data/freshness")
        entry = response.json()["datasets"]["wealth-shares"]
        assert entry["status"] == "fresh"
        assert entry["last_updated"] is not None
        assert entry["age_hours"] is not None
        assert entry["age_hours"] < 1  # just created

    def test_stale_file_status(self, tmp_path: Path) -> None:
        """A file modified 10 days ago should be classified as stale."""
        csv_file = tmp_path / DATASETS["wealth-shares"]
        csv_file.write_text("year,value\n2020,0.5\n")
        # Set mtime to 10 days ago (240 hours)
        ten_days_ago = time.time() - (10 * 24 * 3600)
        import os

        os.utime(csv_file, (ten_days_ago, ten_days_ago))

        with patch("app.routers.data.DATA_DIR", tmp_path):
            response = client.get("/api/data/freshness")
        entry = response.json()["datasets"]["wealth-shares"]
        assert entry["status"] == "stale"

    def test_expired_file_status(self, tmp_path: Path) -> None:
        """A file modified 60 days ago should be classified as expired."""
        csv_file = tmp_path / DATASETS["wealth-shares"]
        csv_file.write_text("year,value\n2020,0.5\n")
        # Set mtime to 60 days ago
        sixty_days_ago = time.time() - (60 * 24 * 3600)
        import os

        os.utime(csv_file, (sixty_days_ago, sixty_days_ago))

        with patch("app.routers.data.DATA_DIR", tmp_path):
            response = client.get("/api/data/freshness")
        entry = response.json()["datasets"]["wealth-shares"]
        assert entry["status"] == "expired"

    def test_has_cache_control_header(self) -> None:
        response = client.get("/api/data/freshness")
        assert "cache-control" in response.headers
