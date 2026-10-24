"""BoE metadata must never lose the fallback dataset's provenance warning."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest
from app.main import app
from app.routers import data as api
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    ("sidecar", "marker", "expected"),
    [
        (None, "illustrative_fallback", "unverified"),
        (None, "live_ons", "unverified"),
        ("{ corrupt", "illustrative_fallback", "unverified"),
        ("[]", "illustrative_fallback", "unverified"),
        ('{"data_type":"live_ons"}', "illustrative_fallback", "unverified"),
        ('{"data_type":"illustrative_fallback"}', "illustrative_fallback", "illustrative_fallback"),
        ('{"data_type":"live_ons"}', "live_ons", "live_ons"),
    ],
)
def test_boe_metadata_provenance(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    sidecar: str | None, marker: str, expected: str,
) -> None:
    # Reuse committed figures verbatim. Only provenance markers vary here.
    public = Path(__file__).resolve().parents[2] / "frontend/public/data"
    frame = pd.read_csv(public / "boe-rates.csv")
    frame["data_type"] = marker
    csv_path = tmp_path / "boe_rates.csv"
    frame.to_csv(csv_path, index=False)
    if sidecar is not None:
        csv_path.with_suffix(".meta.json").write_text(sidecar, encoding="utf-8")
    monkeypatch.setattr(api, "DATA_DIR", tmp_path)
    monkeypatch.setattr(api, "_metadata_cache", {})
    client = TestClient(app)
    response = client.get("/api/data/boe-rates/metadata")
    assert response.status_code == 200
    assert response.json()["data_type"] == expected
    catalog = client.get("/api/data/metadata").json()["datasets"]
    assert next(meta for meta in catalog if meta["name"] == "boe-rates")["data_type"] == expected


def test_committed_boe_static_and_backend_provenance_agree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    public = Path(__file__).resolve().parents[2] / "frontend/public/data"
    metadata = json.loads((public / "boe-rates-metadata.json").read_text())
    (tmp_path / "boe_rates.csv").write_bytes((public / "boe-rates.csv").read_bytes())
    (tmp_path / "boe_rates.meta.json").write_text(json.dumps(metadata), encoding="utf-8")
    monkeypatch.setattr(api, "DATA_DIR", tmp_path)
    monkeypatch.setattr(api, "_metadata_cache", {})
    response = TestClient(app).get("/api/data/boe-rates/metadata")
    assert response.status_code == 200
    assert response.json()["data_type"] == metadata["data_type"]
