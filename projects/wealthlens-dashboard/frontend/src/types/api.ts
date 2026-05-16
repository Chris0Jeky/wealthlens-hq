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
