import { describe, expect, it, vi } from "vitest"
import { nextTick } from "vue"
import { useDatasetSearch } from "@/composables/useDatasetSearch"

vi.mock("@/composables/useDebounce", () => ({
  useDebounce: (source: unknown) => source,
}))

describe("useDatasetSearch", () => {
  it("categorises regional income datasets as regional", async () => {
    const search = useDatasetSearch()
    search.selectedCategories.value = ["regional"]
    await nextTick()

    const names = search.filteredDatasets.value.map((entry) => entry.name)
    expect(names).toContain("gdhi-by-region")
  })
})
