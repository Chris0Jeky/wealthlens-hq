"""Data endpoints — serves processed CSV datasets as JSON.

Provides dataset listing, paginated data access, metadata with
source citations for every dataset, and a health-check endpoint
that reports CSV availability.
"""

from __future__ import annotations

import math
import os
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

router = APIRouter()

DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "processed"

# Cache for metadata derived from CSV reads (row_count, columns).
# Populated lazily by _build_metadata to avoid re-reading CSVs on every
# metadata request.  Safe because the processed data is read-only at runtime.
# Cache is populated once per process lifetime. Restart the server after
# pipeline re-runs to pick up new or changed data files.
_metadata_cache: dict[str, tuple[int, list[str]]] = {}

DATASETS: dict[str, str] = {
    "wealth-shares": "wid_wealth_shares_gb.csv",
    "housing-affordability": "ons_housing_affordability_by_region.csv",
    "wealth-by-decile": "ons_wealth_by_decile.csv",
    "cgt-concentration": "hmrc_cgt_concentration.csv",
}

# Source citations — every dataset must document where the data came from.
DATASET_META: dict[str, dict[str, str]] = {
    "wealth-shares": {
        "description": "Top 1%/10% wealth shares in GB",
        "source": "World Inequality Database",
        "source_url": "https://wid.world/",
        "access_date": "2026-05-14",
    },
    "housing-affordability": {
        "description": "House price to earnings ratio by region",
        "source": "ONS",
        "source_url": (
            "https://www.ons.gov.uk/peoplepopulationandcommunity/housing/"
            "datasets/ratioofhousepricetoworkplacebasedearnings"
            "lowerquartileandmedian"
        ),
        "access_date": "2026-05-14",
    },
    "wealth-by-decile": {
        "description": "Total net wealth by decile",
        "source": "ONS Wealth and Assets Survey",
        "source_url": (
            "https://www.ons.gov.uk/peoplepopulationandcommunity/"
            "personalandhouseholdfinances/incomeandwealth/datasets/"
            "totalwealthwealthingreatbritain"
        ),
        "access_date": "2026-05-14",
    },
    "cgt-concentration": {
        "description": "Capital gains by size of gain",
        "source": "HMRC",
        "source_url": "https://www.gov.uk/government/statistics/capital-gains-tax-statistics",
        "access_date": "2026-05-14",
    },
}


def _read_csv(dataset_name: str) -> pd.DataFrame:
    """Read a dataset CSV, raising appropriate HTTP errors.

    Handles missing files (503) and corrupt/locked/empty/encoding issues
    so that callers always receive a clear error message with the dataset
    name rather than an opaque 500.  The OSError catch covers
    PermissionError, IsADirectoryError, FileNotFoundError (TOCTOU race),
    and Windows file-locking errors.
    """
    csv_path = DATA_DIR / DATASETS[dataset_name]
    if not csv_path.exists():
        raise HTTPException(
            status_code=503,
            detail=f"Dataset file not found: {dataset_name} — run the pipeline first",
        )
    try:
        return pd.read_csv(csv_path)
    except (
        pd.errors.ParserError,
        pd.errors.EmptyDataError,
        OSError,
        UnicodeDecodeError,
    ) as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to read dataset '{dataset_name}': {e}",
        ) from e


def _build_metadata(dataset_name: str) -> dict[str, Any]:
    """Build the full metadata dict for a single dataset.

    Uses a module-level cache so that CSV files are only read once for
    row_count and column information.
    """
    meta = DATASET_META[dataset_name]

    if dataset_name not in _metadata_cache:
        df = _read_csv(dataset_name)
        _metadata_cache[dataset_name] = (len(df), list(df.columns))

    row_count, columns = _metadata_cache[dataset_name]

    return {
        "name": dataset_name,
        "description": meta["description"],
        "source": meta["source"],
        "source_url": meta["source_url"],
        "access_date": meta["access_date"],
        "row_count": row_count,
        "columns": columns,
    }


def health_data() -> dict[str, Any]:
    """Check availability of all configured CSV datasets.

    Returns overall status (healthy/degraded/unavailable) plus per-dataset
    detail including file size when available.  No auth required — this is
    a health / monitoring endpoint.
    """
    datasets_status: dict[str, dict[str, Any]] = {}
    available_count = 0

    for name, filename in DATASETS.items():
        csv_path = DATA_DIR / filename
        entry: dict[str, Any] = {"file": filename}
        try:
            stat = os.stat(csv_path)
            # Verify the file is actually readable, not just present.
            with open(csv_path, "rb"):
                pass
            entry["available"] = True
            entry["size_bytes"] = stat.st_size
            available_count += 1
        except OSError as exc:
            entry["available"] = False
            entry["error"] = str(exc)
        datasets_status[name] = entry

    total = len(DATASETS)
    if available_count == total:
        status = "healthy"
    elif available_count > 0:
        status = "degraded"
    else:
        status = "unavailable"

    return {
        "status": status,
        "datasets": datasets_status,
        "available_count": available_count,
        "total_count": total,
    }


@router.get("/")
def list_datasets() -> dict[str, list[str]]:
    """Return available dataset names."""
    return {"datasets": list(DATASETS.keys())}


@router.get("/metadata")
def all_datasets_metadata() -> dict[str, list[dict[str, Any]]]:
    """Return metadata with source citations for every dataset."""
    return {"datasets": [_build_metadata(name) for name in DATASETS]}


@router.get("/{dataset_name}/metadata")
def dataset_metadata(dataset_name: str) -> dict[str, Any]:
    """Return metadata with source citation for a single dataset."""
    if dataset_name not in DATASETS:
        raise HTTPException(status_code=404, detail=f"Unknown dataset: {dataset_name}")
    return _build_metadata(dataset_name)


@router.get("/{dataset_name}")
def get_dataset(
    dataset_name: str,
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(default=100, ge=1, le=1000, description="Rows per page (max 1000)"),
) -> dict[str, Any]:
    """Return a processed dataset as a paginated list of row objects."""
    if dataset_name not in DATASETS:
        raise HTTPException(status_code=404, detail=f"Unknown dataset: {dataset_name}")

    df = _read_csv(dataset_name)

    # Replace NaN with None so JSON serialization produces explicit nulls
    # rather than silently converting pandas NaN.
    df = df.where(pd.notna(df), None)

    total = len(df)
    total_pages = math.ceil(total / limit) if total > 0 else 1

    start = (page - 1) * limit
    end = start + limit
    page_df = df.iloc[start:end]

    return {
        "data": page_df.to_dict(orient="records"),
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
    }


# --- Module-level guard ---
# Fail fast at import time if someone adds a dataset to one dict but not the other.
assert set(DATASETS.keys()) == set(DATASET_META.keys()), (
    "DATASETS and DATASET_META keys must match — "
    f"DATASETS has {set(DATASETS.keys())}, DATASET_META has {set(DATASET_META.keys())}"
)
