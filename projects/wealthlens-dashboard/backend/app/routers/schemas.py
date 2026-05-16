"""Pydantic response models for the data API endpoints.

Provides automatic OpenAPI documentation and response validation for
every GET endpoint in the data router.  Uses Pydantic v2 syntax.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DatasetListResponse(BaseModel):
    """Response for GET /api/data/ — available dataset names."""

    datasets: list[str]


class DatasetMetadataResponse(BaseModel):
    """Response for GET /api/data/{name}/metadata — source-cited metadata."""

    name: str
    description: str
    source: str
    source_url: str
    access_date: str
    row_count: int = Field(ge=0)
    columns: list[str]
    last_updated: str | None = Field(
        default=None,
        description="ISO 8601 datetime of last CSV file modification, or null if missing",
    )


class AllDatasetsMetadataResponse(BaseModel):
    """Response for GET /api/data/metadata — metadata for every dataset."""

    datasets: list[DatasetMetadataResponse]


class ColumnSummary(BaseModel):
    """Descriptive statistics for a single numeric column."""

    column: str
    count: int = Field(ge=0, description="Number of non-null values in this column")
    mean: float | None = None
    std: float | None = None
    min: float | None = None
    max: float | None = None
    median: float | None = None


class DatasetSummaryResponse(BaseModel):
    """Response for GET /api/data/{name}/summary — descriptive stats."""

    dataset: str
    row_count: int = Field(ge=0, description="Total rows including those with null values")
    numeric_columns: list[ColumnSummary]


class PaginatedDatasetResponse(BaseModel):
    """Response for GET /api/data/{name} — paginated row data."""

    data: list[dict[str, Any]]
    page: int = Field(ge=1)
    limit: int = Field(ge=1)
    total: int = Field(ge=0)
    total_pages: int = Field(ge=1)


class ColumnInfo(BaseModel):
    """Metadata for a single dataset column."""

    name: str
    dtype: str = Field(description="Pandas dtype string (e.g. int64, float64, object)")
    null_count: int = Field(ge=0, description="Number of null/NaN values")
    unique_count: int = Field(ge=0, description="Number of distinct values")


class DatasetColumnsResponse(BaseModel):
    """Response for GET /api/data/{name}/columns — per-column metadata."""

    dataset: str
    row_count: int = Field(ge=0)
    columns: list[ColumnInfo]


class DatasetFreshnessEntry(BaseModel):
    """Freshness info for a single dataset."""

    last_updated: str | None = Field(
        description="ISO 8601 datetime of last file modification, or null if missing"
    )
    age_hours: float | None = Field(
        ge=0, description="Hours since last update, or null if file missing"
    )
    status: str = Field(
        description="One of: fresh (<=7d), stale (<=30d), expired (>30d), unknown (missing)"
    )


class FreshnessThresholds(BaseModel):
    """Thresholds used to classify dataset freshness."""

    fresh_hours: int = Field(description="Max hours to be considered fresh")
    stale_hours: int = Field(description="Max hours to be considered stale (beyond = expired)")


class FreshnessResponse(BaseModel):
    """Response for GET /api/data/freshness — freshness status for all datasets."""

    datasets: dict[str, DatasetFreshnessEntry]
    thresholds: FreshnessThresholds
