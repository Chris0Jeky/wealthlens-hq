export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly statusText: string,
    message?: string,
  ) {
    super(message ?? `HTTP ${status} ${statusText}`)
    this.name = 'ApiError'
  }
}

const BASE_URL = '/api'

async function request<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`)
  if (!res.ok) {
    throw new ApiError(res.status, res.statusText)
  }
  return res.json() as Promise<T>
}

export interface DatasetListResponse {
  datasets: string[]
}

export interface PaginatedDatasetResponse {
  data: Record<string, string | number | null>[]
  page: number
  limit: number
  total: number
  total_pages: number
}

export interface DatasetMetadataResponse {
  name: string
  description: string
  source: string
  source_url: string
  access_date: string
  row_count: number
  columns: string[]
}

export interface AllDatasetsMetadataResponse {
  datasets: DatasetMetadataResponse[]
}

export const api = {
  listDatasets(): Promise<DatasetListResponse> {
    return request<DatasetListResponse>('/data/')
  },

  getDataset(name: string, page = 1, limit = 100): Promise<PaginatedDatasetResponse> {
    return request<PaginatedDatasetResponse>(
      `/data/${encodeURIComponent(name)}?page=${page}&limit=${limit}`,
    )
  },

  getMetadata(name: string): Promise<DatasetMetadataResponse> {
    return request<DatasetMetadataResponse>(
      `/data/${encodeURIComponent(name)}/metadata`,
    )
  },

  getAllMetadata(): Promise<AllDatasetsMetadataResponse> {
    return request<AllDatasetsMetadataResponse>('/data/metadata')
  },
}
