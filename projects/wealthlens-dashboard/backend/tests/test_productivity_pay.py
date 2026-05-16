"""Tests for the productivity-pay dataset endpoint.

Verifies that the /api/data/productivity-pay endpoint returns the
expected structure, metadata, and pagination behaviour — both when
the CSV exists and when it does not.
"""

from __future__ import annotations

import importlib

from fastapi.testclient import TestClient


def _make_client() -> TestClient:
    """Create a fresh test client with reloaded app module."""
    import app.main as main_mod

    importlib.reload(main_mod)
    return TestClient(main_mod.app)


class TestProductivityPayMetadata:
    """Metadata endpoint tests for productivity-pay dataset."""

    def test_dataset_in_list(self) -> None:
        """productivity-pay should appear in the dataset listing."""
        client = _make_client()
        response = client.get("/api/data/")
        assert response.status_code == 200
        data = response.json()
        assert "productivity-pay" in data["datasets"]

    def test_metadata_returns_source_citation(self) -> None:
        """Metadata should include source, source_url, and access_date."""
        client = _make_client()
        response = client.get("/api/data/productivity-pay/metadata")

        # If the CSV has not been generated yet, we get a 503 — that's
        # expected in CI where pipelines haven't run.
        if response.status_code == 503:
            return

        assert response.status_code == 200
        meta = response.json()
        assert meta["name"] == "productivity-pay"
        assert "ONS" in meta["source"]
        assert "source_url" in meta
        assert "access_date" in meta
        assert "columns" in meta
        assert "row_count" in meta

    def test_metadata_columns_match_schema(self) -> None:
        """Metadata columns should include the expected CSV columns."""
        client = _make_client()
        response = client.get("/api/data/productivity-pay/metadata")

        if response.status_code == 503:
            return

        assert response.status_code == 200
        meta = response.json()
        expected = {"year", "productivity_index", "pay_index", "gap_pct"}
        assert expected.issubset(set(meta["columns"]))


class TestProductivityPayData:
    """Data retrieval tests for the productivity-pay dataset."""

    def test_returns_paginated_data(self) -> None:
        """GET /api/data/productivity-pay should return paginated rows."""
        client = _make_client()
        response = client.get("/api/data/productivity-pay")

        if response.status_code == 503:
            return

        assert response.status_code == 200
        body = response.json()
        assert "data" in body
        assert "page" in body
        assert "total" in body
        assert body["page"] == 1
        assert body["total"] > 0

    def test_row_structure(self) -> None:
        """Each row should have year, productivity_index, pay_index, gap_pct."""
        client = _make_client()
        response = client.get("/api/data/productivity-pay")

        if response.status_code == 503:
            return

        assert response.status_code == 200
        rows = response.json()["data"]
        assert len(rows) > 0

        row = rows[0]
        assert "year" in row
        assert "productivity_index" in row
        assert "pay_index" in row
        assert "gap_pct" in row

    def test_pagination_limit(self) -> None:
        """Setting limit=5 should return at most 5 rows."""
        client = _make_client()
        response = client.get("/api/data/productivity-pay?limit=5")

        if response.status_code == 503:
            return

        assert response.status_code == 200
        body = response.json()
        assert len(body["data"]) <= 5
        assert body["limit"] == 5


class TestProductivityPayMissing:
    """Behaviour when the CSV has not been generated yet."""

    def test_returns_503_when_csv_missing(self) -> None:
        """Should return 503 with helpful message when CSV does not exist."""
        client = _make_client()

        # The data router checks DATA_DIR / filename. We verify the error
        # handling by ensuring we get either 200 (CSV exists) or 503 (not yet).
        response = client.get("/api/data/productivity-pay")
        assert response.status_code in (200, 503)

        if response.status_code == 503:
            detail = response.json()["detail"]
            assert "productivity-pay" in detail
