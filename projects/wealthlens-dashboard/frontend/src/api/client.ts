const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"

export interface DatasetMeta {
  name: string
  description: string
  source: string
  source_url: string
  access_date: string
  row_count: number
  columns: string[]
}

export interface PaginatedResponse<T = Record<string, unknown>> {
  data: T[]
  page: number
  limit: number
  total: number
  total_pages: number
}

export interface ColumnInfo {
  name: string
  dtype: string
  null_count: number
  unique_count: number
}

export interface DatasetColumnsResponse {
  dataset: string
  row_count: number
  columns: ColumnInfo[]
}

export interface HealthResponse {
  status: string
}

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`)
  if (!response.ok) {
    throw new Error(`API ${response.status}: ${response.statusText}`)
  }
  return response.json() as Promise<T>
}

export const api = {
  listDatasets(): Promise<{ datasets: string[] }> {
    return fetchJson("/api/data/")
  },

  getMetadata(): Promise<{ datasets: DatasetMeta[] }> {
    return fetchJson("/api/data/metadata")
  },

  getDatasetMetadata(name: string): Promise<DatasetMeta> {
    return fetchJson(`/api/data/${encodeURIComponent(name)}/metadata`)
  },

  getDatasetColumns(name: string): Promise<DatasetColumnsResponse> {
    return fetchJson(`/api/data/${encodeURIComponent(name)}/columns`)
  },

  getDataset(name: string, page = 1, limit = 100): Promise<PaginatedResponse> {
    return fetchJson(`/api/data/${encodeURIComponent(name)}?page=${page}&limit=${limit}`)
  },

  health(): Promise<HealthResponse> {
    return fetchJson("/health")
  },
}
