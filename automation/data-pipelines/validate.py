"""Validate all processed CSV datasets.

Checks that each pipeline output exists, has expected columns,
contains no empty rows, and values fall within plausible ranges.
Run standalone or from Makefile: make validate
"""

from __future__ import annotations

import logging
import sys
from datetime import date
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

DATA_DIR = (
    Path(__file__).resolve().parents[2]
    / "projects"
    / "wealthlens-dashboard"
    / "data"
    / "processed"
)

CHECKS: list[dict] = [
    {
        "file": "wid_wealth_shares_gb.csv",
        "columns": {"variable", "country", "year", "value"},
        "min_rows": 50,
        "dtypes": {"year": "int", "value": "float"},
        "ranges": {"year": (1800, date.today().year + 5), "value": (0.0, 1.0)},
        "unique_keys": ["year", "variable"],
    },
    {
        "file": "ons_housing_affordability_by_region.csv",
        "columns": {"region", "year", "ratio"},
        "min_rows": 100,
        "dtypes": {"year": "int", "ratio": "float"},
        "ranges": {"year": (1990, date.today().year + 5), "ratio": (0.0, 50.0)},
        "unique_keys": ["year", "region"],
    },
    {
        "file": "ons_wealth_by_decile.csv",
        "columns": {"decile", "total_wealth_bn"},
        "min_rows": 10,
        "dtypes": {"decile": "int", "total_wealth_bn": "float"},
        "ranges": {"decile": (1, 10), "total_wealth_bn": (-500.0, 10000.0)},
        "unique_keys": ["decile"],
    },
    {
        "file": "hmrc_cgt_concentration.csv",
        "columns": {"band_lower"},
        "min_rows": 3,
        "dtypes": {"band_lower": "int"},
        "ranges": {"band_lower": (0, 100_000_000)},
        "unique_keys": ["band_lower"],
    },
    {
        "file": "productivity_pay_gap.csv",
        "columns": {"year", "productivity_index", "pay_index", "gap_pct"},
        "min_rows": 20,
    },
]


def validate_all() -> list[str]:
    """Run all validations and return a list of error messages (empty = pass)."""
    errors: list[str] = []

    for check in CHECKS:
        path = DATA_DIR / check["file"]

        if not path.exists():
            errors.append(f"MISSING: {check['file']}")
            continue

        df = pd.read_csv(path)

        if df.empty:
            errors.append(f"EMPTY: {check['file']}")
            continue

        missing_cols = check["columns"] - set(df.columns)
        if missing_cols:
            errors.append(f"COLUMNS: {check['file']} missing {missing_cols}")
            continue

        if len(df) < check["min_rows"]:
            errors.append(f"ROWS: {check['file']} has {len(df)} rows, expected >= {check['min_rows']}")

        null_count = df.isnull().all(axis=1).sum()
        if null_count > 0:
            errors.append(f"NULLS: {check['file']} has {null_count} fully-null rows")

        if "dtypes" in check:
            for col, expected_kind in check["dtypes"].items():
                if col in df.columns:
                    actual = df[col].dtype
                    if expected_kind == "int" and not pd.api.types.is_integer_dtype(actual):
                        errors.append(f"DTYPE: {check['file']}.{col} is {actual}, expected integer")
                    elif expected_kind == "float" and not pd.api.types.is_float_dtype(actual):
                        errors.append(f"DTYPE: {check['file']}.{col} is {actual}, expected float")

        if "ranges" in check:
            for col, (lo, hi) in check["ranges"].items():
                if col in df.columns:
                    vals = pd.to_numeric(df[col], errors="coerce")
                    coerced_nan = int(vals.isna().sum() - df[col].isna().sum())
                    if coerced_nan > 0:
                        errors.append(
                            f"COERCE: {check['file']}.{col} has {coerced_nan} non-numeric values"
                        )
                    below = int((vals < lo).sum())
                    above = int((vals > hi).sum())
                    if below > 0:
                        errors.append(f"RANGE: {check['file']}.{col} has {below} values below {lo}")
                    if above > 0:
                        errors.append(f"RANGE: {check['file']}.{col} has {above} values above {hi}")

        if "unique_keys" in check:
            keys = check["unique_keys"]
            if all(k in df.columns for k in keys):
                dupes = int(df.duplicated(subset=keys, keep="first").sum())
                if dupes > 0:
                    errors.append(f"DUPES: {check['file']} has {dupes} duplicate rows on {keys}")

    return errors


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    errors = validate_all()
    if errors:
        logger.error("Validation FAILED:")
        for e in errors:
            logger.error("- %s", e)
        sys.exit(1)
    else:
        logger.info("All %d datasets validated OK.", len(CHECKS))
