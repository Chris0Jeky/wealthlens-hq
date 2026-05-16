"""Tests for the dataset summary statistics endpoint."""

from __future__ import annotations

from pathlib import Path

import pytest
from app.main import app
from app.routers import data as data_mod
from fastapi.testclient import TestClient

CSV_CONTENT = """year,value,region
2020,100.5,London
2021,200.75,London
2022,300.0,Manchester
"""

CSV_EMPTY_NUMERIC = """name,region
Alice,London
Bob,Manchester
"""

CSV_ALL_NULL_NUMERIC = """year,value
2020,
2021,
2022,
"""


@pytest.fixture(autouse=True)
def _fake_data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    csv_file = tmp_path / "wid_wealth_shares_gb.csv"
    csv_file.write_text(CSV_CONTENT, encoding="utf-8")
    monkeypatch.setattr(data_mod, "DATA_DIR", tmp_path)
    data_mod._metadata_cache.clear()
    data_mod._summary_cache.clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_summary_returns_stats(client: TestClient) -> None:
    resp = client.get("/api/data/wealth-shares/summary")
    assert resp.status_code == 200
    body = resp.json()
    assert body["dataset"] == "wealth-shares"
    assert body["row_count"] == 3
    assert len(body["numeric_columns"]) >= 1

    year_col = next(c for c in body["numeric_columns"] if c["column"] == "year")
    assert year_col["count"] == 3
    assert year_col["min"] == 2020.0
    assert year_col["max"] == 2022.0


def test_summary_mean_and_median(client: TestClient) -> None:
    resp = client.get("/api/data/wealth-shares/summary")
    body = resp.json()
    value_col = next(c for c in body["numeric_columns"] if c["column"] == "value")
    assert value_col["mean"] == pytest.approx(200.4167, rel=1e-3)
    assert value_col["median"] == 200.75


def test_summary_unknown_dataset(client: TestClient) -> None:
    resp = client.get("/api/data/nonexistent/summary")
    assert resp.status_code == 404


def test_summary_no_numeric_columns(
    client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    csv_file = tmp_path / "wid_wealth_shares_gb.csv"
    csv_file.write_text(CSV_EMPTY_NUMERIC, encoding="utf-8")
    monkeypatch.setattr(data_mod, "DATA_DIR", tmp_path)
    data_mod._metadata_cache.clear()

    resp = client.get("/api/data/wealth-shares/summary")
    assert resp.status_code == 200
    body = resp.json()
    assert body["numeric_columns"] == []
    assert body["row_count"] == 2


def test_summary_route_not_shadowed_by_catchall(client: TestClient) -> None:
    """Verify /summary is reached, not caught by /{dataset_name}."""
    resp = client.get("/api/data/wealth-shares/summary")
    assert resp.status_code == 200
    assert "numeric_columns" in resp.json()


def test_summary_all_null_column(
    client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """All-null numeric column returns count=0 and None for all stats."""
    csv_file = tmp_path / "wid_wealth_shares_gb.csv"
    csv_file.write_text(CSV_ALL_NULL_NUMERIC, encoding="utf-8")
    monkeypatch.setattr(data_mod, "DATA_DIR", tmp_path)
    data_mod._metadata_cache.clear()
    data_mod._summary_cache.clear()

    resp = client.get("/api/data/wealth-shares/summary")
    assert resp.status_code == 200
    body = resp.json()
    value_col = next(c for c in body["numeric_columns"] if c["column"] == "value")
    assert value_col["count"] == 0
    assert value_col["mean"] is None
    assert value_col["std"] is None
    assert value_col["min"] is None
    assert value_col["max"] is None
    assert value_col["median"] is None
