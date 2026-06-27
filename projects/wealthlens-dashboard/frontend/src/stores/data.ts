import { defineStore } from 'pinia'
import { ref } from 'vue'
import type {
  DatasetRow,
  FreshnessResponse,
  DatasetFreshnessEntry,
} from '@/types/api'
import { fetchWithRetry } from '@/utils/fetchWithRetry'

// Re-export so existing component imports from '@/stores/data' keep working.
export type { DatasetRow, DatasetFreshnessEntry } from '@/types/api'

export interface DatasetMetadata {
  name: string
  description: string
  source: string
  source_url: string
  access_date: string
  row_count: number
  columns: string[]
  /** Pipeline provenance: 'live_ons' (live), 'illustrative_fallback' (example
   * composite — caveat shown), 'static_published' (real published figures
   * compiled statically, not invented), or null (no sidecar). */
  data_type?: string | null
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

/** The flat, hand-curated static freshness.json: {slug: {last_updated, source}}. */
type StaticFreshnessFile = Record<string, { last_updated?: string; source?: string }>

// Match the backend /api/data/freshness thresholds so the static-mode indicator
// classifies identically to the live endpoint.
const FRESH_MAX_HOURS = 168 // 7 days
const STALE_MAX_HOURS = 720 // 30 days

/**
 * Adapt the flat static freshness.json into the {last_updated, age_hours, status}
 * entries FreshnessIndicator expects, deriving age + status from the curated date
 * (clamped at 0 so a future date can't go negative). A missing/unparseable date
 * degrades to "unknown" rather than throwing.
 *
 * Classification matches the live backend exactly (UTC-anchored hours, 168/720
 * thresholds). Note the chart-page DataFreshnessBadge uses its own local-calendar-day
 * heuristic, so the two freshness UIs are not bit-identical right at the ~30-day
 * boundary; both are sound, they just round differently.
 */
export function adaptStaticFreshness(
  flat: StaticFreshnessFile,
): Record<string, DatasetFreshnessEntry> {
  const out: Record<string, DatasetFreshnessEntry> = {}
  const now = Date.now()
  for (const [slug, entry] of Object.entries(flat ?? {})) {
    const ts = entry?.last_updated ? Date.parse(entry.last_updated) : NaN
    if (Number.isNaN(ts)) {
      out[slug] = { last_updated: entry?.last_updated ?? null, age_hours: null, status: 'unknown' }
      continue
    }
    const ageHours = Math.max(0, (now - ts) / 3_600_000)
    out[slug] = {
      last_updated: entry.last_updated ?? null,
      age_hours: Math.round(ageHours * 10) / 10,
      status: ageHours <= FRESH_MAX_HOURS ? 'fresh' : ageHours <= STALE_MAX_HOURS ? 'stale' : 'expired',
    }
  }
  return out
}

export const useDataStore = defineStore('data', () => {
  const datasets = ref<string[]>([])
  const metadata = ref<Map<string, DatasetMetadata>>(new Map())
  const freshness = ref<Record<string, DatasetFreshnessEntry>>({})
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

  async function fetchFreshness(): Promise<Record<string, DatasetFreshnessEntry>> {
    try {
      // Live API returns {datasets, thresholds}; the static build serves the flat
      // curated freshness.json ({slug: {last_updated, source}}) — the same file the
      // chart-page badges read. Adapt the flat shape here so the home-page indicators
      // and the badges work off ONE curated file (otherwise static mode regresses the
      // indicators: a flat file has no `.datasets` key).
      if (STATIC_MODE) {
        const flat = await request<StaticFreshnessFile>('/freshness')
        const adapted = adaptStaticFreshness(flat)
        freshness.value = adapted
        return adapted
      }
      const json = await request<FreshnessResponse>('/freshness')
      freshness.value = json.datasets
      return json.datasets
    } catch (e) {
      console.warn('[WealthLens] Failed to load dataset freshness:', e instanceof Error ? e.message : e)
      return {}
    }
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
    freshness,
    loading,
    error,
    fetchDatasets,
    fetchDataset,
    fetchMetadata,
    fetchAllMetadata,
    fetchFreshness,
    clearMetadata,
  }
})
