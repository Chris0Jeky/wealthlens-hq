"""Tests for the FastAPI backend endpoints."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

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


# --- Metadata endpoint tests ---


def test_all_metadata_returns_all_datasets():
    """GET /api/data/metadata returns metadata for all 4 datasets."""
    response = client.get("/api/data/metadata")
    assert response.status_code == 200
    body = response.json()
    assert "datasets" in body
    datasets = body["datasets"]
    assert len(datasets) == 4
    names = {d["name"] for d in datasets}
    assert names == {"wealth-shares", "housing-affordability", "wealth-by-decile", "cgt-concentration"}

    required_fields = {"name", "description", "source", "source_url", "access_date", "row_count", "columns"}
    for ds in datasets:
        assert required_fields.issubset(ds.keys()), f"Missing fields in {ds['name']}"
        assert isinstance(ds["row_count"], int)
        assert ds["row_count"] > 0
        assert isinstance(ds["columns"], list)
        assert len(ds["columns"]) > 0


def test_single_dataset_metadata():
    """GET /api/data/{name}/metadata returns correct fields for one dataset."""
    response = client.get("/api/data/wealth-shares/metadata")
    assert response.status_code == 200
    meta = response.json()
    assert meta["name"] == "wealth-shares"
    assert meta["source"] == "World Inequality Database"
    assert meta["source_url"] == "https://wid.world/"
    assert meta["access_date"] == "2026-05-14"
    assert meta["row_count"] > 0
    assert "year" in meta["columns"]
    assert "value" in meta["columns"]


def test_single_dataset_metadata_unknown_returns_404():
    """GET /api/data/{name}/metadata returns 404 for unknown dataset."""
    response = client.get("/api/data/nonexistent/metadata")
    assert response.status_code == 404


# --- Pagination tests ---


def test_pagination_defaults():
    """Default pagination returns page 1, limit 100, and total metadata."""
    response = client.get("/api/data/wealth-shares")
    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 1
    assert body["limit"] == 100
    assert "total" in body
    assert "total_pages" in body
    assert body["total"] > 0
    assert len(body["data"]) <= 100


def test_pagination_custom_page_and_limit():
    """Custom page and limit params work correctly."""
    response = client.get("/api/data/wealth-shares?page=1&limit=5")
    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 1
    assert body["limit"] == 5
    assert len(body["data"]) == 5

    # Second page should also return data (wealth-shares has >5 rows)
    response2 = client.get("/api/data/wealth-shares?page=2&limit=5")
    assert response2.status_code == 200
    body2 = response2.json()
    assert body2["page"] == 2
    assert len(body2["data"]) == 5
    # Rows should be different from page 1
    assert body["data"] != body2["data"]


def test_pagination_beyond_range_returns_empty():
    """Requesting a page beyond total_pages returns empty data list."""
    response = client.get("/api/data/wealth-by-decile?page=999&limit=100")
    assert response.status_code == 200
    body = response.json()
    assert body["data"] == []
    assert body["page"] == 999
    assert body["total"] > 0


def test_pagination_invalid_limit_over_max_rejected():
    """Limit > 1000 is rejected with a 422 validation error."""
    response = client.get("/api/data/wealth-shares?limit=1001")
    assert response.status_code == 422


def test_pagination_invalid_page_zero_rejected():
    """Page 0 (< 1) is rejected with a 422 validation error."""
    response = client.get("/api/data/wealth-shares?page=0")
    assert response.status_code == 422


def test_pagination_total_pages_calculated_correctly():
    """total_pages should equal ceil(total / limit)."""
    import math

    response = client.get("/api/data/wealth-shares?limit=10")
    assert response.status_code == 200
    body = response.json()
    expected_pages = math.ceil(body["total"] / 10)
    assert body["total_pages"] == expected_pages


# --- Key parity tests ---


def test_datasets_and_dataset_meta_keys_match():
    """DATASETS and DATASET_META must have exactly the same keys.

    Catches the case where someone adds a key to one dict but forgets
    the other, which would cause a KeyError at runtime.
    """
    from app.routers.data import DATASET_META, DATASETS

    assert set(DATASETS.keys()) == set(DATASET_META.keys()), (
        f"Key mismatch — DATASETS: {sorted(DATASETS.keys())}, "
        f"DATASET_META: {sorted(DATASET_META.keys())}"
    )


# --- NaN handling tests ---


def test_dataset_response_contains_no_nan_strings():
    """JSON responses must not contain NaN as a value — only None/null."""
    import json

    response = client.get("/api/data/wealth-shares")
    assert response.status_code == 200
    raw = response.text
    # pandas NaN serialised as JSON would appear as the literal NaN (unquoted)
    # or "NaN" (quoted). Neither should be in our response.
    parsed = json.loads(raw)
    for row in parsed["data"]:
        for key, value in row.items():
            assert value != "NaN", f"Found string 'NaN' in {key}"
            # float('nan') != float('nan') is True, but json.loads turns
            # NaN into None in strict mode or raises ValueError, so a
            # successful parse already proves no bare NaN tokens.


# --- Error message quality tests ---


def test_read_csv_parser_error_returns_503_with_dataset_name():
    """When pd.read_csv raises ParserError, the 503 detail must include the dataset name."""
    import pandas as pd

    original_exists = Path.exists

    def _exists_true(self: Path) -> bool:
        """Let the CSV path pass the exists() guard so read_csv is reached."""
        from app.routers.data import DATA_DIR

        if str(self).startswith(str(DATA_DIR)):
            return True
        return original_exists(self)

    with (
        patch.object(Path, "exists", _exists_true),
        patch("app.routers.data.pd.read_csv", side_effect=pd.errors.ParserError("tokenizing")),
    ):
        response = client.get("/api/data/wealth-shares")

    assert response.status_code == 503
    detail = response.json()["detail"]
    assert "wealth-shares" in detail, f"Dataset name missing from error: {detail}"
    assert "tokenizing" in detail, f"Root-cause missing from error: {detail}"


def test_missing_csv_error_includes_dataset_name():
    """When a CSV file is missing, the 503 detail must include the dataset name."""
    from app.routers.data import DATA_DIR

    # Patch Path.exists to return False for the CSV file, simulating a missing file
    original_exists = Path.exists

    def fake_exists(self: Path) -> bool:
        if str(self).startswith(str(DATA_DIR)):
            return False
        return original_exists(self)

    with patch.object(Path, "exists", fake_exists):
        response = client.get("/api/data/wealth-shares")

    assert response.status_code == 503
    detail = response.json()["detail"]
    assert "wealth-shares" in detail, f"Dataset name missing from error: {detail}"


# --- Cache header tests ---


def test_dataset_list_has_cache_headers():
    """GET /api/data/ should include Cache-Control header."""
    response = client.get("/api/data/")
    assert response.status_code == 200
    assert "cache-control" in response.headers
    assert "public" in response.headers["cache-control"]


def test_metadata_has_long_cache():
    """GET /api/data/metadata should cache for 24 hours."""
    response = client.get("/api/data/metadata")
    assert response.status_code == 200
    cc = response.headers.get("cache-control", "")
    assert "max-age=86400" in cc


def test_dataset_has_cache_headers():
    """GET /api/data/{name} should include Cache-Control header."""
    response = client.get("/api/data/wealth-shares")
    assert response.status_code == 200
    assert "cache-control" in response.headers
    assert "public" in response.headers["cache-control"]


def test_health_has_no_cache():
    """GET /health should NOT include Cache-Control header."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "cache-control" not in response.headers
