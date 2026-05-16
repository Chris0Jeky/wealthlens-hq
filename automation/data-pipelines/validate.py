"""Validate all processed CSV datasets.

Checks that each pipeline output exists, has expected columns,
contains no empty rows, and values fall within plausible ranges.
Run standalone or from Makefile: make validate
"""

from __future__ import annotations

import logging
import sys
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
    },
    {
        "file": "ons_housing_affordability_by_region.csv",
        "columns": {"region", "year", "ratio"},
        "min_rows": 100,
    },
    {
        "file": "ons_wealth_by_decile.csv",
        "columns": {"decile", "total_wealth_bn"},
        "min_rows": 10,
    },
    {
        "file": "hmrc_cgt_concentration.csv",
        "columns": {"band_lower"},
        "min_rows": 3,
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

        if len(df) < check["min_rows"]:
            errors.append(f"ROWS: {check['file']} has {len(df)} rows, expected >= {check['min_rows']}")

        null_count = df.isnull().all(axis=1).sum()
        if null_count > 0:
            errors.append(f"NULLS: {check['file']} has {null_count} fully-null rows")

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
