"""Tests for the data API endpoints.

Covers dataset listing, paginated data retrieval, metadata,
health check, and error handling for missing/invalid datasets.
"""

from __future__ import annotations

from unittest.mock import patch

import pandas as pd
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


SAMPLE_DF = pd.DataFrame({"year": [2020, 2021, 2022], "value": [1.0, 2.0, 3.0]})


class TestListDatasets:
    """GET /api/data/ should return the list of available dataset names."""

    def test_returns_200(self) -> None:
        response = client.get("/api/data/")
        assert response.status_code == 200

    def test_returns_dataset_names(self) -> None:
        response = client.get("/api/data/")
        body = response.json()
        assert "datasets" in body
        assert isinstance(body["datasets"], list)
        assert len(body["datasets"]) > 0

    def test_known_datasets_present(self) -> None:
        response = client.get("/api/data/")
        names = response.json()["datasets"]
        for expected in ("wealth-shares", "housing-affordability", "cgt-concentration", "wealth-by-decile"):
            assert expected in names


class TestGetDataset:
    """GET /api/data/{name} should return paginated dataset rows."""

    def test_unknown_dataset_returns_404(self) -> None:
        response = client.get("/api/data/nonexistent")
        assert response.status_code == 404

    @patch("app.routers.data._read_csv", return_value=SAMPLE_DF)
    def test_returns_paginated_data(self, mock_read) -> None:  # noqa: ANN001
        response = client.get("/api/data/wealth-shares")
        assert response.status_code == 200
        body = response.json()
        assert "data" in body
        assert body["total"] == 3
        assert body["page"] == 1
        assert len(body["data"]) == 3

    @patch("app.routers.data._read_csv", return_value=SAMPLE_DF)
    def test_pagination_limit(self, mock_read) -> None:  # noqa: ANN001
        response = client.get("/api/data/wealth-shares?limit=2&page=1")
        assert response.status_code == 200
        body = response.json()
        assert len(body["data"]) == 2
        assert body["total_pages"] == 2

    @patch("app.routers.data._read_csv", return_value=SAMPLE_DF)
    def test_pagination_page_2(self, mock_read) -> None:  # noqa: ANN001
        response = client.get("/api/data/wealth-shares?limit=2&page=2")
        assert response.status_code == 200
        body = response.json()
        assert len(body["data"]) == 1

    def test_invalid_page_returns_422(self) -> None:
        response = client.get("/api/data/wealth-shares?page=0")
        assert response.status_code == 422

    def test_invalid_limit_returns_422(self) -> None:
        response = client.get("/api/data/wealth-shares?limit=0")
        assert response.status_code == 422

    def test_limit_exceeding_max_returns_422(self) -> None:
        response = client.get("/api/data/wealth-shares?limit=1001")
        assert response.status_code == 422


class TestDatasetMetadata:
    """GET /api/data/{name}/metadata should return source citations."""

    def test_unknown_dataset_returns_404(self) -> None:
        response = client.get("/api/data/nonexistent/metadata")
        assert response.status_code == 404

    @patch("app.routers.data._read_csv", return_value=SAMPLE_DF)
    def test_returns_metadata(self, mock_read) -> None:  # noqa: ANN001
        response = client.get("/api/data/wealth-shares/metadata")
        assert response.status_code == 200
        body = response.json()
        assert body["name"] == "wealth-shares"
        assert "source" in body
        assert "source_url" in body
        assert "access_date" in body
        assert body["row_count"] == 3

    @patch("app.routers.data._read_csv", return_value=SAMPLE_DF)
    def test_metadata_includes_columns(self, mock_read) -> None:  # noqa: ANN001
        response = client.get("/api/data/wealth-shares/metadata")
        body = response.json()
        assert body["columns"] == ["year", "value"]


class TestAllDatasetsMetadata:
    """GET /api/data/metadata should return metadata for all datasets."""

    @patch("app.routers.data._read_csv", return_value=SAMPLE_DF)
    def test_returns_all_metadata(self, mock_read) -> None:  # noqa: ANN001
        response = client.get("/api/data/metadata")
        assert response.status_code == 200
        body = response.json()
        assert "datasets" in body
        assert len(body["datasets"]) == 4


class TestHealthEndpoints:
    """Health endpoints should respond correctly."""

    def test_liveness_probe(self) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_data_health_returns_status(self) -> None:
        response = client.get("/api/health/data")
        assert response.status_code == 200
        body = response.json()
        assert "status" in body
        assert body["status"] in ("healthy", "degraded", "unavailable")
        assert "datasets" in body
        assert "available_count" in body
        assert "total_count" in body
        assert body["total_count"] == 4
