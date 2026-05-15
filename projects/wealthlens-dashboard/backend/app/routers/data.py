"""Data endpoints — serves processed CSV datasets as JSON.

Provides dataset listing, paginated data access, and metadata with
source citations for every dataset.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

router = APIRouter()

DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "processed"

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
    """Read a dataset CSV, raising appropriate HTTP errors."""
    csv_path = DATA_DIR / DATASETS[dataset_name]
    if not csv_path.exists():
        raise HTTPException(
            status_code=503,
            detail="Dataset file not found — run the pipeline first",
        )
    return pd.read_csv(csv_path)


def _build_metadata(dataset_name: str) -> dict[str, Any]:
    """Build the full metadata dict for a single dataset."""
    meta = DATASET_META[dataset_name]
    df = _read_csv(dataset_name)
    return {
        "name": dataset_name,
        "description": meta["description"],
        "source": meta["source"],
        "source_url": meta["source_url"],
        "access_date": meta["access_date"],
        "row_count": len(df),
        "columns": list(df.columns),
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
