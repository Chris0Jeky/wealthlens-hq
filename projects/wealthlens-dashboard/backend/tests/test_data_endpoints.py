"""Tests for the core data router endpoints: list, metadata, pagination."""

from __future__ import annotations

import logging
from pathlib import Path

import pytest
from app.main import app
from app.routers import data as data_mod
from fastapi.testclient import TestClient

CSV_CONTENT = """\
year,value,region
2018,50.5,London
2019,60.0,Manchester
2020,70.1,Birmingham
2021,80.2,London
2022,90.3,Manchester
"""


@pytest.fixture(autouse=True)
def _fake_data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    for filename in data_mod.DATASETS.values():
        (tmp_path / filename).write_text(CSV_CONTENT, encoding="utf-8")
    monkeypatch.setattr(data_mod, "DATA_DIR", tmp_path)
    data_mod._metadata_cache.clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


class TestListDatasets:
    def test_returns_all_dataset_names(self, client: TestClient) -> None:
        resp = client.get("/api/data/")
        assert resp.status_code == 200
        body = resp.json()
        assert "datasets" in body
        assert set(body["datasets"]) == set(data_mod.DATASETS.keys())

    def test_response_is_a_list(self, client: TestClient) -> None:
        resp = client.get("/api/data/")
        assert isinstance(resp.json()["datasets"], list)


class TestDatasetMetadata:
    def test_single_dataset_metadata(self, client: TestClient) -> None:
        resp = client.get("/api/data/wealth-shares/metadata")
        assert resp.status_code == 200
        body = resp.json()
        assert body["name"] == "wealth-shares"
        assert body["source"] == "World Inequality Database"
        assert body["row_count"] == 5
        assert "year" in body["columns"]

    def test_all_datasets_metadata(self, client: TestClient) -> None:
        resp = client.get("/api/data/metadata")
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["datasets"]) == len(data_mod.DATASETS)

    def test_unknown_dataset_metadata_returns_404(self, client: TestClient) -> None:
        resp = client.get("/api/data/nonexistent/metadata")
        assert resp.status_code == 404

    def test_all_metadata_degrades_on_missing_csv_not_503(self, client: TestClient) -> None:
        """One missing CSV must not 503 the whole catalog (or hide all citations)."""
        missing = "wealth-shares"
        (data_mod.DATA_DIR / data_mod.DATASETS[missing]).unlink()
        data_mod._metadata_cache.clear()

        resp = client.get("/api/data/metadata")
        assert resp.status_code == 200  # whole catalog stays up
        by_name = {d["name"]: d for d in resp.json()["datasets"]}
        assert len(by_name) == len(data_mod.DATASETS)

        # The missing dataset degrades but KEEPS its source citation.
        gone = by_name[missing]
        assert gone["available"] is False
        assert gone["row_count"] is None
        assert gone["columns"] == []
        assert gone["last_updated"] is None  # file gone -> no mtime
        assert gone["data_type"] is None  # no sidecar
        assert gone["source"] == "World Inequality Database"
        assert gone["source_url"].startswith("http")

        # A present dataset is still fully available.
        present = next(d for n, d in by_name.items() if n != missing)
        assert present["available"] is True
        assert present["row_count"] == 5

    def test_all_metadata_degrades_on_corrupt_csv_not_503(self, client: TestClient) -> None:
        """A present-but-unreadable CSV degrades that entry too (not just missing)."""
        corrupt = "wealth-shares"
        (data_mod.DATA_DIR / data_mod.DATASETS[corrupt]).write_text("", encoding="utf-8")  # empty -> EmptyDataError
        data_mod._metadata_cache.clear()

        resp = client.get("/api/data/metadata")
        assert resp.status_code == 200
        by_name = {d["name"]: d for d in resp.json()["datasets"]}
        bad = by_name[corrupt]
        assert bad["available"] is False
        assert bad["row_count"] is None
        assert bad["source"] == "World Inequality Database"  # citation still served

    def test_single_metadata_stays_strict_on_missing_csv(self, client: TestClient) -> None:
        """The single-dataset endpoint still fails loudly (503) — only the catalog degrades."""
        (data_mod.DATA_DIR / data_mod.DATASETS["wealth-shares"]).unlink()
        data_mod._metadata_cache.clear()
        resp = client.get("/api/data/wealth-shares/metadata")
        assert resp.status_code == 503

    def test_metadata_includes_source_url(self, client: TestClient) -> None:
        resp = client.get("/api/data/wealth-shares/metadata")
        body = resp.json()
        assert body["source_url"].startswith("http")
        assert body["access_date"]


class TestPaginatedData:
    def test_default_pagination(self, client: TestClient) -> None:
        resp = client.get("/api/data/wealth-shares")
        assert resp.status_code == 200
        body = resp.json()
        assert body["page"] == 1
        assert body["total"] == 5
        assert body["total_pages"] == 1
        assert len(body["data"]) == 5

    def test_custom_page_and_limit(self, client: TestClient) -> None:
        resp = client.get("/api/data/wealth-shares?page=1&limit=2")
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["data"]) == 2
        assert body["total_pages"] == 3

    def test_second_page(self, client: TestClient) -> None:
        resp = client.get("/api/data/wealth-shares?page=2&limit=2")
        body = resp.json()
        assert body["page"] == 2
        assert len(body["data"]) == 2
        assert body["data"][0]["year"] == 2020

    def test_last_page_partial(self, client: TestClient) -> None:
        resp = client.get("/api/data/wealth-shares?page=3&limit=2")
        body = resp.json()
        assert len(body["data"]) == 1

    def test_page_beyond_range_returns_empty(self, client: TestClient) -> None:
        resp = client.get("/api/data/wealth-shares?page=99&limit=100")
        body = resp.json()
        assert body["data"] == []

    def test_invalid_page_returns_422(self, client: TestClient) -> None:
        resp = client.get("/api/data/wealth-shares?page=0")
        assert resp.status_code == 422

    def test_limit_too_large_returns_422(self, client: TestClient) -> None:
        resp = client.get("/api/data/wealth-shares?limit=9999")
        assert resp.status_code == 422

    def test_unknown_dataset_returns_404(self, client: TestClient) -> None:
        resp = client.get("/api/data/does-not-exist")
        assert resp.status_code == 404

    def test_missing_file_returns_503(
        self, client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        monkeypatch.setattr(data_mod, "DATA_DIR", empty_dir)
        resp = client.get("/api/data/wealth-shares")
        assert resp.status_code == 503


class TestDataTypeSidecar:
    """_get_data_type distinguishes an absent sidecar from a corrupt one."""

    def test_corrupt_sidecar_logs_and_returns_none(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        """A present-but-unparseable sidecar warns (not silent) and degrades to None.

        Silently dropping it would hide the data-honesty caveat for an illustrative
        dataset — the exact failure the project guards against.
        """
        # The "wealthlens" logger sets propagate=False (logging_config), so caplog
        # (rooted at the real root logger) only sees these records with propagation on.
        monkeypatch.setattr(logging.getLogger("wealthlens"), "propagate", True)
        monkeypatch.setattr(data_mod, "DATA_DIR", tmp_path)
        name = next(iter(data_mod.DATASETS))
        sidecar = (tmp_path / data_mod.DATASETS[name]).with_suffix(".meta.json")
        sidecar.write_text("{ not valid json", encoding="utf-8")

        with caplog.at_level(logging.WARNING, logger="wealthlens.data"):
            result = data_mod._get_data_type(name)

        assert result is None
        assert "Corrupt data_type sidecar" in caplog.text

    def test_absent_sidecar_is_silent_none(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        """A genuinely absent sidecar returns None with NO warning (backward-compatible)."""
        monkeypatch.setattr(logging.getLogger("wealthlens"), "propagate", True)
        monkeypatch.setattr(data_mod, "DATA_DIR", tmp_path)
        name = next(iter(data_mod.DATASETS))

        with caplog.at_level(logging.WARNING, logger="wealthlens.data"):
            result = data_mod._get_data_type(name)

        assert result is None
        assert "sidecar" not in caplog.text
