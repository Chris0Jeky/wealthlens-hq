import { defineStore } from 'pinia'
import { ref } from 'vue'
import type {
  DatasetRow,
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

const STATIC_MODE = import.meta.env.VITE_STATIC_DATA === 'true'
const API_BASE = '/api/data'
const STATIC_BASE = `${import.meta.env.BASE_URL}data`

async function request<T>(path: string): Promise<T> {
  const url = STATIC_MODE ? toStaticUrl(path) : `${API_BASE}${path}`
  let res: Response
  try {
    res = await fetchWithRetry(url, undefined, STATIC_MODE ? 0 : 3)
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

function toStaticUrl(apiPath: string): string {
  if (apiPath === '/') return `${STATIC_BASE}/datasets.json`
  if (apiPath === '/metadata') return `${STATIC_BASE}/all-metadata.json`

  const metaMatch = apiPath.match(/^\/([a-z0-9-]+)\/metadata$/)
  if (metaMatch) return `${STATIC_BASE}/${metaMatch[1]}-metadata.json`

  const dataMatch = apiPath.match(/^\/([a-z0-9-]+)/)
  if (dataMatch) return `${STATIC_BASE}/${dataMatch[1]}.json`

  return `${STATIC_BASE}${apiPath}`
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
    if (STATIC_MODE) {
      return request<PaginatedResponse>(`/${name}`)
    }
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
