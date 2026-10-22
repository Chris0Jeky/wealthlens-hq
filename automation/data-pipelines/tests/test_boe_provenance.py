"""BoE fallback provenance must survive processing and publication."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import Mock

import fetch_boe_rates as boe
import pandas as pd
import pytest
import requests

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "projects/wealthlens-dashboard/backend"))

import generate_static_api as static_api  # noqa: E402
from app.routers import data as api  # noqa: E402


@pytest.fixture()
def pipeline_dirs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(boe, "RAW_DIR", tmp_path / "raw")
    monkeypatch.setattr(boe, "PROCESSED_DIR", tmp_path / "processed")
    monkeypatch.setattr(boe, "CHART_DIR", tmp_path / "charts")
    return tmp_path


def test_failed_fetch_labels_fallback_through_api_and_static_export(
    pipeline_dirs: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    def unavailable(*args: object, **kwargs: object) -> None:
        raise requests.ConnectionError("offline regression fixture")

    monkeypatch.setattr(boe.requests, "get", unavailable)
    frame = boe.process(boe.fetch())
    processed = pipeline_dirs / "processed"
    sidecar = json.loads((processed / "boe_rates.meta.json").read_text())
    assert sidecar["data_type"] == "illustrative_fallback"
    assert frame["data_type"].eq("illustrative_fallback").all()

    monkeypatch.setattr(api, "DATA_DIR", processed)
    monkeypatch.setattr(api, "_metadata_cache", {})
    assert api._build_metadata("boe-rates")["data_type"] == "illustrative_fallback"

    output = pipeline_dirs / "public"
    monkeypatch.setattr(static_api, "DATA_DIR", processed)
    monkeypatch.setattr(static_api, "OUT_DIR", output)
    monkeypatch.setattr(static_api, "DATASETS", {"boe-rates": "boe_rates.csv"})
    monkeypatch.setattr(static_api, "generate_simulator_static", lambda: 0)
    static_api.main()
    metadata = json.loads((output / "boe-rates-metadata.json").read_text())
    assert metadata["data_type"] == "illustrative_fallback"
    catalog = json.loads((output / "all-metadata.json").read_text())
    assert catalog["datasets"][0]["data_type"] == "illustrative_fallback"
    assert pd.read_csv(output / "boe-rates.csv")["data_type"].eq("illustrative_fallback").all()
    assert all(
        row["data_type"] == "illustrative_fallback"
        for row in json.loads((output / "boe-rates.json").read_text())["data"]
    )
    # More fallback rows must never turn an example into an official chart.
    boe.build_chart(pd.concat([frame, frame]))
    chart = (pipeline_dirs / "charts/boe_rates.html").read_text(encoding="utf-8")
    assert "ILLUSTRATIVE FALLBACK DATA" in chart
    assert "not published statistics" in chart


def test_successful_fetch_records_source_without_row_count_heuristic(
    pipeline_dirs: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Use existing bytes to test transport provenance, never invent official figures.
    # This is a mocked response, not evidence that the fixture is official data.
    raw_dir = pipeline_dirs / "raw"
    raw_dir.mkdir()
    fixture = boe._write_fallback(raw_dir / "fixture.csv")
    frame = pd.read_csv(fixture).drop(columns=["data_type"], errors="ignore").head(1)
    response = Mock(content=frame.to_csv(index=False).encode())
    monkeypatch.setattr(boe.requests, "get", Mock(return_value=response))

    result = boe.process(boe.fetch())
    sidecar = json.loads((pipeline_dirs / "processed/boe_rates.meta.json").read_text())
    assert sidecar["data_type"] == "live_ons"
    assert sidecar["access_date"] == boe.ACCESS_DATE
    assert sidecar["source_url"] == boe.BOE_IADB_URL
    assert "Illustrative" not in sidecar["provenance_note"]
    assert result["data_type"].eq("live_ons").all()
    boe.build_chart(result)
    assert "ILLUSTRATIVE FALLBACK DATA" not in (pipeline_dirs / "charts/boe_rates.html").read_text()


@pytest.mark.parametrize("sidecar_text", [None, "{ corrupt", "[]", '{"data_type":"live_ons"}'])
def test_missing_corrupt_or_conflicting_raw_provenance_never_becomes_official(
    pipeline_dirs: Path, sidecar_text: str | None,
) -> None:
    raw_dir = pipeline_dirs / "raw"
    raw_dir.mkdir()
    raw = boe._write_fallback(raw_dir / "input.csv")
    sidecar = raw.with_suffix(".meta.json")
    if sidecar_text is None:
        sidecar.unlink(missing_ok=True)
    else:
        sidecar.write_text(sidecar_text)
    result = boe.process(raw)
    assert result["data_type"].isin(["illustrative_fallback", "unverified"]).all()
    meta = json.loads((pipeline_dirs / "processed/boe_rates.meta.json").read_text())
    assert meta["data_type"] in {"illustrative_fallback", "unverified"}


def test_committed_boe_artifacts_preserve_fallback_provenance(pipeline_dirs: Path) -> None:
    public = ROOT / "projects/wealthlens-dashboard/frontend/public/data"
    metadata = json.loads((public / "boe-rates-metadata.json").read_text())
    assert metadata["data_type"] in {"illustrative_fallback", "live_ons"}
    published = pd.read_csv(public / "boe-rates.csv")
    assert published["data_type"].eq(metadata["data_type"]).all()
    fallback = pd.read_csv(boe._write_fallback(pipeline_dirs / "fallback.csv"))
    expected = fallback.rename(columns={"DATE": "date", "IUDBEDR": "bank_rate", "D7BT": "cpi_annual"})
    values = ["date", "bank_rate", "cpi_annual"]
    if published[values].equals(expected[values]):
        assert metadata["data_type"] == "illustrative_fallback"
    template = json.loads((ROOT / "automation/data-pipelines/metadata/boe_rates.meta.json").read_text())
    assert template["data_type"] == "illustrative_fallback"


def test_missing_boe_sidecar_is_unverified_in_both_publication_paths(
    pipeline_dirs: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    frame = boe.process(boe._write_fallback(pipeline_dirs / "input.csv"))
    processed = pipeline_dirs / "processed"
    csv_path = processed / "boe_rates.csv"
    csv_path.with_suffix(".meta.json").unlink()
    monkeypatch.setattr(api, "DATA_DIR", processed)
    monkeypatch.setattr(api, "_metadata_cache", {})
    assert api._build_metadata("boe-rates")["data_type"] == "unverified"
    assert static_api._read_data_type(csv_path, frame.to_dict("records")) == "unverified"
