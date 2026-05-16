import { defineStore } from 'pinia'
import { ref } from 'vue'
import type {
  DatasetListResponse,
  DatasetRow,
  PaginatedDatasetResponse,
} from '@/types/api'

const API_BASE = ((): string => {
  const raw = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.trim()
  if (!raw) return '/api'
  return raw.replace(/\/+$/, '')
})()

// Re-export so existing component imports from '@/stores/data' keep working.
export type { DatasetRow } from '@/types/api'

export const useDataStore = defineStore('data', () => {
  const datasets = ref<string[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchDatasets(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const res = await fetch(`${API_BASE}/data/`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const json: DatasetListResponse = await res.json()
      datasets.value = json.datasets
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch datasets'
    } finally {
      loading.value = false
    }
  }

  async function fetchDataset(name: string): Promise<DatasetRow[]> {
    const res = await fetch(`${API_BASE}/data/${name}`)
    if (!res.ok) {
      throw new Error(
        `Failed to fetch ${name}: ${res.status} ${res.statusText}`,
      )
    }
    const json: PaginatedDatasetResponse = await res.json()
    return json.data
  }

  return { datasets, loading, error, fetchDatasets, fetchDataset }
})
