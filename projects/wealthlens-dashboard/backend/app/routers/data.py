"""Data endpoints — serves processed CSV datasets as JSON.

Provides dataset listing, paginated data access, metadata with
source citations for every dataset, and a health-check endpoint
that reports CSV availability.
"""

from __future__ import annotations

import json
import logging
import math
import os
from datetime import UTC, datetime
from pathlib import Path as FilePath
from typing import Any, Literal

import pandas as pd
from fastapi import APIRouter, HTTPException, Path, Query, Response
from fastapi.responses import StreamingResponse

from app.routers.schemas import (
    AllDatasetsMetadataResponse,
    DatasetColumnsResponse,
    DatasetListResponse,
    DatasetMetadataResponse,
    DatasetSummaryResponse,
    FreshnessResponse,
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
            "https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/labourproductivity/timeseries/lzvd/prdy"
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
        "source_url": ("https://www.gov.uk/government/statistics/hmrc-tax-and-nics-receipts-for-the-uk"),
        "access_date": "2026-05-16",
    },
    "boe-rates": {
        "description": "Bank Rate and CPI annual inflation",
        "source": "Bank of England Interactive Analytical Database",
        "source_url": ("https://www.bankofengland.co.uk/boeapps/database/"),
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
            "https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/ashe1702"
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
        # Log the full traceback server-side (logger.exception, in an except
        # block) — the underlying exception can include the filesystem path
        # (e.g. OSError "[Errno 13] ... '/abs/path.csv'"), which is exactly the
        # diagnostic detail we want in logs, never in the response. Defence-in-
        # depth: the registered 5xx handler already replaces the detail of any
        # >=500 response with a generic message, so the exception was not
        # client-visible — but don't BUILD a detail string out of a raw
        # exception regardless. dataset_name is a validated DATASETS allowlist
        # slug, so it is safe to echo back in the (generic) detail.
        logger.exception("Failed to read dataset '%s'", dataset_name)
        raise HTTPException(
            status_code=503,
            detail=f"Failed to read dataset '{dataset_name}'",
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

    last_updated = _get_last_updated(dataset_name)
    data_type = _get_data_type(dataset_name)

    return {
        "name": dataset_name,
        "description": meta["description"],
        "source": meta["source"],
        "source_url": meta["source_url"],
        "access_date": meta["access_date"],
        "available": True,
        "row_count": row_count,
        "columns": columns,
        "last_updated": last_updated,
        "data_type": data_type,
    }


def _build_metadata_safe(dataset_name: str) -> dict[str, Any]:
    """Per-dataset metadata that DEGRADES rather than failing the whole catalog.

    The /metadata catalog must keep serving every dataset's source citations even
    if one CSV is temporarily missing (a partial pipeline run) — source-citation
    visibility is mission-critical. On ANY per-dataset failure this returns the
    static citation fields with available=False, row_count=None, columns=[] (the
    last_updated/data_type helpers already degrade to None), mirroring the
    per-dataset degradation the freshness/health endpoints already use. The
    single-dataset endpoint stays strict (503), so it never returns available=False.

    The catch is intentionally broad (any Exception, logged with traceback): the
    whole point is that one dataset can never black out the catalog, so an
    unexpected read-time error degrades just that entry rather than 503-ing all.

    LIMITATION: row_count/columns are cached for a successfully-read dataset (see
    _metadata_cache), so a CSV deleted *after* it was first read still reports
    available=True until the cache is cleared or the process restarts — consistent
    with the cache's documented restart-to-refresh contract. The uncached
    /api/health/data endpoint always reflects current filesystem state.
    """
    try:
        return _build_metadata(dataset_name)
    except Exception:
        logger.exception("metadata: %s unavailable; serving citation-only entry", dataset_name)
        meta = DATASET_META[dataset_name]
        return {
            "name": dataset_name,
            "description": meta["description"],
            "source": meta["source"],
            "source_url": meta["source_url"],
            "access_date": meta["access_date"],
            "available": False,
            "row_count": None,
            "columns": [],
            "last_updated": _get_last_updated(dataset_name),
            "data_type": _get_data_type(dataset_name),
        }


# --- Freshness tracking ---
# Thresholds for classifying dataset freshness.
FRESHNESS_FRESH_HOURS = 168  # 7 days
FRESHNESS_STALE_HOURS = 720  # 30 days


def _get_last_updated(dataset_name: str) -> str | None:
    """Return the ISO 8601 UTC modification time of a dataset's CSV file.

    Returns None if the file does not exist or cannot be stat'd.
    """
    csv_path = DATA_DIR / DATASETS[dataset_name]
    try:
        mtime = csv_path.stat().st_mtime
        return datetime.fromtimestamp(mtime, tz=UTC).isoformat()
    except OSError as exc:
        logger.warning("Cannot stat dataset %s: %s", dataset_name, exc)
        return None


def _get_data_type(dataset_name: str) -> str | None:
    """Return the ``data_type`` from a dataset's ``.meta.json`` sidecar.

    The data pipelines write a sidecar (e.g. ``productivity_pay_gap.meta.json``)
    next to each processed CSV recording provenance — ``"live_ons"`` for live
    data or ``"illustrative_fallback"`` when illustrative data was used. The
    frontend surfaces a data-honesty caveat when the value is
    ``"illustrative_fallback"``.

    Deliberately UNCACHED (unlike row_count/columns): a pipeline rerun that
    switches a dataset between live and fallback data must be reflected without
    a server restart, and this is a single cheap small-file read.

    Returns None when no sidecar exists or it cannot be read/parsed, so a
    dataset without provenance metadata stays backward-compatible (no caveat).
    """
    sidecar_path = (DATA_DIR / DATASETS[dataset_name]).with_suffix(".meta.json")
    try:
        sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    value = sidecar.get("data_type")
    return value if isinstance(value, str) else None


def _freshness_status(age_hours: float) -> Literal["fresh", "stale", "expired"]:
    """Classify a dataset's age into fresh/stale/expired."""
    if age_hours <= FRESHNESS_FRESH_HOURS:
        return "fresh"
    if age_hours <= FRESHNESS_STALE_HOURS:
        return "stale"
    return "expired"


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

    logger.info("Health check: %s (%d/%d datasets available)", status, available_count, total)

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
    "/freshness",
    response_model=FreshnessResponse,
    summary="Dataset freshness status",
)
def dataset_freshness(response: Response) -> dict[str, Any]:
    """Return freshness status for all datasets.

    Reads the modification time of each CSV file to determine how
    recently the data was updated.  Classifies each dataset as
    fresh (within 7 days), stale (within 30 days), or expired (older).
    Returns null for last_updated and age_hours if the file is missing.
    """
    response.headers["Cache-Control"] = _CACHE_METADATA
    now = datetime.now(tz=UTC)
    datasets_freshness: dict[str, dict[str, Any]] = {}

    for name in DATASETS:
        csv_path = DATA_DIR / DATASETS[name]
        try:
            mtime = csv_path.stat().st_mtime
            last_updated_dt = datetime.fromtimestamp(mtime, tz=UTC)
            # Clamp at 0: a file mtime in the future (clock skew across build/deploy
            # hosts, restore-from-backup, an image with future-dated files) would make
            # age negative, which fails the response model's age_hours>=0 and 500s the
            # WHOLE endpoint (blacking out every dataset). A future-dated file is simply
            # treated as just-updated (fresh).
            age_hours = max(0.0, (now - last_updated_dt).total_seconds() / 3600)
            datasets_freshness[name] = {
                "last_updated": last_updated_dt.isoformat(),
                "age_hours": round(age_hours, 1),
                "status": _freshness_status(age_hours),
            }
        except OSError as exc:
            logger.warning("Cannot stat dataset %s for freshness: %s", name, exc)
            datasets_freshness[name] = {
                "last_updated": None,
                "age_hours": None,
                "status": "unknown",
            }

    return {
        "datasets": datasets_freshness,
        "thresholds": {
            "fresh_hours": FRESHNESS_FRESH_HOURS,
            "stale_hours": FRESHNESS_STALE_HOURS,
        },
    }


@router.get(
    "/metadata",
    response_model=AllDatasetsMetadataResponse,
    summary="Metadata for all datasets",
)
def all_datasets_metadata(response: Response) -> dict[str, list[dict[str, Any]]]:
    """Return metadata with source citations for every dataset.

    Each entry includes the dataset description, data source name and URL,
    access date, row count, and column names. If a dataset's CSV is missing or
    unreadable, that entry degrades to ``available: false`` (citations still
    present, row_count null, columns empty) rather than failing the whole
    catalog — see ``_build_metadata_safe``.
    """
    response.headers["Cache-Control"] = _CACHE_METADATA
    # Build defensively: one missing/unreadable CSV must not 503 the whole catalog
    # (and take down every other dataset's source citations with it).
    return {"datasets": [_build_metadata_safe(name) for name in DATASETS]}


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
def dataset_columns(
    dataset_name: str = Path(
        ...,
        pattern=r"^[a-z0-9-]{1,50}$",
        description="Dataset identifier (lowercase, digits, hyphens only)",
    ),
) -> dict[str, Any]:
    """Return per-column metadata: dtype, null count, unique count."""
    if dataset_name not in DATASETS:
        raise HTTPException(status_code=404, detail=f"Unknown dataset: {dataset_name}")

    if dataset_name in _columns_cache:
        return _columns_cache[dataset_name]

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
    result: dict[str, Any] = {"dataset": dataset_name, "row_count": len(df), "columns": columns}
    _columns_cache[dataset_name] = result
    return result


_columns_cache: dict[str, dict[str, Any]] = {}

_summary_cache: dict[str, dict[str, Any]] = {}


@router.get(
    "/{dataset_name}/summary", response_model=DatasetSummaryResponse, summary="Summary statistics for a dataset"
)
def dataset_summary(
    dataset_name: str = Path(
        ...,
        pattern=r"^[a-z0-9-]{1,50}$",
        description="Dataset identifier (lowercase, digits, hyphens only)",
    ),
) -> dict[str, Any]:
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
        summaries.append(
            {
                "column": col,
                "count": int(series.count()),
                "mean": round(float(series.mean()), 4) if len(series) > 0 else None,
                "std": round(float(series.std()), 4) if len(series) > 1 else None,
                "min": round(float(series.min()), 4) if len(series) > 0 else None,
                "max": round(float(series.max()), 4) if len(series) > 0 else None,
                "median": round(float(series.median()), 4) if len(series) > 0 else None,
            }
        )

    result: dict[str, Any] = {
        "dataset": dataset_name,
        "row_count": len(df),
        "numeric_columns": summaries,
    }
    _summary_cache[dataset_name] = result
    return result


@router.get("/{dataset_name}/download", summary="Download dataset as CSV")
def download_dataset(
    dataset_name: str = Path(
        ...,
        pattern=r"^[a-z0-9-]{1,50}$",
        description="Dataset identifier (lowercase, digits, hyphens only)",
    ),
) -> StreamingResponse:
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
