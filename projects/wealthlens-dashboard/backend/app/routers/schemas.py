"""Pydantic response models for the data API endpoints.

Provides automatic OpenAPI documentation and response validation for
every GET endpoint in the data router.  Uses Pydantic v2 syntax.
"""

from __future__ import annotations

from typing import Any, Literal

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
    available: bool = Field(
        default=True,
        description=(
            "False when the dataset's CSV is missing/unreadable (e.g. a partial "
            "pipeline run). Source citations are still served; row_count/columns "
            "are null/empty. Always True from the single-dataset endpoint, which "
            "503s instead."
        ),
    )
    row_count: int | None = Field(
        default=None,
        ge=0,
        description="Row count, or null when the dataset file is unavailable",
    )
    columns: list[str] = Field(default_factory=list)
    last_updated: str | None = Field(
        default=None,
        description="ISO 8601 datetime of last CSV file modification, or null if missing",
    )
    data_type: str | None = Field(
        default=None,
        description=(
            "Data provenance from the pipeline's .meta.json sidecar: "
            "'live_ons' for live data, 'illustrative_fallback' when "
            "illustrative data was used, or null if no sidecar exists"
        ),
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

    last_updated: str | None = Field(description="ISO 8601 datetime of last file modification, or null if missing")
    age_hours: float | None = Field(ge=0, description="Hours since last update, or null if file missing")
    status: Literal["fresh", "stale", "expired", "unknown"] = Field(
        description="fresh (<=7d), stale (<=30d), expired (>30d), unknown (missing)"
    )


class FreshnessThresholds(BaseModel):
    """Thresholds used to classify dataset freshness."""

    fresh_hours: int = Field(description="Max hours to be considered fresh")
    stale_hours: int = Field(description="Max hours to be considered stale (beyond = expired)")


class FreshnessResponse(BaseModel):
    """Response for GET /api/data/freshness — freshness status for all datasets."""

    datasets: dict[str, DatasetFreshnessEntry]
    thresholds: FreshnessThresholds


class SimulatorScenarioInfo(BaseModel):
    """One available WealthLens-Sim scenario."""

    id: str
    name: str
    description: str


class SimulatorScenarioListResponse(BaseModel):
    """Response for GET /api/simulator/ — available scenarios."""

    scenarios: list[SimulatorScenarioInfo]
