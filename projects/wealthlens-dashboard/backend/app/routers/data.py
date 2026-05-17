"""Data endpoints — serves processed CSV datasets as JSON.

Provides dataset listing, paginated data access, metadata with
source citations for every dataset, and a health-check endpoint
that reports CSV availability.
"""

from __future__ import annotations

import logging
import math
import os
from pathlib import Path as FilePath
from typing import Any

import pandas as pd
from fastapi import APIRouter, HTTPException, Path, Query, Response
from fastapi.responses import StreamingResponse

from app.routers.schemas import (
    AllDatasetsMetadataResponse,
    DatasetColumnsResponse,
    DatasetListResponse,
    DatasetMetadataResponse,
    DatasetSummaryResponse,
    PaginatedDatasetResponse,
)

logger = logging.getLogger("wealthlens.data")

router = APIRouter()

DATA_DIR = FilePath(__file__).resolve().parents[3] / "data" / "processed"

# Cache durations — data is updated weekly at most, so cache aggressively.
_CACHE_METADATA = "public, max-age=3600"  # 1 hour for list/metadata endpoints
_CACHE_DATA = "public, max-age=300"  # 5 minutes for paginated data (params vary)

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
    "productivity-pay": "productivity_pay_gap.csv",
    "gdhi-by-region": "ons_gdhi_by_region.csv",
    "tax-composition": "tax_composition.csv",
    "boe-rates": "boe_rates.csv",
    "child-poverty": "child_poverty_by_region.csv",
    "generational-wealth": "generational_wealth_gap.csv",
    "wage-stagnation": "wage_stagnation.csv",
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
    "productivity-pay": {
        "description": "UK productivity vs. real pay, indexed to 100 at 1997",
        "source": "ONS Labour Productivity (LZVD) & ONS AWE (KAB9) deflated by CPIH (L55O)",
        "source_url": (
            "https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/"
            "labourproductivity/timeseries/lzvd/prdy"
        ),
        "access_date": "2026-05-16",
    },
    "gdhi-by-region": {
        "description": "Gross disposable household income per head by region",
        "source": "ONS Regional GDHI",
        "source_url": (
            "https://www.ons.gov.uk/economy/regionalaccounts/"
            "grossdisposablehouseholdincome/datasets/"
            "regionalgrossdisposablehouseholdincomegdhi"
        ),
        "access_date": "2026-05-16",
    },
    "tax-composition": {
        "description": "UK tax revenue composition: work taxes vs wealth taxes",
        "source": "HMRC Tax and NIC Receipts",
        "source_url": (
            "https://www.gov.uk/government/statistics/"
            "hmrc-tax-and-nics-receipts-for-the-uk"
        ),
        "access_date": "2026-05-16",
    },
    "boe-rates": {
        "description": "Bank Rate and CPI annual inflation",
        "source": "Bank of England Interactive Analytical Database",
        "source_url": (
            "https://www.bankofengland.co.uk/boeapps/database/"
        ),
        "access_date": "2026-05-16",
    },
    "child-poverty": {
        "description": "Child poverty rates by UK region (after housing costs)",
        "source": "DWP/HMRC Children in Low Income Families",
        "source_url": (
            "https://www.gov.uk/government/statistics/"
            "children-in-low-income-families-local-area-statistics-2014-to-2023"
        ),
        "access_date": "2026-05-16",
    },
    "generational-wealth": {
        "description": "Median household wealth by generation at equivalent ages",
        "source": "Resolution Foundation / ONS Wealth and Assets Survey",
        "source_url": "https://www.resolutionfoundation.org/publications/",
        "access_date": "2026-05-16",
    },
    "wage-stagnation": {
        "description": "Median real weekly earnings in 2024 prices",
        "source": "ONS Annual Survey of Hours and Earnings (ASHE), Table 1",
        "source_url": (
            "https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/"
            "earningsandworkinghours/datasets/ashe1702"
        ),
        "access_date": "2026-05-16",
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
        logger.warning("Dataset file not found: %s", dataset_name)
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
        logger.error("Failed to read dataset '%s': %s", dataset_name, e)
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
        row_count = len(df)
        _metadata_cache[dataset_name] = (row_count, list(df.columns))
        logger.info("Cached metadata for %s (%d rows)", dataset_name, row_count)

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
            with open(csv_path, "rb") as f:
                size = os.fstat(f.fileno()).st_size
            entry["available"] = True
            entry["size_bytes"] = size
            available_count += 1
        except OSError as exc:
            entry["available"] = False
            entry["error"] = getattr(exc, "strerror", None) or type(exc).__name__
        datasets_status[name] = entry

    total = len(DATASETS)
    if available_count == total:
        status = "healthy"
    elif available_count > 0:
        status = "degraded"
    else:
        status = "unavailable"

    logger.info(
        "Health check: %s (%d/%d datasets available)", status, available_count, total
    )

    return {
        "status": status,
        "datasets": datasets_status,
        "available_count": available_count,
        "total_count": total,
    }


@router.get("/", response_model=DatasetListResponse, summary="List available datasets")
def list_datasets(response: Response) -> dict[str, list[str]]:
    """Return the names of all configured datasets.

    The returned list can be used to build URLs for the paginated data
    and metadata endpoints.
    """
    response.headers["Cache-Control"] = _CACHE_METADATA
    return {"datasets": list(DATASETS.keys())}


@router.get(
    "/metadata",
    response_model=AllDatasetsMetadataResponse,
    summary="Metadata for all datasets",
)
def all_datasets_metadata(response: Response) -> dict[str, list[dict[str, Any]]]:
    """Return metadata with source citations for every dataset.

    Each entry includes the dataset description, data source name and URL,
    access date, row count, and column names.
    """
    response.headers["Cache-Control"] = _CACHE_METADATA
    return {"datasets": [_build_metadata(name) for name in DATASETS]}


@router.get(
    "/{dataset_name}/metadata",
    response_model=DatasetMetadataResponse,
    summary="Metadata for one dataset",
)
def dataset_metadata(
    response: Response,
    dataset_name: str = Path(
        ...,
        pattern=r"^[a-z0-9-]{1,50}$",
        description="Dataset identifier (lowercase, digits, hyphens only)",
    ),
) -> dict[str, Any]:
    """Return metadata with source citation for a single dataset.

    Args:
        dataset_name: Slug identifying the dataset (e.g. ``wealth-shares``).

    Raises:
        HTTPException 404: If *dataset_name* is not recognised.
    """
    if dataset_name not in DATASETS:
        raise HTTPException(status_code=404, detail=f"Unknown dataset: {dataset_name}")
    response.headers["Cache-Control"] = _CACHE_METADATA
    return _build_metadata(dataset_name)


@router.get("/{dataset_name}/columns", response_model=DatasetColumnsResponse)
def dataset_columns(dataset_name: str) -> dict[str, Any]:
    """Return per-column metadata: dtype, null count, unique count."""
    if dataset_name not in DATASETS:
        raise HTTPException(status_code=404, detail=f"Unknown dataset: {dataset_name}")

    df = _read_csv(dataset_name)
    columns = []
    for col in df.columns:
        columns.append(
            {
                "name": col,
                "dtype": str(df[col].dtype),
                "null_count": int(df[col].isna().sum()),
                "unique_count": int(df[col].nunique()),
            }
        )
    return {"dataset": dataset_name, "row_count": len(df), "columns": columns}


_summary_cache: dict[str, dict[str, Any]] = {}


@router.get("/{dataset_name}/summary", response_model=DatasetSummaryResponse,
            summary="Summary statistics for a dataset")
def dataset_summary(dataset_name: str) -> dict[str, Any]:
    """Return descriptive statistics for numeric columns in a dataset."""
    if dataset_name not in DATASETS:
        raise HTTPException(status_code=404, detail=f"Unknown dataset: {dataset_name}")

    if dataset_name in _summary_cache:
        return _summary_cache[dataset_name]

    df = _read_csv(dataset_name)
    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    summaries = []
    for col in numeric_cols:
        series = df[col].dropna()
        summaries.append({
            "column": col,
            "count": int(series.count()),
            "mean": round(float(series.mean()), 4) if len(series) > 0 else None,
            "std": round(float(series.std()), 4) if len(series) > 1 else None,
            "min": round(float(series.min()), 4) if len(series) > 0 else None,
            "max": round(float(series.max()), 4) if len(series) > 0 else None,
            "median": round(float(series.median()), 4) if len(series) > 0 else None,
        })

    result: dict[str, Any] = {
        "dataset": dataset_name,
        "row_count": len(df),
        "numeric_columns": summaries,
    }
    _summary_cache[dataset_name] = result
    return result


@router.get("/{dataset_name}/download", summary="Download dataset as CSV")
def download_dataset(dataset_name: str) -> StreamingResponse:
    """Download a dataset as a CSV file streamed directly from disk."""
    if dataset_name not in DATASETS:
        raise HTTPException(status_code=404, detail=f"Unknown dataset: {dataset_name}")

    csv_path = DATA_DIR / DATASETS[dataset_name]
    if not csv_path.exists():
        raise HTTPException(
            status_code=503,
            detail=f"Dataset file not found: {dataset_name} — run the pipeline first",
        )

    size = csv_path.stat().st_size

    def iterfile():
        with open(csv_path, "rb") as f:
            yield from f

    return StreamingResponse(
        iterfile(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{dataset_name}.csv"',
            "Content-Length": str(size),
        },
    )


@router.get(
    "/{dataset_name}",
    response_model=PaginatedDatasetResponse,
    summary="Get paginated dataset rows",
)
def get_dataset(
    response: Response,
    dataset_name: str = Path(
        ...,
        pattern=r"^[a-z0-9-]{1,50}$",
        description="Dataset identifier (lowercase, digits, hyphens only)",
    ),
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(default=100, ge=1, le=1000, description="Rows per page (max 1000)"),
) -> dict[str, Any]:
    """Return a processed dataset as a paginated list of row objects.

    Args:
        dataset_name: Slug identifying the dataset (e.g. ``wealth-shares``).
        page: 1-indexed page number.  Defaults to ``1``.
        limit: Number of rows per page, between 1 and 1000.  Defaults to ``100``.

    Raises:
        HTTPException 404: If *dataset_name* is not recognised.
    """
    if dataset_name not in DATASETS:
        raise HTTPException(status_code=404, detail=f"Unknown dataset: {dataset_name}")

    response.headers["Cache-Control"] = _CACHE_DATA
    df = _read_csv(dataset_name)

    # Replace NaN with None so JSON serialization produces explicit nulls
    # rather than silently converting pandas NaN.
    df = df.where(pd.notna(df), other=None)  # type: ignore[arg-type]

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
