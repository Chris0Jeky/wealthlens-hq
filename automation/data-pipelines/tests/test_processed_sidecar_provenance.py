"""Lock the sidecar `data_type` provenance the always-static pipelines WRITE.

The dashboard's data-honesty mechanism keys on a `data_type` string in each
``data/processed/{dataset}.meta.json`` sidecar (read by the backend
``_get_data_type`` and surfaced via ``/metadata``). Recognised vocabulary:

  - ``live_ons``             — fetched live from the official source;
  - ``illustrative_fallback`` — an illustrative composite (example figures);
  - ``static_published``      — REAL published figures compiled statically (not a
                               live fetch, not invented).

The sidecars themselves are gitignored build artifacts regenerated at deploy
time, so the load-bearing thing to test is the PIPELINE WRITER: child poverty and
generational wealth previously wrote no ``data_type`` (child poverty wrote
``is_fallback`` instead), so the deployed API reported ``data_type: null`` —
indistinguishable from "no provenance" and unable to flag the data as non-live.
These tests exercise the real writers into a tmp dir and assert they now emit the
honest ``static_published`` marker. NOT ``illustrative_fallback``: these are real
DWP / Resolution Foundation / ONS figures, and mislabelling them would let the UI
caption real data as "example data".
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import fetch_child_poverty
import fetch_generational_wealth

RECOGNISED_DATA_TYPES = {"live_ons", "illustrative_fallback", "static_published"}


def test_child_poverty_writer_emits_static_published(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """process() writes data_type=static_published for the always-fallback dataset."""
    monkeypatch.setattr(fetch_child_poverty, "PROCESSED_DIR", tmp_path)
    df_raw = pd.DataFrame(fetch_child_poverty.FALLBACK_DATA)

    fetch_child_poverty.process(df_raw, is_fallback=True)

    meta = json.loads((tmp_path / "child_poverty_by_region.meta.json").read_text(encoding="utf-8"))
    assert meta["data_type"] == "static_published", f"got {meta.get('data_type')!r}"
    assert meta["data_type"] in RECOGNISED_DATA_TYPES
    # is_fallback is retained for backward-compat; data_type is the contract key.
    assert meta["is_fallback"] is True


def test_generational_writer_emits_static_published(tmp_path: Path) -> None:
    """_write_meta emits data_type=static_published for the curated static dataset."""
    csv_path = tmp_path / "generational_wealth_gap.csv"
    fetch_generational_wealth._write_meta(csv_path)

    meta = json.loads(csv_path.with_suffix(".meta.json").read_text(encoding="utf-8"))
    assert meta["data_type"] == "static_published", f"got {meta.get('data_type')!r}"
    assert meta["data_type"] in RECOGNISED_DATA_TYPES
