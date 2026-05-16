"""Tests for the /api/data/ endpoints.

Verifies dataset listing, paginated data retrieval, metadata responses,
404 handling for unknown datasets, and query parameter validation.

These are integration tests that require processed CSV files in the data
directory. They will be skipped in CI if the files are not present.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers.data import DATA_DIR, DATASETS

client = TestClient(app)

KNOWN_DATASETS = list(DATASETS.keys())

pytestmark = pytest.mark.skipif(
    not all((DATA_DIR / f).exists() for f in DATASETS.values()),
    reason="Processed CSV files not available — run the pipeline first",
)


class TestListDatasets:
    """GET /api/data/ returns available dataset names."""

    def test_returns_200(self) -> None:
        response = client.get("/api/data/")
        assert response.status_code == 200

    def test_response_contains_datasets_key(self) -> None:
        response = client.get("/api/data/")
        body = response.json()
        assert "datasets" in body
        assert isinstance(body["datasets"], list)

    def test_all_known_datasets_present(self) -> None:
        response = client.get("/api/data/")
        datasets = response.json()["datasets"]
        for name in KNOWN_DATASETS:
            assert name in datasets


class TestGetDataset:
    """GET /api/data/{name} returns paginated row data."""

    def test_returns_200_for_known_dataset(self) -> None:
        response = client.get("/api/data/wealth-shares")
        assert response.status_code == 200

    def test_response_shape(self) -> None:
        response = client.get("/api/data/wealth-shares")
        body = response.json()
        assert "data" in body
        assert "page" in body
        assert "limit" in body
        assert "total" in body
        assert "total_pages" in body

    def test_data_is_list_of_dicts(self) -> None:
        response = client.get("/api/data/wealth-shares")
        data = response.json()["data"]
        assert isinstance(data, list)
        assert len(data) > 0
        assert isinstance(data[0], dict)

    def test_pagination_defaults(self) -> None:
        response = client.get("/api/data/wealth-shares")
        body = response.json()
        assert body["page"] == 1
        assert body["limit"] == 100

    def test_custom_page_and_limit(self) -> None:
        response = client.get("/api/data/wealth-shares?page=1&limit=5")
        body = response.json()
        assert body["limit"] == 5
        assert len(body["data"]) <= 5

    def test_404_for_unknown_dataset(self) -> None:
        response = client.get("/api/data/nonexistent")
        assert response.status_code == 404

    def test_invalid_page_rejected(self) -> None:
        response = client.get("/api/data/wealth-shares?page=0")
        assert response.status_code == 422

    def test_limit_exceeds_max_rejected(self) -> None:
        response = client.get("/api/data/wealth-shares?limit=1001")
        assert response.status_code == 422

    def test_limit_zero_rejected(self) -> None:
        response = client.get("/api/data/wealth-shares?limit=0")
        assert response.status_code == 422

    def test_page_beyond_last_returns_empty_data(self) -> None:
        response = client.get("/api/data/wealth-shares?page=9999")
        body = response.json()
        assert response.status_code == 200
        assert body["data"] == []
        assert body["page"] == 9999


class TestDatasetMetadata:
    """GET /api/data/{name}/metadata returns source-cited metadata."""

    def test_returns_200_for_known_dataset(self) -> None:
        response = client.get("/api/data/wealth-shares/metadata")
        assert response.status_code == 200

    def test_response_contains_required_fields(self) -> None:
        response = client.get("/api/data/wealth-shares/metadata")
        body = response.json()
        assert body["name"] == "wealth-shares"
        assert "description" in body
        assert "source" in body
        assert "source_url" in body
        assert "access_date" in body
        assert "row_count" in body
        assert "columns" in body

    def test_row_count_is_positive(self) -> None:
        response = client.get("/api/data/wealth-shares/metadata")
        assert response.json()["row_count"] > 0

    def test_columns_is_nonempty_list(self) -> None:
        response = client.get("/api/data/wealth-shares/metadata")
        columns = response.json()["columns"]
        assert isinstance(columns, list)
        assert len(columns) > 0

    def test_404_for_unknown_dataset(self) -> None:
        response = client.get("/api/data/nonexistent/metadata")
        assert response.status_code == 404


class TestAllDatasetsMetadata:
    """GET /api/data/metadata returns metadata for all datasets."""

    def test_returns_200(self) -> None:
        response = client.get("/api/data/metadata")
        assert response.status_code == 200

    def test_contains_all_datasets(self) -> None:
        response = client.get("/api/data/metadata")
        datasets = response.json()["datasets"]
        names = [d["name"] for d in datasets]
        for name in KNOWN_DATASETS:
            assert name in names


class TestHealthData:
    """GET /api/health/data reports dataset availability."""

    def test_returns_200(self) -> None:
        response = client.get("/api/health/data")
        assert response.status_code == 200

    def test_status_is_healthy_when_data_present(self) -> None:
        response = client.get("/api/health/data")
        body = response.json()
        assert body["status"] in ("healthy", "degraded")
        assert body["available_count"] > 0

    def test_total_count_matches_list_endpoint(self) -> None:
        list_resp = client.get("/api/data/")
        health_resp = client.get("/api/health/data")
        assert health_resp.json()["total_count"] == len(list_resp.json()["datasets"])
