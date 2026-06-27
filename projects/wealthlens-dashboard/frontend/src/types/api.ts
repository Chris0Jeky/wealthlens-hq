/**
 * TypeScript interfaces matching the backend Pydantic response models.
 *
 * Source: backend/app/routers/schemas.py
 * Keep in sync with the FastAPI schemas whenever they change.
 */

// Mirrors backend Pydantic models in schemas.py.
// Pydantic Field constraints (ge=0, ge=1) are not expressible in TS
// and are enforced server-side only.

/** GET /api/data/ — available dataset names. */
export interface DatasetListResponse {
  datasets: string[]
}

/** GET /api/data/{name}/metadata — source-cited metadata for one dataset. */
export interface DatasetMetadataResponse {
  name: string
  description: string
  source: string
  source_url: string
  access_date: string
  row_count: number
  columns: string[]
  last_updated?: string | null
  /** Pipeline provenance: 'live_ons' (live), 'illustrative_fallback' (example
   * composite — caveat shown), 'static_published' (real published figures
   * compiled statically, not invented), or null (no sidecar). */
  data_type?: string | null
}

/** GET /api/data/metadata — metadata for every dataset. */
export interface AllDatasetsMetadataResponse {
  datasets: DatasetMetadataResponse[]
}

/**
 * Backend emits dict[str, Any]; we narrow to the types our charts handle.
 */
export interface DatasetRow {
  [key: string]: string | number | null
}

/** GET /api/data/{name} — paginated row data. */
export interface PaginatedDatasetResponse {
  data: DatasetRow[]
  page: number
  limit: number
  total: number
  total_pages: number
}

/** Freshness info for a single dataset. */
export interface DatasetFreshnessEntry {
  last_updated: string | null
  age_hours: number | null
  status: "fresh" | "stale" | "expired" | "unknown"
}

/** Thresholds used to classify dataset freshness. */
export interface FreshnessThresholds {
  fresh_hours: number
  stale_hours: number
}

/** GET /api/data/freshness — freshness status for all datasets. */
export interface FreshnessResponse {
  datasets: Record<string, DatasetFreshnessEntry>
  thresholds: FreshnessThresholds
}
