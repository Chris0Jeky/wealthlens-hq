"""Tests for the data validation script."""

from __future__ import annotations

# Add parent to path so we can import validate
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from validate import CHECKS, validate_all


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
            c for c in CHECKS
            if c.get("ranges") and any(col not in c.get("unique_keys", []) for col in c["ranges"])
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
