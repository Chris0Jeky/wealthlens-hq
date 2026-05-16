import { defineStore } from 'pinia'
import { ref } from 'vue'
import type {
  DatasetListResponse,
  DatasetRow,
  PaginatedDatasetResponse,
} from '@/types/api'
import { fetchWithRetry } from '@/utils/fetchWithRetry'

// Re-export so existing component imports from '@/stores/data' keep working.
export type { DatasetRow } from '@/types/api'

export interface DatasetMetadata {
  name: string
  description: string
  source: string
  source_url: string
  access_date: string
  row_count: number
  columns: string[]
}

export interface PaginatedResponse {
  data: DatasetRow[]
  page: number
  limit: number
  total: number
  total_pages: number
}

const BASE_URL = '/api/data'

async function request<T>(path: string): Promise<T> {
  let res: Response
  try {
    res = await fetchWithRetry(`${BASE_URL}${path}`)
  } catch {
    throw new Error('Could not reach the server')
  }
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`)
  }
  try {
    return (await res.json()) as T
  } catch {
    throw new Error('Response was not valid JSON')
  }
}

export const useDataStore = defineStore('data', () => {
  const datasets = ref<string[]>([])
  const metadata = ref<Map<string, DatasetMetadata>>(new Map())
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchDatasets(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const json = await request<{ datasets: string[] }>('/')
      datasets.value = json.datasets
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch datasets'
    } finally {
      loading.value = false
    }
  }

  async function fetchDataset(
    name: string,
    page = 1,
    limit = 100,
  ): Promise<PaginatedResponse> {
    return request<PaginatedResponse>(`/${name}?page=${page}&limit=${limit}`)
  }

  async function fetchMetadata(name: string): Promise<DatasetMetadata> {
    const cached = metadata.value.get(name)
    if (cached) return cached
    const meta = await request<DatasetMetadata>(`/${name}/metadata`)
    metadata.value.set(name, meta)
    return meta
  }

  async function fetchAllMetadata(): Promise<DatasetMetadata[]> {
    const json = await request<{ datasets: DatasetMetadata[] }>('/metadata')
    for (const m of json.datasets) {
      metadata.value.set(m.name, m)
    }
    return json.datasets
  }

  function clearMetadata(name?: string): void {
    if (name) {
      metadata.value.delete(name)
    } else {
      metadata.value.clear()
    }
  }

  return {
    datasets,
    metadata,
    loading,
    error,
    fetchDatasets,
    fetchDataset,
    fetchMetadata,
    fetchAllMetadata,
    clearMetadata,
  }
})
