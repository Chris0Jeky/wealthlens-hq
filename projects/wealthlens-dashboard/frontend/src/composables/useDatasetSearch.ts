import { ref, computed, type Ref } from "vue"
import { useDebounce } from "@/composables/useDebounce"
import { CHART_METADATA, type ChartMeta } from "@/utils/chartConstants"

/**
 * Dataset entry with searchable metadata.
 * Built from CHART_METADATA — the single source of truth for dataset info.
 */
export interface DatasetEntry {
  name: string
  title: string
  description: string
  category: string
  tags: string[]
}

/** Available filter categories for datasets. */
export const DATASET_CATEGORIES = [
  { id: "wealth", label: "Wealth" },
  { id: "housing", label: "Housing" },
  { id: "tax", label: "Tax" },
  { id: "income", label: "Income" },
  { id: "regional", label: "Regional" },
] as const

export type CategoryId = (typeof DATASET_CATEGORIES)[number]["id"]

/**
 * Infer category and tags from dataset name and description.
 * This keeps metadata collocated with chartConstants rather than duplicating it.
 */
function categoriseDataset(meta: ChartMeta): { category: CategoryId; tags: string[] } {
  const text = `${meta.name} ${meta.title} ${meta.description}`.toLowerCase()

  if (text.includes("housing") || text.includes("affordability")) {
    return { category: "housing", tags: ["housing", "regional", "ons"] }
  }
  if (text.includes("cgt") || text.includes("capital gains") || text.includes("tax")) {
    return { category: "tax", tags: ["tax", "hmrc", "capital gains"] }
  }
  if (text.includes("region")) {
    return { category: "regional", tags: ["regional"] }
  }
  if (text.includes("income") || text.includes("earnings") || text.includes("pay")) {
    return { category: "income", tags: ["income", "earnings"] }
  }
  if (text.includes("wealth") || text.includes("decile")) {
    return { category: "wealth", tags: ["wealth", "inequality", "ons"] }
  }

  return { category: "wealth", tags: ["inequality"] }
}

/** Build the searchable dataset list from chart metadata. */
function buildDatasetEntries(): DatasetEntry[] {
  return Object.values(CHART_METADATA).map((meta) => {
    const { category, tags } = categoriseDataset(meta)
    return {
      name: meta.name,
      title: meta.title,
      description: meta.description,
      category,
      tags,
    }
  })
}

/**
 * Case-insensitive substring match across title, description, name, and tags.
 * Returns true if every word in the query matches at least one field.
 */
function matchesQuery(entry: DatasetEntry, query: string): boolean {
  if (!query.trim()) return true

  const searchable = [entry.name, entry.title, entry.description, entry.category, ...entry.tags]
    .join(" ")
    .toLowerCase()

  const words = query.toLowerCase().trim().split(/\s+/)
  return words.every((word) => searchable.includes(word))
}

/**
 * Composable for searching and filtering datasets on the home page.
 *
 * @param debounceMs - debounce delay for the search input (default 200ms)
 * @returns reactive search state and filtered results
 */
export function useDatasetSearch(debounceMs = 200) {
  const query = ref("")
  const debouncedQuery = useDebounce(query, debounceMs)
  const selectedCategories: Ref<string[]> = ref([])

  const allDatasets = ref<DatasetEntry[]>(buildDatasetEntries())

  const filteredDatasets = computed(() => {
    let results = allDatasets.value

    // Apply text search
    const q = debouncedQuery.value
    if (q.trim()) {
      results = results.filter((entry) => matchesQuery(entry, q))
    }

    // Apply category filter
    if (selectedCategories.value.length > 0) {
      const cats = new Set(selectedCategories.value)
      results = results.filter((entry) => cats.has(entry.category))
    }

    return results
  })

  const isSearchActive = computed(() => {
    return debouncedQuery.value.trim().length > 0 || selectedCategories.value.length > 0
  })

  const resultCount = computed(() => filteredDatasets.value.length)

  function clearSearch() {
    query.value = ""
    selectedCategories.value = []
  }

  return {
    query,
    debouncedQuery,
    selectedCategories,
    allDatasets,
    filteredDatasets,
    isSearchActive,
    resultCount,
    clearSearch,
  }
}
