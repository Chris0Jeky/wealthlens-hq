"""Call-site regression test for the ``to_finite_float`` NaN guard in fetch_ons_housing.

#365 follow-up. ``fetch_ons_housing.process`` walks a region x year grid out of ONS
sheet ``1c`` and, for each cell, does ``ratio = to_finite_float(cell)`` (L90). This
file locks that one call site so a future refactor that swaps in a bare ``float()``
(which would let an ``inf`` / ``"nan"`` source cell parse and leak into the published
``ons_housing_affordability_by_region.csv``) is caught here, not in production data.

Discriminating signal: this is a DROP call site. A cell that HAD content but does not
parse to a finite number is dropped — no row is recorded for it (genuinely-empty grid
cells, which pandas reads as ``NaN``, are silently skipped). So the published ``ratio``
column should carry no non-finite value *at all*; only a bypassed bare ``float()`` lets
``inf``/``nan`` survive into a published row. We assert on both the returned frame and
the CSV actually written to ``PROCESSED_DIR``.

The parse is inline inside ``process()``, so we exercise it by monkeypatching the
``pandas`` Excel reader it calls (to return a faithful minimal sheet-``1c`` frame) and
pointing ``PROCESSED_DIR`` at a tmp dir.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import fetch_ons_housing


def _has_nonfinite(series: pd.Series) -> bool:
    """True if any entry is NaN/None or +/-inf.

    The housing parser drops a bad cell entirely (it records no row), so a surviving
    ``ratio`` carries no legitimate missing value — any NaN/inf here can only be a leak
    from a bypassed ``to_finite_float``. Vectorised; ``isin`` matches both ``np.inf``
    and ``float('inf')``, ``isna`` covers both ``None`` and ``NaN``.
    """
    return bool(series.isna().any() or series.isin([float("inf"), float("-inf")]).any())


def _sheet_1c(rows: list[list[object]]) -> pd.DataFrame:
    """Build a positional (``header=None``) sheet-``1c`` frame.

    Mirrors what ``process()`` reads: row 0 = title, row 1 = header
    (col 0 = Code, col 1 = Name, col 2+ = year columns), rows 2+ = region data
    (code, name, ratio cells).
    """
    header = ["Code", "Name", 1997, 1998]
    title: list[object] = ["House price to workplace-based earnings ratio", None, None, None]
    return pd.DataFrame([title, header, *rows])


def _run_process(
    frame: pd.DataFrame, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> pd.DataFrame:
    """Drive ``process()`` over ``frame`` with output redirected to ``tmp_path``."""
    monkeypatch.setattr(fetch_ons_housing.pd, "read_excel", lambda *_a, **_k: frame)
    monkeypatch.setattr(fetch_ons_housing, "PROCESSED_DIR", tmp_path)
    return fetch_ons_housing.process(tmp_path / "fake.xlsx")


def test_present_but_nonfinite_cells_are_dropped_not_published(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An ``inf``/``"nan"`` cell with content is dropped; the published ratios stay finite.

    ``inf`` and the text ``"nan"`` both parse under a bare ``float()`` (the mutation),
    but ``to_finite_float`` returns ``None`` for them, so the cell yields no row. The
    valid cells in the same region survive.
    """
    frame = _sheet_1c(
        [
            ["E12000007", "London", 8.0, "inf"],  # 1998 = inf -> dropped (no row)
            ["E12000001", "North East", 4.5, 5.0],  # both valid
            ["E12000008", "South East", "nan", 9.2],  # 1997 = text "nan" -> dropped
        ]
    )
    df = _run_process(frame, tmp_path, monkeypatch)

    # The published metric carries no non-finite value at all (DROP call site).
    assert not _has_nonfinite(df["ratio"])

    # The bad (region, year) cells produced no row; the valid ones did.
    pairs = set(zip(df["region"], df["year"], strict=True))
    assert ("London", 1998) not in pairs  # inf cell dropped
    assert ("South East", 1997) not in pairs  # "nan" cell dropped
    assert {("London", 1997), ("North East", 1997), ("North East", 1998), ("South East", 1998)} == pairs

    # The artifact actually written to disk is finite too, not just the returned frame.
    csv_path = tmp_path / "ons_housing_affordability_by_region.csv"
    assert csv_path.exists()
    on_disk = pd.read_csv(csv_path)
    assert not _has_nonfinite(on_disk["ratio"])


def test_genuinely_empty_grid_cells_are_skipped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A blank (pandas ``NaN``) cell in the sparse grid is skipped, never published as NaN.

    Empty cells are expected in this sparse region/year grid: ``to_finite_float`` maps
    them to ``None`` and ``process`` skips them. With a bare ``float()`` the ``NaN``
    would instead parse straight through into a published row.
    """
    frame = _sheet_1c(
        [
            ["E12000007", "London", 8.0, float("nan")],  # 1998 blank -> skipped
            ["E12000001", "North East", 4.5, 5.0],  # both valid
        ]
    )
    df = _run_process(frame, tmp_path, monkeypatch)

    assert not _has_nonfinite(df["ratio"])
    pairs = set(zip(df["region"], df["year"], strict=True))
    assert ("London", 1998) not in pairs  # blank cell yields no row
    assert {("London", 1997), ("North East", 1997), ("North East", 1998)} == pairs
