"""Backend data-route edge-case tests.

Covers health_data statuses, metadata caching, _read_csv error branches,
pagination edge cases, and response model validation. Does NOT duplicate
tests already in tests/test_api.py.

All tests are fully mocked so they run without CSV data files on disk.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app
from app.routers import data as data_module
from app.routers.schemas import (
    AllDatasetsMetadataResponse,
    DatasetListResponse,
    DatasetMetadataResponse,
    PaginatedDatasetResponse,
)

client = TestClient(app)

# ---------------------------------------------------------------------------
# Shared fake data
# ---------------------------------------------------------------------------

_FAKE_DF = pd.DataFrame(
    {"year": [2020, 2021, 2022], "value": [0.1, 0.2, 0.3]}
)

_original_path_exists = Path.exists


def _csv_paths_exist(self: Path) -> bool:
    """Pretend CSV files inside DATA_DIR exist."""
    if str(self).startswith(str(data_module.DATA_DIR)):
        return True
    return _original_path_exists(self)


def _csv_paths_missing(self: Path) -> bool:
    """Pretend CSV files inside DATA_DIR do NOT exist."""
    if str(self).startswith(str(data_module.DATA_DIR)):
        return False
    return _original_path_exists(self)


def _fake_read_csv(*args, **kwargs):
    """Return a copy of the fake DataFrame for any read_csv call."""
    return _FAKE_DF.copy()


# ---------------------------------------------------------------------------
# 1. health_data -- healthy status
# ---------------------------------------------------------------------------


def _make_fake_file():
    """Return a mock file object whose fileno() returns a fake fd."""
    f = MagicMock()
    f.fileno.return_value = 999
    f.__enter__ = lambda self: self
    f.__exit__ = lambda self, *a: None
    return f


def test_health_data_healthy():
    """All CSVs present -> status 'healthy', available_count == total_count."""
    real_open = open  # noqa: A001

    def _mock_open(path, *args, **kwargs):
        if str(path).startswith(str(data_module.DATA_DIR)):
            return _make_fake_file()
        return real_open(path, *args, **kwargs)

    class _FakeStat:
        st_size = 42

    with (
        patch("builtins.open", side_effect=_mock_open),
        patch("os.fstat", return_value=_FakeStat()),
    ):
        resp = client.get("/api/health/data")

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "healthy"
    assert body["available_count"] == body["total_count"]
    assert body["total_count"] == len(data_module.DATASETS)


# ---------------------------------------------------------------------------
# 2. health_data -- degraded status
# ---------------------------------------------------------------------------


def test_health_data_degraded():
    """Some CSVs missing -> status 'degraded', available_count < total_count."""
    real_open = open  # noqa: A001
    call_count = 0

    def _open_partial(path, *args, **kwargs):
        nonlocal call_count
        if str(path).startswith(str(data_module.DATA_DIR)):
            call_count += 1
            if call_count > 1:
                raise OSError("mocked missing")
            return _make_fake_file()
        return real_open(path, *args, **kwargs)

    class _FakeStat:
        st_size = 42

    with (
        patch("builtins.open", side_effect=_open_partial),
        patch("os.fstat", return_value=_FakeStat()),
    ):
        resp = client.get("/api/health/data")

    body = resp.json()
    assert body["status"] == "degraded"
    assert 0 < body["available_count"] < body["total_count"]


# ---------------------------------------------------------------------------
# 3. health_data -- unavailable status
# ---------------------------------------------------------------------------


def test_health_data_unavailable():
    """All CSVs missing -> status 'unavailable', available_count == 0."""
    real_open = open  # noqa: A001

    def _always_fail(path, *args, **kwargs):
        if str(path).startswith(str(data_module.DATA_DIR)):
            raise OSError("mocked unavailable")
        return real_open(path, *args, **kwargs)

    with patch("builtins.open", side_effect=_always_fail):
        resp = client.get("/api/health/data")

    body = resp.json()
    assert body["status"] == "unavailable"
    assert body["available_count"] == 0


# ---------------------------------------------------------------------------
# 4. health_data per-dataset detail fields
# ---------------------------------------------------------------------------


def test_health_data_per_dataset_detail():
    """Each dataset entry has 'file' and 'available'; size_bytes when available."""
    real_open = open  # noqa: A001

    def _mock_open(path, *args, **kwargs):
        if str(path).startswith(str(data_module.DATA_DIR)):
            return _make_fake_file()
        return real_open(path, *args, **kwargs)

    class _FakeStat:
        st_size = 123

    with (
        patch("builtins.open", side_effect=_mock_open),
        patch("os.fstat", return_value=_FakeStat()),
    ):
        resp = client.get("/api/health/data")

    body = resp.json()
    for name, entry in body["datasets"].items():
        assert "file" in entry, f"{name} missing 'file'"
        assert "available" in entry, f"{name} missing 'available'"
        if entry["available"]:
            assert "size_bytes" in entry, f"{name} missing 'size_bytes'"
            assert isinstance(entry["size_bytes"], int)
            assert entry["size_bytes"] >= 0


# ---------------------------------------------------------------------------
# 5. metadata caching -- pd.read_csv called only once
# ---------------------------------------------------------------------------


def test_metadata_caching():
    """Second metadata call should use cache, not re-read CSV."""
    saved = dict(data_module._metadata_cache)
    data_module._metadata_cache.clear()
    try:
        with (
            patch.object(Path, "exists", _csv_paths_exist),
            patch(
                "app.routers.data.pd.read_csv",
                side_effect=_fake_read_csv,
            ) as mock_read,
        ):
            resp1 = client.get("/api/data/wealth-shares/metadata")
            assert resp1.status_code == 200
            first_call_count = mock_read.call_count

            resp2 = client.get("/api/data/wealth-shares/metadata")
            assert resp2.status_code == 200
            assert mock_read.call_count == first_call_count
    finally:
        data_module._metadata_cache.clear()
        data_module._metadata_cache.update(saved)


# ---------------------------------------------------------------------------
# 6. _read_csv UnicodeDecodeError handling
# ---------------------------------------------------------------------------


def test_read_csv_unicode_decode_error():
    """UnicodeDecodeError from read_csv -> 503 with dataset name in detail."""
    with (
        patch.object(Path, "exists", _csv_paths_exist),
        patch(
            "app.routers.data.pd.read_csv",
            side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "mocked"),
        ),
    ):
        resp = client.get("/api/data/wealth-shares")

    assert resp.status_code == 503
    detail = resp.json()["detail"]
    assert "wealth-shares" in detail


# ---------------------------------------------------------------------------
# 7. _read_csv EmptyDataError handling
# ---------------------------------------------------------------------------


def test_read_csv_empty_data_error():
    """EmptyDataError from read_csv -> 503 with dataset name in detail."""
    with (
        patch.object(Path, "exists", _csv_paths_exist),
        patch(
            "app.routers.data.pd.read_csv",
            side_effect=pd.errors.EmptyDataError("No columns to parse"),
        ),
    ):
        resp = client.get("/api/data/wealth-shares")

    assert resp.status_code == 503
    detail = resp.json()["detail"]
    assert "wealth-shares" in detail


# ---------------------------------------------------------------------------
# 8. _read_csv OSError handling
# ---------------------------------------------------------------------------


def test_read_csv_os_error():
    """OSError (PermissionError, file locking) from read_csv -> 503."""
    with (
        patch.object(Path, "exists", _csv_paths_exist),
        patch(
            "app.routers.data.pd.read_csv",
            side_effect=OSError("Permission denied"),
        ),
    ):
        resp = client.get("/api/data/wealth-shares")

    assert resp.status_code == 503
    detail = resp.json()["detail"]
    assert "wealth-shares" in detail


# ---------------------------------------------------------------------------
# 9. pagination limit=1 returns exactly 1 row
# ---------------------------------------------------------------------------


def test_pagination_limit_one():
    """limit=1 should return exactly 1 row."""
    with (
        patch.object(Path, "exists", _csv_paths_exist),
        patch("app.routers.data.pd.read_csv", side_effect=_fake_read_csv),
    ):
        resp = client.get("/api/data/wealth-shares?limit=1")

    assert resp.status_code == 200
    body = resp.json()
    assert len(body["data"]) == 1
    assert body["limit"] == 1


# ---------------------------------------------------------------------------
# 10. pagination limit=1000 returns at most 1000 rows
# ---------------------------------------------------------------------------


def test_pagination_limit_max():
    """limit=1000 should return at most 1000 rows."""
    with (
        patch.object(Path, "exists", _csv_paths_exist),
        patch("app.routers.data.pd.read_csv", side_effect=_fake_read_csv),
    ):
        resp = client.get("/api/data/wealth-shares?limit=1000")

    assert resp.status_code == 200
    body = resp.json()
    assert len(body["data"]) <= 1000
    assert body["limit"] == 1000


# ---------------------------------------------------------------------------
# 11. response model validation
# ---------------------------------------------------------------------------


def test_response_model_dataset_list():
    """GET /api/data/ response validates against DatasetListResponse."""
    resp = client.get("/api/data/")
    assert resp.status_code == 200
    parsed = DatasetListResponse(**resp.json())
    assert len(parsed.datasets) == len(data_module.DATASETS)


def test_response_model_paginated_dataset():
    """GET /api/data/{name} response validates against PaginatedDatasetResponse."""
    with (
        patch.object(Path, "exists", _csv_paths_exist),
        patch("app.routers.data.pd.read_csv", side_effect=_fake_read_csv),
    ):
        resp = client.get("/api/data/wealth-shares")

    assert resp.status_code == 200
    parsed = PaginatedDatasetResponse(**resp.json())
    assert parsed.page >= 1
    assert parsed.limit >= 1
    assert parsed.total >= 0
    assert parsed.total_pages >= 1


def test_response_model_single_metadata():
    """GET /api/data/{name}/metadata validates against DatasetMetadataResponse."""
    saved = dict(data_module._metadata_cache)
    data_module._metadata_cache.clear()
    try:
        with (
            patch.object(Path, "exists", _csv_paths_exist),
            patch("app.routers.data.pd.read_csv", side_effect=_fake_read_csv),
        ):
            resp = client.get("/api/data/wealth-shares/metadata")
    finally:
        data_module._metadata_cache.clear()
        data_module._metadata_cache.update(saved)

    assert resp.status_code == 200
    parsed = DatasetMetadataResponse(**resp.json())
    assert parsed.name == "wealth-shares"
    assert parsed.row_count >= 0


def test_response_model_all_metadata():
    """GET /api/data/metadata validates against AllDatasetsMetadataResponse."""
    saved = dict(data_module._metadata_cache)
    data_module._metadata_cache.clear()
    try:
        with (
            patch.object(Path, "exists", _csv_paths_exist),
            patch("app.routers.data.pd.read_csv", side_effect=_fake_read_csv),
        ):
            resp = client.get("/api/data/metadata")
    finally:
        data_module._metadata_cache.clear()
        data_module._metadata_cache.update(saved)

    assert resp.status_code == 200
    parsed = AllDatasetsMetadataResponse(**resp.json())
    assert len(parsed.datasets) == len(data_module.DATASETS)
    for ds in parsed.datasets:
        assert ds.row_count >= 0
        assert len(ds.columns) > 0
