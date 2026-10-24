"""Tests for BoE rates dataset API endpoints.

Verifies that the boe-rates dataset is registered, serves data
correctly, and returns proper metadata with source citations.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from app.main import app
from app.routers import data as data_module
from fastapi.testclient import TestClient

client = TestClient(app)


# ---------------------------------------------------------------------------
# Registration tests
# ---------------------------------------------------------------------------


def test_boe_rates_in_dataset_list() -> None:
    """boe-rates must appear in the dataset listing."""
    response = client.get("/api/data/")
    assert response.status_code == 200
    assert "boe-rates" in response.json()["datasets"]


def test_boe_rates_in_dataset_meta() -> None:
    """boe-rates must have metadata with source citation."""
    assert "boe-rates" in data_module.DATASET_META
    meta = data_module.DATASET_META["boe-rates"]
    assert "Bank of England" in meta["source"]
    assert "source_url" in meta
    assert "access_date" in meta


def test_boe_rates_keys_match() -> None:
    """DATASETS and DATASET_META must both contain boe-rates."""
    assert "boe-rates" in data_module.DATASETS
    assert "boe-rates" in data_module.DATASET_META


# ---------------------------------------------------------------------------
# Data endpoint tests (require CSV to exist)
# ---------------------------------------------------------------------------


def _csv_exists() -> bool:
    csv_path = data_module.DATA_DIR / data_module.DATASETS["boe-rates"]
    return csv_path.exists()


@pytest.mark.skipif(not _csv_exists(), reason="boe_rates.csv not found — run pipeline first")
def test_get_boe_rates_data() -> None:
    """GET /api/data/boe-rates should return paginated rate data."""
    response = client.get("/api/data/boe-rates")
    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    assert len(body["data"]) > 0
    assert "date" in body["data"][0]
    assert "bank_rate" in body["data"][0]


@pytest.mark.skipif(not _csv_exists(), reason="boe_rates.csv not found — run pipeline first")
def test_get_boe_rates_metadata() -> None:
    """GET /api/data/boe-rates/metadata should return source citation."""
    response = client.get("/api/data/boe-rates/metadata")
    assert response.status_code == 200
    meta = response.json()
    assert meta["name"] == "boe-rates"
    assert "Bank of England" in meta["source"]
    assert meta["row_count"] > 0
    assert "date" in meta["columns"]
    assert "bank_rate" in meta["columns"]


# ---------------------------------------------------------------------------
# Missing CSV tests (always run)
# ---------------------------------------------------------------------------


def test_boe_rates_503_when_csv_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """boe-rates should return 503 when the CSV does not exist."""
    monkeypatch.setattr(data_module, "DATA_DIR", tmp_path)
    monkeypatch.setattr(data_module, "_metadata_cache", {})

    response = client.get("/api/data/boe-rates")
    assert response.status_code == 503
    body = response.json()
    message = body.get("error", {}).get("message", body.get("detail", ""))
    assert message


@pytest.mark.parametrize("use_sidecar", [True, False])
def test_boe_api_citation_matches_committed_static_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, use_sidecar: bool,
) -> None:
    """Exercise response serialization so neither source nor its access date is lost."""
    public = Path(__file__).resolve().parents[2] / "frontend/public/data"
    published = json.loads((public / "boe-rates-metadata.json").read_text())
    (tmp_path / "boe_rates.csv").write_bytes((public / "boe-rates.csv").read_bytes())
    if use_sidecar:
        (tmp_path / "boe_rates.meta.json").write_text(json.dumps(published))
    monkeypatch.setattr(data_module, "DATA_DIR", tmp_path)
    monkeypatch.setattr(data_module, "_metadata_cache", {})
    response = client.get("/api/data/boe-rates/metadata")
    assert response.status_code == 200
    for key in ("description", "source", "source_url", "access_date", "sources"):
        assert response.json()[key] == published[key]
    catalog = client.get("/api/data/metadata").json()["datasets"]
    entry = next(item for item in catalog if item["name"] == "boe-rates")
    assert entry["sources"] == published["sources"]


def test_boe_api_prefers_current_pipeline_citation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A later pipeline must override the committed last-good source order and date."""
    public = Path(__file__).resolve().parents[2] / "frontend/public/data"
    sidecar = json.loads((public / "boe-rates-metadata.json").read_text())
    sidecar["sources"].reverse()
    sidecar["access_date"] = sidecar["sources"][0]["access_date"] = "recorded-pipeline-access-date"
    (tmp_path / "boe_rates.meta.json").write_text(json.dumps(sidecar))
    (tmp_path / "boe_rates.csv").write_bytes((public / "boe-rates.csv").read_bytes())
    monkeypatch.setattr(data_module, "DATA_DIR", tmp_path)
    monkeypatch.setattr(data_module, "_metadata_cache", {})
    response = client.get("/api/data/boe-rates/metadata")
    assert response.status_code == 200
    assert response.json()["sources"] == sidecar["sources"]
    assert response.json()["access_date"] == sidecar["access_date"]
    assert response.json()["source"] == " / ".join(source["name"] for source in sidecar["sources"])
