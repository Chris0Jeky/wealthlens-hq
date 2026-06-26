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

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parents[2] / "projects" / "wealthlens-dashboard" / "data" / "processed"

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
        "dtypes": {"total_wealth_bn": "float"},
        "ranges": {"total_wealth_bn": (-500.0, 10000.0)},
        "unique_keys": ["decile"],
    },
    {
        # Only band_lower is guarded ON PURPOSE: num_taxpayers_thousands /
        # share_of_taxpayers_pct are intentionally NaN-tolerant — HMRC suppresses some
        # bands' taxpayer counts for disclosure control while still publishing the gains,
        # so a NaN there is the honest "suppressed" value, NOT a leak. Do NOT add a
        # finite/range guard on those columns (it would falsely fail on legitimate
        # suppression). The HMRC chart-builder renders those NaNs as "n/a"/"suppressed"
        # (fetch_hmrc_stats.build_chart, guarded by pd.notna).
        "file": "hmrc_cgt_concentration.csv",
        "columns": {"band_lower"},
        "min_rows": 3,
        "dtypes": {"band_lower": "numeric"},
        "ranges": {"band_lower": (0, 100_000_000)},
        "unique_keys": ["band_lower"],
    },
    {
        "file": "productivity_pay_gap.csv",
        "columns": {"year", "productivity_index", "pay_index", "gap_pct"},
        "min_rows": 20,
        "dtypes": {"year": "int", "productivity_index": "float", "pay_index": "float", "gap_pct": "float"},
        # gap_pct can be slightly negative (pay outran productivity in some years).
        "ranges": {
            "year": (1900, date.today().year + 5),
            "productivity_index": (0.0, 1_000.0),
            "pay_index": (0.0, 1_000.0),
            "gap_pct": (-50.0, 100.0),
        },
        "unique_keys": ["year"],
    },
    {
        "file": "ons_gdhi_by_region.csv",
        "columns": {"region", "gdhi_per_head", "year"},
        "min_rows": 10,
        "dtypes": {"gdhi_per_head": "numeric", "year": "int"},
        "ranges": {"gdhi_per_head": (5_000, 200_000), "year": (1990, date.today().year + 5)},
        "unique_keys": ["region"],
    },
    {
        "file": "tax_composition.csv",
        # Require the derived published totals + the data_source provenance column too,
        # so a regenerated CSV that drops them is caught (and the totals get NONFINITE-
        # guarded). Downstream API/charts expose this CSV directly.
        "columns": {
            "year",
            "income_tax_bn",
            "nics_bn",
            "cgt_bn",
            "iht_bn",
            "sdlt_bn",
            "work_taxes_bn",
            "wealth_taxes_bn",
            "total_selected_bn",
            "work_pct",
            "wealth_pct",
            "data_source",
        },
        "min_rows": 3,
        "dtypes": {
            "income_tax_bn": "float",
            "nics_bn": "float",
            "cgt_bn": "float",
            "iht_bn": "float",
            "sdlt_bn": "float",
            "work_taxes_bn": "float",
            "wealth_taxes_bn": "float",
            "total_selected_bn": "float",
            "work_pct": "float",
            "wealth_pct": "float",
        },
        "ranges": {
            "income_tax_bn": (0.0, 2_000.0),
            "nics_bn": (0.0, 2_000.0),
            "cgt_bn": (0.0, 200.0),
            "iht_bn": (0.0, 200.0),
            "sdlt_bn": (0.0, 200.0),
            "work_taxes_bn": (0.0, 4_000.0),
            "wealth_taxes_bn": (0.0, 1_000.0),
            "total_selected_bn": (0.0, 5_000.0),
            "work_pct": (0.0, 100.0),
            "wealth_pct": (0.0, 100.0),
        },
        "unique_keys": ["year"],
    },
    {
        "file": "boe_rates.csv",
        # Require cpi_annual to be present: it is emitted + consumed by the chart, and
        # the dtype/range guards below only fire for columns that EXIST, so without this
        # a dropped column would validate clean and the chart would NaN out every row.
        "columns": {"date", "bank_rate", "cpi_annual"},
        "min_rows": 10,
        "dtypes": {"bank_rate": "float", "cpi_annual": "float"},
        "ranges": {"bank_rate": (0.0, 50.0), "cpi_annual": (-10.0, 50.0)},
        "unique_keys": ["date"],
        # Per-cell NaN in these is the HONEST "not published yet" value, NOT a leak:
        # fetch_boe_rates.process keeps a row when EITHER series is present and writes
        # None for the other (BoE publishes a month's bank rate before that month's
        # CPI; an early bank_rate can be unfilled). test_pipeline_finite_cells asserts
        # such NaN rows are published. nan_ok suppresses the per-cell NONFINITE flag for
        # these columns ONLY (the column must still exist; an inf is still flagged) — but
        # only up to max_nan_frac: a mostly-blank column is a broken series (e.g. a
        # renamed live source code), not honest-missing, and must still fail. Honest
        # missing is a few unpublished trailing months / a leading gap (well under half),
        # so 50% is a safe ceiling.
        "nan_ok": {"bank_rate", "cpi_annual"},
        "max_nan_frac": 0.5,
    },
    {
        "file": "wage_stagnation.csv",
        "columns": {"year", "real_weekly"},
        "min_rows": 20,
        "dtypes": {"year": "int", "real_weekly": "int"},
        "ranges": {
            "year": (2000, date.today().year + 5),
            "real_weekly": (0, 2_000),
        },
        "unique_keys": ["year"],
    },
    {
        # Previously UNVALIDATED (CHECKS covered 9 of 11 pipeline outputs); the
        # test_checks_cover_every_pipeline drift guard now keeps the list complete.
        # above_national_avg is a bool flag (no numeric guard); the three numeric
        # columns are range/finite-guarded.
        "file": "child_poverty_by_region.csv",
        "columns": {"region", "child_poverty_pct", "children_in_poverty", "national_avg_pct", "above_national_avg"},
        "min_rows": 10,
        "dtypes": {"child_poverty_pct": "float", "children_in_poverty": "numeric", "national_avg_pct": "float"},
        "ranges": {
            "child_poverty_pct": (0.0, 100.0),
            "national_avg_pct": (0.0, 100.0),
            "children_in_poverty": (0, 5_000_000),
        },
        "unique_keys": ["region"],
    },
    {
        # Previously UNVALIDATED. generation/birth_years are labels and `projected`
        # is a bool flag (no numeric guard); the three numeric columns are guarded.
        # One row is one (generation, age-milestone) observation, so that pair is the key.
        "file": "generational_wealth_gap.csv",
        "columns": {"generation", "birth_years", "age_milestone", "median_wealth_gbp", "year_measured", "projected"},
        "min_rows": 5,
        "dtypes": {"age_milestone": "int", "median_wealth_gbp": "numeric", "year_measured": "int"},
        "ranges": {
            "age_milestone": (0, 120),
            "median_wealth_gbp": (0, 5_000_000),
            "year_measured": (1900, date.today().year + 5),
        },
        "unique_keys": ["generation", "age_milestone"],
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
                    if expected_kind == "numeric" and not pd.api.types.is_numeric_dtype(actual):
                        errors.append(f"DTYPE: {check['file']}.{col} is {actual}, expected numeric")
                    elif expected_kind == "int" and not pd.api.types.is_integer_dtype(actual):
                        errors.append(f"DTYPE: {check['file']}.{col} is {actual}, expected integer")
                    elif expected_kind == "float" and not pd.api.types.is_float_dtype(actual):
                        errors.append(f"DTYPE: {check['file']}.{col} is {actual}, expected float")

        if "ranges" in check:
            for col, (lo, hi) in check["ranges"].items():
                if col in df.columns:
                    vals = pd.to_numeric(df[col], errors="coerce")
                    coerced_nan = int(vals.isna().sum() - df[col].isna().sum())
                    if coerced_nan > 0:
                        errors.append(f"COERCE: {check['file']}.{col} has {coerced_nan} non-numeric values")
                    below = int((vals < lo).sum())
                    above = int((vals > hi).sum())
                    if below > 0:
                        errors.append(f"RANGE: {check['file']}.{col} has {below} values below {lo}")
                    if above > 0:
                        errors.append(f"RANGE: {check['file']}.{col} has {above} values above {hi}")

        # Non-finite guard: a blank (NaN) or inf value in a numeric column slips past
        # every other check — `nan < lo` and `nan > hi` are both False (RANGE), a
        # genuine NaN cancels in the COERCE diff, a NaN column is still float dtype
        # (DTYPE), and NULLS only flags fully-null ROWS. So a single blank source cell
        # could publish a NaN unnoticed. Flag any non-finite value in a declared-numeric
        # column (those with a range or an int/float/numeric dtype). CONTRACT: a numeric
        # column is only covered if its CHECK declares a range or numeric dtype — every
        # numeric output column above does. A *literal* "NaN"/"inf" string in an object
        # column is handled by the COERCE check, not here (blank counts raw NaN only).
        numeric_cols = set(check.get("ranges", {})) | {
            col for col, kind in check.get("dtypes", {}).items() if kind in ("int", "float", "numeric")
        }
        # nan_ok columns carry honest-missing NaN by design (see the boe_rates check),
        # so an INDIVIDUAL blank there is expected, not a leak. But a column that is
        # MOSTLY blank is a broken series (e.g. a renamed live source code), not
        # honest-missing — that must still fail, else nan_ok would let an all-NaN
        # bank_rate/cpi_annual validate clean (COLUMNS only checks existence; an
        # all-NaN column is still float dtype and passes RANGE/COERCE/NULLS). So:
        # tolerate per-cell blanks up to max_nan_frac of the column, flag beyond it.
        # An inf is never legitimate, so it is still flagged for every numeric column.
        nan_ok = check.get("nan_ok", set())
        max_nan_frac = check.get("max_nan_frac", 0.5)
        n_rows = len(df)
        for col in sorted(numeric_cols):
            if col in df.columns:
                coerced = pd.to_numeric(df[col], errors="coerce")
                raw_blank = int(df[col].isna().sum())
                infinite = int(np.isinf(coerced).sum())
                if col in nan_ok:
                    if n_rows and raw_blank / n_rows > max_nan_frac:
                        errors.append(
                            f"NONFINITE: {check['file']}.{col} is {raw_blank}/{n_rows} blank "
                            f"(> {max_nan_frac:.0%}); a tolerated column may be honest-missing, not wholesale-blank"
                        )
                    blank = 0  # individual honest-missing blanks are fine below the ceiling
                else:
                    blank = raw_blank
                if blank + infinite > 0:
                    errors.append(f"NONFINITE: {check['file']}.{col} has {blank + infinite} blank/infinite value(s)")

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
