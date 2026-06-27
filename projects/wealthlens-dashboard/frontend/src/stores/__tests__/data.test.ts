import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import { setActivePinia, createPinia } from "pinia"

/**
 * Mock fetchWithRetry so store tests don't trigger actual retry delays.
 * The mock delegates to globalThis.fetch (which tests stub per-case),
 * but without retry logic or setTimeout backoff.
 */
vi.mock("@/utils/fetchWithRetry", () => ({
  fetchWithRetry: (url: string) => globalThis.fetch(url),
}))

import { useDataStore, adaptStaticFreshness } from "@/stores/data"

describe("useDataStore", () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
  })

  it("has empty datasets initially", () => {
    const store = useDataStore()
    expect(store.datasets).toEqual([])
  })

  it("is not loading initially", () => {
    const store = useDataStore()
    expect(store.loading).toBe(false)
  })

  it("has no error initially", () => {
    const store = useDataStore()
    expect(store.error).toBeNull()
  })

  describe("fetchDatasets", () => {
    it("populates the datasets list on success", async () => {
      const mockDatasets = ["wealth-shares", "housing-affordability"]
      vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
        ok: true,
        json: async () => ({ datasets: mockDatasets }),
      } as Response)

      const store = useDataStore()
      await store.fetchDatasets()

      expect(store.datasets).toEqual(mockDatasets)
      expect(store.loading).toBe(false)
      expect(store.error).toBeNull()
    })

    it("sets loading to true while fetching", async () => {
      let resolveFetch!: (value: Response) => void
      vi.spyOn(globalThis, "fetch").mockReturnValueOnce(
        new Promise((resolve) => {
          resolveFetch = resolve
        }),
      )

      const store = useDataStore()
      const fetchPromise = store.fetchDatasets()
      expect(store.loading).toBe(true)

      resolveFetch({
        ok: true,
        json: async () => ({ datasets: [] }),
      } as Response)
      await fetchPromise

      expect(store.loading).toBe(false)
    })

    it("sets error on non-ok HTTP response", async () => {
      vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
        ok: false,
        status: 500,
      } as Response)

      const store = useDataStore()
      await store.fetchDatasets()

      expect(store.error).toBe("HTTP 500")
      expect(store.loading).toBe(false)
      expect(store.datasets).toEqual([])
    })

    it("sets error on network failure", async () => {
      vi.spyOn(globalThis, "fetch").mockRejectedValueOnce(new TypeError("Failed to fetch"))

      const store = useDataStore()
      await store.fetchDatasets()

      expect(store.error).toBe("Could not reach the server")
      expect(store.loading).toBe(false)
    })

    it("clears previous error on successful retry", async () => {
      const fetchSpy = vi.spyOn(globalThis, "fetch")
      fetchSpy.mockRejectedValueOnce(new Error("Network error"))

      const store = useDataStore()
      await store.fetchDatasets()
      expect(store.error).toBe("Could not reach the server")

      fetchSpy.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ datasets: ["recovered"] }),
      } as Response)

      await store.fetchDatasets()
      expect(store.error).toBeNull()
      expect(store.datasets).toEqual(["recovered"])
    })

    it("handles non-Error thrown values", async () => {
      vi.spyOn(globalThis, "fetch").mockRejectedValueOnce("string error")

      const store = useDataStore()
      await store.fetchDatasets()

      expect(store.error).toBe("Could not reach the server")
      expect(store.loading).toBe(false)
    })
  })

  describe("fetchDataset", () => {
    it("returns paginated data on success", async () => {
      const mockResponse = {
        data: [{ decile: 1, wealth: 15000 }],
        page: 1,
        limit: 100,
        total: 1,
        total_pages: 1,
      }
      vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response)

      const store = useDataStore()
      const result = await store.fetchDataset("wealth-shares")

      expect(result).toEqual(mockResponse)
      expect(globalThis.fetch).toHaveBeenCalledWith("/api/data/wealth-shares?page=1&limit=100")
    })

    it("passes pagination params", async () => {
      vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: [], page: 2, limit: 50, total: 0, total_pages: 0 }),
      } as Response)

      const store = useDataStore()
      await store.fetchDataset("wealth-shares", 2, 50)

      expect(globalThis.fetch).toHaveBeenCalledWith("/api/data/wealth-shares?page=2&limit=50")
    })

    it("throws on non-ok response", async () => {
      vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
        ok: false,
        status: 404,
      } as Response)

      const store = useDataStore()
      await expect(store.fetchDataset("missing")).rejects.toThrow("HTTP 404")
    })
  })

  describe("fetchMetadata", () => {
    it("fetches and caches metadata", async () => {
      const mockMeta = {
        name: "wealth-shares",
        description: "Top 1%/10% wealth shares",
        source: "World Inequality Database",
        source_url: "https://wid.world/",
        access_date: "2026-05-14",
        row_count: 100,
        columns: ["year", "percentile", "share"],
      }
      vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
        ok: true,
        json: async () => mockMeta,
      } as Response)

      const store = useDataStore()
      const result = await store.fetchMetadata("wealth-shares")

      expect(result).toEqual(mockMeta)
      expect(store.metadata.get("wealth-shares")).toEqual(mockMeta)
    })

    it("returns cached metadata without refetching", async () => {
      const mockMeta = {
        name: "wealth-shares",
        description: "Top 1%/10% wealth shares",
        source: "WID",
        source_url: "https://wid.world/",
        access_date: "2026-05-14",
        row_count: 50,
        columns: ["year"],
      }
      const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
        ok: true,
        json: async () => mockMeta,
      } as Response)

      const store = useDataStore()
      await store.fetchMetadata("wealth-shares")
      const second = await store.fetchMetadata("wealth-shares")

      expect(second).toEqual(mockMeta)
      expect(fetchSpy).toHaveBeenCalledTimes(1)
    })
  })

  describe("fetchAllMetadata", () => {
    it("fetches all metadata and populates cache", async () => {
      const mockDatasets = [
        {
          name: "a",
          description: "A",
          source: "S",
          source_url: "http://x",
          access_date: "2026-01-01",
          row_count: 10,
          columns: ["x"],
        },
        {
          name: "b",
          description: "B",
          source: "S",
          source_url: "http://y",
          access_date: "2026-01-01",
          row_count: 20,
          columns: ["y"],
        },
      ]
      vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
        ok: true,
        json: async () => ({ datasets: mockDatasets }),
      } as Response)

      const store = useDataStore()
      const result = await store.fetchAllMetadata()

      expect(result).toEqual(mockDatasets)
      expect(store.metadata.get("a")).toEqual(mockDatasets[0])
      expect(store.metadata.get("b")).toEqual(mockDatasets[1])
    })
  })

  describe("clearMetadata", () => {
    it("clears a single entry by name", async () => {
      vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          name: "x",
          description: "",
          source: "",
          source_url: "",
          access_date: "",
          row_count: 0,
          columns: [],
        }),
      } as Response)

      const store = useDataStore()
      await store.fetchMetadata("x")
      expect(store.metadata.get("x")).toBeDefined()

      store.clearMetadata("x")
      expect(store.metadata.get("x")).toBeUndefined()
    })

    it("clears all entries when no name given", async () => {
      const store = useDataStore()
      store.metadata.set("a", {
        name: "a",
        description: "",
        source: "",
        source_url: "",
        access_date: "",
        row_count: 0,
        columns: [],
      })
      store.metadata.set("b", {
        name: "b",
        description: "",
        source: "",
        source_url: "",
        access_date: "",
        row_count: 0,
        columns: [],
      })

      store.clearMetadata()
      expect(store.metadata.size).toBe(0)
    })
  })

  describe("adaptStaticFreshness (static-mode flat freshness.json)", () => {
    // Freeze "now" so the derived age/status is deterministic regardless of run date.
    beforeEach(() => {
      vi.useFakeTimers({ toFake: ["Date"] })
      vi.setSystemTime(new Date("2026-06-15T12:00:00Z"))
    })
    afterEach(() => {
      vi.useRealTimers()
    })

    it("derives age_hours + status from the curated date for FreshnessIndicator", () => {
      const out = adaptStaticFreshness({
        "wealth-shares": { last_updated: "2026-06-14", source: "ONS" }, // ~1 day -> fresh
        "tax-composition": { last_updated: "2026-06-01", source: "HMRC" }, // 14 days -> stale
        "boe-rates": { last_updated: "2026-01-01", source: "BoE" }, // >30 days -> expired
      })
      expect(out["wealth-shares"]).toMatchObject({ last_updated: "2026-06-14", status: "fresh" })
      expect(out["wealth-shares"].age_hours).toBeGreaterThanOrEqual(0)
      expect(out["tax-composition"].status).toBe("stale")
      expect(out["boe-rates"].status).toBe("expired")
    })

    it("degrades a missing/unparseable date to unknown (no throw)", () => {
      const out = adaptStaticFreshness({
        a: { source: "no date" },
        b: { last_updated: "not-a-date", source: "bad" },
      })
      expect(out["a"]).toEqual({ last_updated: null, age_hours: null, status: "unknown" })
      expect(out["b"].status).toBe("unknown")
    })

    it("clamps a future date to age 0 / fresh (never negative)", () => {
      const out = adaptStaticFreshness({ x: { last_updated: "2026-12-31", source: "s" } })
      expect(out["x"].age_hours).toBe(0)
      expect(out["x"].status).toBe("fresh")
    })
  })
})
