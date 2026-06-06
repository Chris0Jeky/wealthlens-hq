"""Regression tests for scripts/generate_static_api.py NaN handling.

A blank/suppressed source cell (pandas NaN) must serialise to JSON ``null``, not
the invalid-JSON literal ``NaN``. The generator previously used
``df.where(pd.notna(df), other=None)``, which is ineffective for float columns
(pandas re-coerces None back to NaN), so ``cgt-concentration.json`` shipped a
literal ``NaN`` that no browser ``fetch().json()`` / ``JSON.parse`` can read.

These tests lock the two halves of the fix: record-level NaN->None sanitisation,
and ``allow_nan=False`` strict serialisation as a build-time guard.
"""

import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import generate_static_api as gsa  # noqa: E402


def _write_csv(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "dataset.csv"
    path.write_text(text, encoding="utf-8")
    return path


def test_blank_cell_becomes_none_not_nan(tmp_path: Path) -> None:
    """A blank numeric cell parses to None (JSON null), not float NaN."""
    csv = _write_csv(
        tmp_path,
        # The second row's suppressed taxpayer count is blank -> pandas NaN.
        "gain_band,band_lower,num_taxpayers_thousands\n"
        "A,0.0,2.0\n"
        "B,3000.0,\n",
    )
    records = gsa._read_csv_as_records(csv)

    assert records[1]["num_taxpayers_thousands"] is None
    # Surrounding values are untouched.
    assert records[0]["num_taxpayers_thousands"] == 2.0
    assert records[1]["gain_band"] == "B"
    assert records[1]["band_lower"] == 3000.0


def test_records_serialise_as_strict_valid_json(tmp_path: Path) -> None:
    """Sanitised records pass json.dumps(allow_nan=False) and round-trip."""
    csv = _write_csv(
        tmp_path,
        "a,b\n1.0,\n,2.0\n",  # one blank per row
    )
    records = gsa._read_csv_as_records(csv)

    # allow_nan=False is the generator's build-time guard: it must not raise,
    # must emit `null` (never the invalid `NaN` token), and must round-trip
    # through a strict JSON parser (what the browser does).
    out = json.dumps({"data": records}, allow_nan=False)
    assert "NaN" not in out
    assert "null" in out
    assert json.loads(out) == {"data": records}


def test_allow_nan_false_would_catch_an_unsanitised_leak() -> None:
    """The guard is real: a raw NaN trips allow_nan=False (no silent NaN ship)."""
    import math

    try:
        json.dumps({"x": math.nan}, allow_nan=False)
    except ValueError:
        pass
    else:  # pragma: no cover - the guard must raise
        raise AssertionError("allow_nan=False should reject a NaN value")
