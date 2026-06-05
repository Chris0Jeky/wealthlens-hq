"""Focused regression test for the HMRC CGT NaN handling.

``fetch_hmrc_stats.process`` parses the gains and taxpayer-count cells out of an
HMRC table. Two distinct correctness requirements:

* A blank/NaN **gains** cell must DROP the row — gains is the published metric, and
  a NaN gains would leak into ``total_gains_millions`` / ``share_of_gains_pct``.
* A blank/suppressed **taxpayer-count** cell must KEEP the row (HMRC suppresses some
  bands' counts for disclosure control while still publishing the gains). Dropping it
  would discard valid gains data; the count is recorded as NaN (the honest
  "suppressed" representation) for that band only.

The parse is inline inside ``process()``, so we exercise it by monkeypatching the
two pandas Excel readers it calls and pointing ``PROCESSED_DIR`` at a tmp dir.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import fetch_hmrc_stats


class _FakeExcelFile:
    """Stand-in for ``pd.ExcelFile`` exposing only the ``sheet_names`` used."""

    def __init__(self, *_args: object, **_kwargs: object) -> None:
        self.sheet_names = ["Contents", "2_1a"]


def _raw_frame() -> pd.DataFrame:
    """Build a raw HMRC-style sheet exercising both NaN scenarios.

    Layout mirrors what ``process()`` expects:
      col 0 = band lower limit, col 1 = num individuals (thousands),
      col 2 = gains (£m), col 3 = tax (£m).
    The header row must contain both "range" and "number" for detection.
    """
    rows = [
        ["Notes", None, None, None],
        ["Range of gain", "Number of individuals", "Amounts of gains", "Amounts of tax"],
        # Valid band — finite count + gains.
        ["10000", "30", "10000", "1000"],
        # SUPPRESSED taxpayer count (pandas NaN) but PUBLISHED gains: the row must be
        # KEPT with its gains, count recorded as NaN (HMRC disclosure suppression).
        ["500000", float("nan"), "12000", "2400"],
        # Blank GAINS cell: the row must be DROPPED (gains is the published metric).
        ["700000", "8", float("nan"), "1600"],
        # Another valid band so the frame is non-empty.
        ["1000000", "5", "25000", "5000"],
        # Totals row.
        ["All", "35", "47000", "8400"],
    ]
    return pd.DataFrame(rows)


@pytest.fixture()
def _processed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> pd.DataFrame:
    monkeypatch.setattr(fetch_hmrc_stats.pd, "ExcelFile", _FakeExcelFile)
    monkeypatch.setattr(fetch_hmrc_stats.pd, "read_excel", lambda *_a, **_k: _raw_frame())
    monkeypatch.setattr(fetch_hmrc_stats, "PROCESSED_DIR", tmp_path)
    return fetch_hmrc_stats.process({"table2": tmp_path / "fake.ods"})


def test_blank_gains_row_is_dropped(_processed: pd.DataFrame) -> None:
    """A band with a blank (NaN) gains cell is dropped, never published as NaN gains."""
    assert 700000 not in _processed["band_lower"].tolist(), "blank-gains band must be dropped"
    assert not _processed["total_gains_millions"].isna().any(), (
        "total_gains_millions (the published metric) must contain no NaN"
    )


def test_suppressed_count_band_is_kept_with_gains(_processed: pd.DataFrame) -> None:
    """A band with a suppressed (blank) taxpayer count keeps its published gains."""
    band = _processed[_processed["band_lower"] == 500000.0]
    assert len(band) == 1, "suppressed-count band must be KEPT (its gains are valid)"
    assert band["total_gains_millions"].iloc[0] == pytest.approx(12000.0)
    # The count itself is the honest 'suppressed' NaN for that band only.
    assert pd.isna(band["num_taxpayers_thousands"].iloc[0])


def test_valid_bands_survive(_processed: pd.DataFrame) -> None:
    assert set(_processed["band_lower"].tolist()) == {10000.0, 500000.0, 1000000.0}
