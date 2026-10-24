"""Do not certify an unverified fallback as official published statistics.

Generational wealth keeps its existing static-published contract. Child poverty
now refuses the legacy constants and fetches the official HBAI tables instead.
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


def test_child_poverty_writer_refuses_unverified_fallback(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A legacy fallback flag cannot bypass the official-source requirement."""
    monkeypatch.setattr(fetch_child_poverty, "PROCESSED_DIR", tmp_path)
    with pytest.raises(ValueError, match="fallback"):
        fetch_child_poverty.process(pd.DataFrame(), is_fallback=True)
    assert not list(tmp_path.iterdir())


def test_generational_writer_emits_static_published(tmp_path: Path) -> None:
    """_write_meta emits data_type=static_published for the curated static dataset."""
    csv_path = tmp_path / "generational_wealth_gap.csv"
    fetch_generational_wealth._write_meta(csv_path)

    meta = json.loads(csv_path.with_suffix(".meta.json").read_text(encoding="utf-8"))
    assert meta["data_type"] == "static_published", f"got {meta.get('data_type')!r}"
    assert meta["data_type"] in RECOGNISED_DATA_TYPES
