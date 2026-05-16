"""Tests for Cache-Control response headers on dataset endpoints.

Verifies that:
- List and metadata endpoints return ``Cache-Control: public, max-age=3600``.
- Paginated data endpoints return ``Cache-Control: public, max-age=300``.
- Error responses (404) do NOT carry cache headers.

Tests that require CSV data files on disk are skipped automatically when
the processed data directory is missing or empty.
"""

from __future__ import annotations

import pytest
from app.main import app
from app.routers.data import DATA_DIR, DATASETS
from fastapi.testclient import TestClient

client = TestClient(app)

_first_dataset = next(iter(DATASETS))
_first_csv_exists = (DATA_DIR / DATASETS[_first_dataset]).exists()
_all_csvs_exist = all((DATA_DIR / fname).exists() for fname in DATASETS.values())

_skip_no_first_csv = pytest.mark.skipif(
    not _first_csv_exists,
    reason="First dataset CSV not available — run the data pipeline first",
)

_skip_no_all_csvs = pytest.mark.skipif(
    not _all_csvs_exist,
    reason="Not all CSV files available — run the data pipeline first",
)


# ------------------------------------------------------------------
# List endpoint — /api/data/
# ------------------------------------------------------------------


class TestListDatasetCacheHeader:
    """GET /api/data/ should return a 1-hour cache header."""

    def test_cache_control_present(self) -> None:
        response = client.get("/api/data/")
        assert response.status_code == 200
        assert response.headers.get("cache-control") == "public, max-age=3600"


# ------------------------------------------------------------------
# All-metadata endpoint — /api/data/metadata
# ------------------------------------------------------------------


class TestAllMetadataCacheHeader:
    """GET /api/data/metadata should return a 1-hour cache header."""

    @_skip_no_all_csvs
    def test_cache_control_present(self) -> None:
        response = client.get("/api/data/metadata")
        assert response.status_code == 200
        assert response.headers.get("cache-control") == "public, max-age=3600"


# ------------------------------------------------------------------
# Single-dataset metadata — /api/data/{name}/metadata
# ------------------------------------------------------------------


class TestSingleMetadataCacheHeader:
    """GET /api/data/{name}/metadata should return a 1-hour cache header."""

    @_skip_no_first_csv
    def test_cache_control_present(self) -> None:
        response = client.get(f"/api/data/{_first_dataset}/metadata")
        assert response.status_code == 200
        assert response.headers.get("cache-control") == "public, max-age=3600"


# ------------------------------------------------------------------
# Paginated data — /api/data/{name}
# ------------------------------------------------------------------


class TestDataEndpointCacheHeader:
    """GET /api/data/{name} should return a 5-minute cache header."""

    @_skip_no_first_csv
    def test_cache_control_present(self) -> None:
        response = client.get(f"/api/data/{_first_dataset}")
        assert response.status_code == 200
        assert response.headers.get("cache-control") == "public, max-age=300"


# ------------------------------------------------------------------
# Error responses — must NOT carry cache headers
# ------------------------------------------------------------------


class TestErrorResponseNoCacheHeader:
    """Error responses must NOT carry Cache-Control headers."""

    def test_404_data_no_cache_header(self) -> None:
        response = client.get("/api/data/nonexistent-dataset")
        assert response.status_code == 404
        assert "cache-control" not in response.headers

    def test_404_metadata_no_cache_header(self) -> None:
        response = client.get("/api/data/nonexistent-dataset/metadata")
        assert response.status_code == 404
        assert "cache-control" not in response.headers
