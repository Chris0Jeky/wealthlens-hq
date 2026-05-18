"""Tests for the wage-stagnation dataset endpoint."""

from __future__ import annotations

import importlib
import textwrap
from collections.abc import Generator
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

_SAMPLE_CSV = textwrap.dedent("""\
    year,real_weekly
    2008,520
    2024,504
""")


@pytest.fixture()
def csv_client(tmp_path: Path) -> Generator[TestClient, None, None]:
    csv_path = tmp_path / "wage_stagnation.csv"
    csv_path.write_text(_SAMPLE_CSV, encoding="utf-8")

    import app.routers.data as data_mod

    with patch.object(data_mod, "DATA_DIR", tmp_path):
        data_mod._metadata_cache.clear()
        import app.main as main_mod

        importlib.reload(main_mod)
        yield TestClient(main_mod.app)


def test_dataset_in_list(csv_client: TestClient) -> None:
    response = csv_client.get("/api/data/")
    assert response.status_code == 200
    assert "wage-stagnation" in response.json()["datasets"]


def test_metadata_has_source_and_schema(csv_client: TestClient) -> None:
    response = csv_client.get("/api/data/wage-stagnation/metadata")
    assert response.status_code == 200
    meta = response.json()
    assert meta["source_url"].startswith("https://www.ons.gov.uk/")
    assert meta["access_date"] == "2026-05-16"
    assert {"year", "real_weekly"}.issubset(set(meta["columns"]))


def test_returns_paginated_rows(csv_client: TestClient) -> None:
    response = csv_client.get("/api/data/wage-stagnation")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert body["data"][0] == {"year": 2008, "real_weekly": 520}
