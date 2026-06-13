"""Tests for the productivity-pay dataset endpoint.

Verifies that the /api/data/productivity-pay endpoint returns the
expected structure, metadata, and pagination behaviour.

Tests use a temporary CSV fixture so they always run, even when the
pipeline has not been executed (no silent 503 skips).
"""

from __future__ import annotations

import importlib
import json
import textwrap
from collections.abc import Generator
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

# Sample CSV content with the expected schema.
_SAMPLE_CSV = textwrap.dedent("""\
    year,productivity_index,pay_index,gap_pct
    1997,100.0,100.0,0.0
    1998,102.5,102.5,0.0
    1999,105.0,105.0,0.0
    2000,108.0,107.0,0.9
    2001,110.5,110.0,0.5
    2002,113.0,112.0,0.9
    2003,116.0,113.5,2.2
    2004,118.5,114.5,3.5
    2005,120.0,115.0,4.3
    2006,122.5,116.0,5.6
""")


@pytest.fixture()
def csv_client(tmp_path: Path) -> Generator[TestClient, None, None]:
    """Create a test client with a temporary productivity-pay CSV.

    Patches the data router's DATA_DIR to point at the temp directory
    so tests exercise real logic without needing pipeline output.
    """
    # Write the sample CSV into the temp dir
    csv_path = tmp_path / "productivity_pay_gap.csv"
    csv_path.write_text(_SAMPLE_CSV, encoding="utf-8")

    # Patch DATA_DIR and clear the metadata cache, then reload
    import app.routers.data as data_mod

    with patch.object(data_mod, "DATA_DIR", tmp_path):
        data_mod._metadata_cache.clear()
        import app.main as main_mod
        importlib.reload(main_mod)
        yield TestClient(main_mod.app)


class TestProductivityPayMetadata:
    """Metadata endpoint tests for productivity-pay dataset."""

    def test_dataset_in_list(self, csv_client: TestClient) -> None:
        """productivity-pay should appear in the dataset listing."""
        response = csv_client.get("/api/data/")
        assert response.status_code == 200
        data = response.json()
        assert "productivity-pay" in data["datasets"]

    def test_metadata_returns_source_citation(self, csv_client: TestClient) -> None:
        """Metadata should include source, source_url, and access_date."""
        response = csv_client.get("/api/data/productivity-pay/metadata")
        assert response.status_code == 200
        meta = response.json()
        assert meta["name"] == "productivity-pay"
        assert "ONS" in meta["source"]
        assert "source_url" in meta
        assert "access_date" in meta
        assert "columns" in meta
        assert "row_count" in meta

    def test_metadata_columns_match_schema(self, csv_client: TestClient) -> None:
        """Metadata columns should include the expected CSV columns."""
        response = csv_client.get("/api/data/productivity-pay/metadata")
        assert response.status_code == 200
        meta = response.json()
        expected = {"year", "productivity_index", "pay_index", "gap_pct"}
        assert expected.issubset(set(meta["columns"]))


def _client_with_sidecar(
    tmp_path: Path, data_type: str | None
) -> Generator[TestClient, None, None]:
    """Build a TestClient whose productivity-pay CSV optionally has a sidecar.

    Writes the sample CSV to *tmp_path* and, when *data_type* is not None,
    writes a ``productivity_pay_gap.meta.json`` sidecar recording that
    provenance (mirroring what the pipeline emits). Patches DATA_DIR and
    clears the metadata cache so the reloaded app reads from *tmp_path*.
    """
    csv_path = tmp_path / "productivity_pay_gap.csv"
    csv_path.write_text(_SAMPLE_CSV, encoding="utf-8")
    if data_type is not None:
        sidecar = csv_path.with_suffix(".meta.json")
        sidecar.write_text(
            json.dumps({"data_type": data_type, "csv_file": csv_path.name}),
            encoding="utf-8",
        )

    import app.routers.data as data_mod

    with patch.object(data_mod, "DATA_DIR", tmp_path):
        data_mod._metadata_cache.clear()
        import app.main as main_mod
        importlib.reload(main_mod)
        yield TestClient(main_mod.app)


class TestProductivityPayDataType:
    """data_type provenance is surfaced (or null) in the metadata response.

    Proves the data-honesty contract end-to-end through the backend: the
    sidecar's data_type flows into GET /{name}/metadata so the frontend can
    show an illustrative-data caveat. data_type is read UNCACHED, so each
    case gets its own client/sidecar state.
    """

    def test_data_type_none_without_sidecar(self, tmp_path: Path) -> None:
        """No sidecar -> data_type is null (backward-compatible default)."""
        for client in _client_with_sidecar(tmp_path, data_type=None):
            response = client.get("/api/data/productivity-pay/metadata")
            assert response.status_code == 200
            assert response.json()["data_type"] is None

    def test_data_type_illustrative_fallback(self, tmp_path: Path) -> None:
        """An illustrative_fallback sidecar surfaces as data_type."""
        for client in _client_with_sidecar(tmp_path, data_type="illustrative_fallback"):
            response = client.get("/api/data/productivity-pay/metadata")
            assert response.status_code == 200
            assert response.json()["data_type"] == "illustrative_fallback"

    def test_data_type_live_ons(self, tmp_path: Path) -> None:
        """A live_ons sidecar surfaces as data_type."""
        for client in _client_with_sidecar(tmp_path, data_type="live_ons"):
            response = client.get("/api/data/productivity-pay/metadata")
            assert response.status_code == 200
            assert response.json()["data_type"] == "live_ons"


class TestProductivityPayData:
    """Data retrieval tests for the productivity-pay dataset."""

    def test_returns_paginated_data(self, csv_client: TestClient) -> None:
        """GET /api/data/productivity-pay should return paginated rows."""
        response = csv_client.get("/api/data/productivity-pay")
        assert response.status_code == 200
        body = response.json()
        assert "data" in body
        assert "page" in body
        assert "total" in body
        assert body["page"] == 1
        assert body["total"] == 10

    def test_row_structure(self, csv_client: TestClient) -> None:
        """Each row should have year, productivity_index, pay_index, gap_pct."""
        response = csv_client.get("/api/data/productivity-pay")
        assert response.status_code == 200
        rows = response.json()["data"]
        assert len(rows) > 0

        row = rows[0]
        assert "year" in row
        assert "productivity_index" in row
        assert "pay_index" in row
        assert "gap_pct" in row

    def test_pagination_limit(self, csv_client: TestClient) -> None:
        """Setting limit=5 should return at most 5 rows."""
        response = csv_client.get("/api/data/productivity-pay?limit=5")
        assert response.status_code == 200
        body = response.json()
        assert len(body["data"]) == 5
        assert body["limit"] == 5


class TestProductivityPayMissing:
    """Behaviour when the CSV has not been generated yet."""

    def test_returns_503_when_csv_missing(self, tmp_path: Path) -> None:
        """Should return 503 with helpful message when CSV does not exist."""
        # Point DATA_DIR at an empty tmp dir (no CSV)
        import app.routers.data as data_mod

        with patch.object(data_mod, "DATA_DIR", tmp_path):
            data_mod._metadata_cache.clear()
            import app.main as main_mod
            importlib.reload(main_mod)
            client = TestClient(main_mod.app)

            response = client.get("/api/data/productivity-pay")
            assert response.status_code == 503
            body = response.json()
            message = body.get("error", {}).get("message", body.get("detail", ""))
            assert message


class TestProcessLogic:
    """Unit tests for the pipeline process() function."""

    def test_process_returns_fallback_when_inputs_none(
        self, pipeline_module: ModuleType,
    ) -> None:
        """process() should return fallback data when any input is None."""
        df, is_fallback = pipeline_module.process(None, None, None)
        assert is_fallback is True
        assert len(df) > 0
        assert "year" in df.columns
        assert "productivity_index" in df.columns
        assert "pay_index" in df.columns
        assert "gap_pct" in df.columns

    def test_process_handles_zero_cpih(
        self, pipeline_module: ModuleType,
    ) -> None:
        """process() should not produce inf when CPIH is 0."""
        import pandas as pd

        prod_df = pd.DataFrame({"year": [1997, 1998], "value": [100.0, 105.0]})
        awe_df = pd.DataFrame({"year": [1997, 1998], "value": [400.0, 420.0]})
        # CPIH with a zero value — should be dropped, not cause inf
        cpih_df = pd.DataFrame({"year": [1997, 1998], "value": [100.0, 0.0]})

        df, _is_fallback = pipeline_module.process(prod_df, awe_df, cpih_df)
        # With only one valid CPIH row (1997), the base year exists so we
        # get a 1-row result with the base year normalised to 100.
        assert not df["productivity_index"].isin([float("inf")]).any()
        assert not df["pay_index"].isin([float("inf")]).any()
