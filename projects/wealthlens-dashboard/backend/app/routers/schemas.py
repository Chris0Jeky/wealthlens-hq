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
