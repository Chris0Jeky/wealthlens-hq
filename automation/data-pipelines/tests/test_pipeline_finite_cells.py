"""Call-site regression tests for the shared ``_cells.to_finite_float`` NaN guard.

#365 follow-up. ``fetch_hmrc_stats`` already has a focused test
(``test_hmrc_finite_cells``); this file locks in the three fetchers the #365 review
named — ``fetch_boe_rates``, ``fetch_productivity_pay`` and ``fetch_wid_data`` — so a
future refactor that reintroduces a bare ``float()`` (which would let a blank / NaN /
inf source cell leak into a published CSV) is caught here rather than in production
data. The remaining ``to_finite_float`` call sites are now covered too —
``fetch_tax_composition``, ``fetch_ons_gdhi``, ``fetch_ons_housing`` and
``fetch_ons_wealth`` each have a sibling ``test_<fetcher>_finite_cells.py`` — so every
guarded seam across the pipelines is mutation-tested.

Discriminating signal: a working ``to_finite_float`` never emits ``inf`` (it converts
a bad cell to ``None`` — the row is dropped, or the value recorded as a missing
``NaN``); only a bypassed bare ``float()`` lets an ``inf`` through. So for a KEPT row
the test asserts the published column carries no ``inf``; for a DROP call site it
asserts the bad row is gone and the column carries no non-finite value at all.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import fetch_boe_rates
import fetch_productivity_pay
import fetch_wid_data


def _has_inf(series: pd.Series) -> bool:
    """True if any entry is +/-infinity.

    Infinity is the unmistakable signature of a bypassed ``to_finite_float``: the
    guard converts a non-finite cell to ``None`` (the row is dropped, or the value
    recorded as a missing ``NaN``), so a published ``inf`` can only come from a bare
    ``float()``. Vectorised; ``isin`` matches both ``np.inf`` and ``float('inf')``.
    """
    return bool(series.isin([float("inf"), float("-inf")]).any())


def _has_nonfinite(series: pd.Series) -> bool:
    """True if any entry is NaN/None or +/-inf.

    Use only where surviving rows carry no legitimate missing value (a DROP call
    site, or a forward-filled column) — there a NaN can only be a leak. Vectorised
    and safe on object dtype (``isna`` covers both ``None`` and ``NaN``).
    """
    return bool(series.isna().any() or _has_inf(series))


# --- fetch_wid_data.process -------------------------------------------------


def test_wid_drops_nonfinite_value_and_noninteger_year(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A blank/inf value or a non-integer year is dropped, never published as NaN."""
    monkeypatch.setattr(fetch_wid_data, "PROCESSED_DIR", tmp_path)
    raw: dict[str, Any] = {
        "shweal_p99p100_992_j": [
            {
                "GB": {
                    "values": [
                        {"y": 2000, "v": 0.20},  # valid
                        {"y": 2001, "v": ""},  # blank value -> drop
                        {"y": 2002, "v": "inf"},  # non-finite -> drop
                        {"y": "2003.5", "v": 0.22},  # non-integer year -> drop
                        {"y": 2004, "v": 0.23},  # valid
                    ]
                }
            },
        ],
    }
    df = fetch_wid_data.process(raw)
    assert df["year"].tolist() == [2000, 2004]
    assert not _has_nonfinite(df["value"])


# --- fetch_productivity_pay._fetch_ons_timeseries ---------------------------


class _FakeResp:
    """Minimal stand-in for a ``requests`` response exposing the used surface."""

    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return self._payload


def test_productivity_timeseries_drops_nonfinite_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A blank/NaN observation is dropped from the parsed ONS time-series."""
    payload = {
        "years": [
            {"year": "2000", "value": "100.0"},  # valid
            {"year": "2001", "value": ""},  # blank -> drop
            {"year": "2002", "value": "nan"},  # non-finite -> drop
            {"year": "2003", "value": "110.0"},  # valid
        ]
    }
    monkeypatch.setattr(
        fetch_productivity_pay.requests, "get", lambda *_a, **_k: _FakeResp(payload)
    )
    df = fetch_productivity_pay._fetch_ons_timeseries("http://example.org/x", "prod")
    assert df is not None
    assert df["year"].tolist() == [2000, 2003]
    assert not _has_nonfinite(df["value"])


# --- fetch_boe_rates.process ------------------------------------------------


def test_boe_rejects_nonfinite_rate_cells(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A non-finite Bank Rate / CPI cell never reaches the published CSV.

    ``inf`` would survive a bare ``float()``; ``to_finite_float`` turns it into
    ``None``. bank_rate is forward-filled (so a rejected cell leaves no NaN), but cpi
    is not — a rejected cpi cell is recorded as a missing NaN, so the test asserts
    cpi carries no ``inf`` (the leak signal), not no-NaN. A row whose values are all
    non-finite is dropped entirely. Both call sites (bank_rate L214, cpi L222) are
    exercised with a value that bare ``float()`` would accept.
    """
    monkeypatch.setattr(fetch_boe_rates, "PROCESSED_DIR", tmp_path)
    raw = tmp_path / "boe_raw.csv"
    raw.write_text(
        "DATE,IUDBEDR,D7BT\n"
        "01 Jan 2000,5.5,2.1\n"  # valid
        "02 Jan 2000,inf,3.0\n"  # bank_rate non-finite -> None (row kept via CPI), ffilled
        "03 Jan 2000,nan,nan\n"  # all non-finite -> row dropped
        "04 Jan 2000,4.0,1.5\n"  # valid
        "05 Jan 2000,4.5,inf\n",  # CPI non-finite, bank_rate valid -> row kept, cpi rejected
        encoding="utf-8",
    )
    df = fetch_boe_rates.process(raw)
    assert not _has_nonfinite(df["bank_rate"])  # ffilled -> no NaN, no inf
    assert not _has_inf(df["cpi_annual"])  # a rejected cpi is a missing NaN, never inf
    # The all-non-finite row was dropped; valid + recoverable rows survive.
    assert "2000-01-03" not in df["date"].tolist()
    assert {"2000-01-01", "2000-01-04", "2000-01-05"} <= set(df["date"].tolist())
    # The row whose only bad cell was CPI survives with a missing (NaN) cpi, not inf.
    cpi_05 = df.loc[df["date"] == "2000-01-05", "cpi_annual"].iloc[0]
    assert pd.isna(cpi_05)
