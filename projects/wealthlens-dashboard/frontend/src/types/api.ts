/**
 * TypeScript interfaces matching the backend Pydantic response models.
 *
 * Source: backend/app/routers/schemas.py
 * Keep in sync with the FastAPI schemas whenever they change.
 */

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

/** A single row returned by the paginated dataset endpoint. */
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
