"""Tests for the data validation script."""

from __future__ import annotations

# Add parent to path so we can import validate
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from run_all import SCRIPTS
from validate import CHECKS, validate_all


def test_checks_cover_every_pipeline() -> None:
    """Every pipeline output must have a validate CHECK.

    CHECKS once drifted from the pipeline set (child_poverty + generational_wealth
    were never validated). Each pipeline emits exactly one processed CSV, so the
    CHECKS file count must equal the pipeline count — this guard keeps it that way.

    Anchored on run_all.SCRIPTS (the canonical pipeline list, which test_run_all
    separately holds equal to the fetch_*.py set) rather than re-globbing fetch_*.py
    here, so a future fetch_* HELPER module can't false-fail this test. It is a
    COUNT-based proxy (CHECKS keys on CSV names; pipelines have no programmatic name
    mapping), so it catches a MISSING check (the drift that occurred) but not a
    count-preserving rename/swap — the per-check test_valid_file_passes plus
    `make validate` on the real tree cover filename correctness. (If a pipeline ever
    emits 0 or >1 CSVs, update this guard.)
    """
    files = [c["file"] for c in CHECKS]
    assert len(files) == len(set(files)), f"duplicate file in CHECKS: {files}"
    assert all(f.endswith(".csv") for f in files), f"non-CSV file in CHECKS: {files}"
    assert len(files) == len(SCRIPTS), (
        f"{len(SCRIPTS)} pipelines in run_all.SCRIPTS but {len(files)} validate CHECKS — "
        "every pipeline output must be validated (CHECKS drifted from the pipeline set)"
    )


class TestValidateAll:
    """Test validate_all against synthetic data."""

    def test_missing_file_reported(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("validate.DATA_DIR", tmp_path)
        errors = validate_all()
        assert any("MISSING" in e for e in errors)

    def test_empty_file_reported(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("validate.DATA_DIR", tmp_path)
        csv_file = tmp_path / CHECKS[0]["file"]
        csv_file.write_text(",".join(CHECKS[0]["columns"]) + "\n")
        errors = validate_all()
        assert any("EMPTY" in e for e in errors)

    def test_missing_columns_reported(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("validate.DATA_DIR", tmp_path)
        csv_file = tmp_path / CHECKS[0]["file"]
        csv_file.write_text("wrong_col\n" + "\n".join(["x"] * 100))
        errors = validate_all()
        assert any("COLUMNS" in e for e in errors)

    def test_too_few_rows_reported(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("validate.DATA_DIR", tmp_path)
        check = CHECKS[0]
        header = ",".join(check["columns"])
        row = ",".join(["x"] * len(check["columns"]))
        csv_file = tmp_path / check["file"]
        csv_file.write_text(header + "\n" + row + "\n")
        errors = validate_all()
        assert any("ROWS" in e for e in errors)

    def test_valid_file_passes(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("validate.DATA_DIR", tmp_path)
        for check in CHECKS:
            csv_file = tmp_path / check["file"]
            csv_file.write_text(self._synth_valid_csv(check))
        errors = validate_all()
        assert errors == []

    def test_duplicate_keys_reported(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        # Positively exercise the unique_keys path: take a valid file and repeat
        # one data row so its unique-key tuple appears twice -> DUPES must fire.
        monkeypatch.setattr("validate.DATA_DIR", tmp_path)
        check = next(c for c in CHECKS if "unique_keys" in c)
        lines = self._synth_valid_csv(check).splitlines()
        lines.append(lines[1])  # duplicate the first data row
        (tmp_path / check["file"]).write_text("\n".join(lines) + "\n")
        errors = validate_all()
        assert any("DUPES" in e for e in errors)

    def _write_all_valid_then_corrupt(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, bad_value: str
    ) -> tuple[str, str, list[str]]:
        """Write valid CSVs for every check, then poison one numeric cell.

        Picks a ranged numeric column that is NOT a unique key, so the corruption
        exercises the non-finite guard rather than the dupes/key path. Returns
        (file, column, errors).
        """
        monkeypatch.setattr("validate.DATA_DIR", tmp_path)
        for check in CHECKS:
            (tmp_path / check["file"]).write_text(self._synth_valid_csv(check))
        # Robust against CHECKS reordering: require a ranged column that is not also a
        # unique key (so the corruption hits the non-finite guard, not the dupes path).
        target = next(
            c for c in CHECKS if c.get("ranges") and any(col not in c.get("unique_keys", []) for col in c["ranges"])
        )
        keys = target.get("unique_keys", [])
        numeric_col = next(c for c in target["ranges"] if c not in keys)
        cols = sorted(target["columns"])
        col_idx = cols.index(numeric_col)
        lines = self._synth_valid_csv(target).splitlines()
        cells = lines[1].split(",")
        cells[col_idx] = bad_value  # "" -> NaN; "inf" -> +inf
        lines[1] = ",".join(cells)
        (tmp_path / target["file"]).write_text("\n".join(lines) + "\n")
        return target["file"], numeric_col, validate_all()

    def test_nonfinite_blank_value_reported(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        # A blank (NaN) numeric cell slips past RANGE (nan<lo / nan>hi both False),
        # COERCE (a genuine NaN cancels in the diff), DTYPE (a NaN column is still
        # float), and the fully-null-ROW NULLS check. The NONFINITE guard must catch it.
        file, col, errors = self._write_all_valid_then_corrupt(tmp_path, monkeypatch, "")
        assert any("NONFINITE" in e and file in e and col in e for e in errors), errors

    def test_nonfinite_inf_value_reported(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        file, col, errors = self._write_all_valid_then_corrupt(tmp_path, monkeypatch, "inf")
        assert any("NONFINITE" in e and file in e and col in e for e in errors), errors

    def test_nan_ok_column_tolerates_blank_but_still_flags_inf(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A nan_ok column's blank is honest-missing (no NONFINITE); an inf still fails.

        boe_rates.cpi_annual is published-late: fetch_boe_rates writes a row with a
        bank rate before that month's CPI exists. validate.py must NOT fail on that
        honest NaN, but an inf is never legitimate.
        """
        monkeypatch.setattr("validate.DATA_DIR", tmp_path)
        boe = next(c for c in CHECKS if c["file"] == "boe_rates.csv")
        assert "cpi_annual" in boe.get("nan_ok", set())  # contract under test
        cols = sorted(boe["columns"])
        idx = cols.index("cpi_annual")

        def _write_with_cpi(value: str) -> list[str]:
            for check in CHECKS:
                (tmp_path / check["file"]).write_text(self._synth_valid_csv(check))
            lines = self._synth_valid_csv(boe).splitlines()
            cells = lines[1].split(",")
            cells[idx] = value
            lines[1] = ",".join(cells)
            (tmp_path / boe["file"]).write_text("\n".join(lines) + "\n")
            return validate_all()

        # Blank cpi -> honest-missing -> NOT flagged.
        blank_errors = _write_with_cpi("")
        assert not any("NONFINITE" in e and "boe_rates" in e and "cpi_annual" in e for e in blank_errors), blank_errors
        # inf cpi -> still flagged (a non-finite that is never legitimate).
        inf_errors = _write_with_cpi("inf")
        assert any("NONFINITE" in e and "boe_rates" in e and "cpi_annual" in e for e in inf_errors), inf_errors

    def test_nan_ok_column_rejects_a_wholesale_blank_column(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A nan_ok column tolerates honest-missing cells but NOT a mostly/all-blank
        column — a renamed/broken live BoE series would NaN out the whole column, and
        that must still fail (else nan_ok would let an empty primary series pass)."""
        monkeypatch.setattr("validate.DATA_DIR", tmp_path)
        boe = next(c for c in CHECKS if c["file"] == "boe_rates.csv")
        cols = sorted(boe["columns"])
        idx = cols.index("bank_rate")
        for check in CHECKS:
            (tmp_path / check["file"]).write_text(self._synth_valid_csv(check))
        # Blank out EVERY bank_rate cell (a wholesale series failure).
        lines = self._synth_valid_csv(boe).splitlines()
        for i in range(1, len(lines)):
            cells = lines[i].split(",")
            cells[idx] = ""
            lines[i] = ",".join(cells)
        (tmp_path / boe["file"]).write_text("\n".join(lines) + "\n")
        errors = validate_all()
        assert any("NONFINITE" in e and "boe_rates" in e and "bank_rate" in e for e in errors), errors

    @staticmethod
    def _synth_valid_csv(check: dict) -> str:
        """Build a CSV that satisfies every rule in ``check``.

        Unlike a naive "N identical rows of 1" fixture, this respects the
        ``dtypes`` (int/float/numeric), ``ranges`` and ``unique_keys`` checks that
        ``validate.py`` enforces. Each row is unique on the unique-key columns:
        a ranged key uses ``lo + i`` while it fits the range (else it cycles to
        stay in range), and an unranged column uses the row index ``i`` (always
        distinct), so at least one key column varies per row and the key tuple is
        unique. Generates exactly ``min_rows`` rows (the validator wants
        ``>= min_rows``); narrow ranges such as year in (2000, 2031) make a fixed
        200-row count impossible.
        """
        cols = sorted(check["columns"])
        dtypes = check.get("dtypes", {})
        ranges = check.get("ranges", {})
        lines = [",".join(cols)]
        for i in range(check["min_rows"]):
            cells = []
            for col in cols:
                if col in ranges:
                    lo, hi = ranges[col]
                    width = hi - lo
                    value = lo + i if i <= width else lo + (i % (int(width) + 1))
                else:
                    value = i  # distinct per row: covers unranged unique keys/strings
                kind = dtypes.get(col)
                if kind == "float":
                    cells.append(str(float(value)))
                elif kind == "int":
                    cells.append(str(int(value)))
                else:  # "numeric" or no dtype constraint
                    cells.append(str(value))
            lines.append(",".join(cells))
        return "\n".join(lines) + "\n"
