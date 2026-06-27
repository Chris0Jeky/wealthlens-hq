/**
 * Integration tests: chart data flow.
 *
 * Tests the full data path from the Pinia data store through to the
 * useChartData composable in both API mode and static-data mode,
 * verifying fetch, caching, retry, and error handling.
 *
 * Key design note: The data store reads VITE_STATIC_DATA at module level
 * (as a const), so we must use vi.resetModules() + dynamic import to test
 * each mode in isolation.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import { createPinia, setActivePinia } from "pinia"
import { flushPromises, mount } from "@vue/test-utils"
import { defineComponent, nextTick } from "vue"

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function mockFetchResponse(body: unknown, status = 200): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(body),
    headers: new Headers(),
    redirected: false,
    statusText: "OK",
    type: "basic",
    url: "",
    clone: () => mockFetchResponse(body, status),
    body: null,
    bodyUsed: false,
    arrayBuffer: () => Promise.resolve(new ArrayBuffer(0)),
    blob: () => Promise.resolve(new Blob()),
    formData: () => Promise.resolve(new FormData()),
    text: () => Promise.resolve(JSON.stringify(body)),
    bytes: () => Promise.resolve(new Uint8Array()),
  } as Response
}

function mockFetchInvalidJson(): Response {
  return {
    ok: true,
    status: 200,
    json: () => Promise.reject(new SyntaxError("Unexpected token")),
    headers: new Headers(),
    redirected: false,
    statusText: "OK",
    type: "basic",
    url: "",
    clone: vi.fn(),
    body: null,
    bodyUsed: false,
    arrayBuffer: () => Promise.resolve(new ArrayBuffer(0)),
    blob: () => Promise.resolve(new Blob()),
    formData: () => Promise.resolve(new FormData()),
    text: () => Promise.resolve("not json"),
    bytes: () => Promise.resolve(new Uint8Array()),
  } as unknown as Response
}

const SAMPLE_PAGINATED = {
  data: [
    { year: 2020, value: 0.5 },
    { year: 2021, value: 0.6 },
  ],
  page: 1,
  limit: 100,
  total: 2,
  total_pages: 1,
}

const SAMPLE_METADATA = {
  name: "wealth-shares",
  description: "Top wealth shares over time",
  source: "World Inequality Database",
  source_url: "https://wid.world",
  access_date: "2025-01-15",
  row_count: 100,
  columns: ["year", "value"],
}

const SAMPLE_ALL_METADATA = {
  datasets: [SAMPLE_METADATA],
}

const SAMPLE_DATASET_LIST = {
  datasets: ["wealth-shares", "housing-affordability"],
}

// ---------------------------------------------------------------------------
// Tests: API mode (VITE_STATIC_DATA is not "true")
// ---------------------------------------------------------------------------

describe("Data store — API mode", () => {
  beforeEach(() => {
    vi.resetModules()
    vi.stubEnv("VITE_STATIC_DATA", "false")
    vi.stubEnv("BASE_URL", "/")
    setActivePinia(createPinia())
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.unstubAllEnvs()
    vi.restoreAllMocks()
    vi.useRealTimers()
  })

  it("fetchDatasets populates datasets list from API", async () => {
    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(mockFetchResponse(SAMPLE_DATASET_LIST))

    const { useDataStore } = await import("@/stores/data")
    const store = useDataStore()

    await store.fetchDatasets()

    expect(fetchSpy).toHaveBeenCalledTimes(1)
    expect(fetchSpy.mock.calls[0][0]).toContain("/api/data/")
    expect(store.datasets).toEqual(["wealth-shares", "housing-affordability"])
    expect(store.loading).toBe(false)
    expect(store.error).toBeNull()
  })

  it("fetchDataset returns paginated data from API", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(mockFetchResponse(SAMPLE_PAGINATED))

    const { useDataStore } = await import("@/stores/data")
    const store = useDataStore()

    const result = await store.fetchDataset("wealth-shares", 1, 100)

    expect(result.data).toHaveLength(2)
    expect(result.page).toBe(1)
    expect(result.total).toBe(2)
  })

  it("fetchMetadata caches results — second call does not fetch", async () => {
    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(mockFetchResponse(SAMPLE_METADATA))

    const { useDataStore } = await import("@/stores/data")
    const store = useDataStore()

    const first = await store.fetchMetadata("wealth-shares")
    const second = await store.fetchMetadata("wealth-shares")

    expect(first).toEqual(SAMPLE_METADATA)
    expect(second).toEqual(SAMPLE_METADATA)
    // Only one network call — second was served from cache
    expect(fetchSpy).toHaveBeenCalledTimes(1)
  })

  it("clearMetadata invalidates cache so next fetch hits network", async () => {
    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(mockFetchResponse(SAMPLE_METADATA))

    const { useDataStore } = await import("@/stores/data")
    const store = useDataStore()

    await store.fetchMetadata("wealth-shares")
    store.clearMetadata("wealth-shares")
    await store.fetchMetadata("wealth-shares")

    expect(fetchSpy).toHaveBeenCalledTimes(2)
  })

  it("fetchAllMetadata populates all metadata and caches them", async () => {
    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(mockFetchResponse(SAMPLE_ALL_METADATA))

    const { useDataStore } = await import("@/stores/data")
    const store = useDataStore()

    const result = await store.fetchAllMetadata()

    expect(result).toHaveLength(1)
    expect(result[0].name).toBe("wealth-shares")
    // Should be cached
    expect(store.metadata.get("wealth-shares")).toEqual(SAMPLE_METADATA)
    expect(fetchSpy).toHaveBeenCalledTimes(1)
  })

  it("network failure sets error state on fetchDatasets", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("Network error"))

    const { useDataStore } = await import("@/stores/data")
    const store = useDataStore()

    // fetchDatasets calls fetchWithRetry which retries 3 times with backoff.
    // We must advance timers through all retry delays.
    const promise = store.fetchDatasets()

    // Advance past all retry backoffs (300ms + 600ms + 1200ms)
    await vi.advanceTimersByTimeAsync(300)
    await vi.advanceTimersByTimeAsync(600)
    await vi.advanceTimersByTimeAsync(1200)

    await promise

    expect(store.error).toBe("Could not reach the server")
    expect(store.loading).toBe(false)
    expect(store.datasets).toEqual([])
  })

  it("HTTP 500 triggers retry with exponential backoff", async () => {
    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(mockFetchResponse(null, 500))
      .mockResolvedValueOnce(mockFetchResponse(null, 500))
      .mockResolvedValueOnce(mockFetchResponse(SAMPLE_PAGINATED))

    const { useDataStore } = await import("@/stores/data")
    const store = useDataStore()

    const fetchPromise = store.fetchDataset("wealth-shares")

    // Advance through backoff timers (300ms, 600ms)
    await vi.advanceTimersByTimeAsync(300)
    await vi.advanceTimersByTimeAsync(600)

    const result = await fetchPromise

    expect(fetchSpy).toHaveBeenCalledTimes(3)
    expect(result.data).toHaveLength(2)
  })

  it("HTTP 404 does NOT retry (client error)", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(mockFetchResponse(null, 404))

    const { useDataStore } = await import("@/stores/data")
    const store = useDataStore()

    await expect(store.fetchDataset("nonexistent")).rejects.toThrow("HTTP 404")
    // No retries for 4xx
    expect(fetchSpy).toHaveBeenCalledTimes(1)
  })

  it("invalid JSON response throws descriptive error", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(mockFetchInvalidJson())

    const { useDataStore } = await import("@/stores/data")
    const store = useDataStore()

    await expect(store.fetchDataset("wealth-shares")).rejects.toThrow("Response was not valid JSON")
  })
})

// ---------------------------------------------------------------------------
// Tests: Static data mode (VITE_STATIC_DATA="true")
// ---------------------------------------------------------------------------

describe("Data store — static mode", () => {
  beforeEach(() => {
    vi.resetModules()
    vi.stubEnv("VITE_STATIC_DATA", "true")
    vi.stubEnv("BASE_URL", "/")
    setActivePinia(createPinia())
  })

  afterEach(() => {
    vi.unstubAllEnvs()
    vi.restoreAllMocks()
  })

  it("fetchDatasets uses static URL /data/datasets.json", async () => {
    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(mockFetchResponse(SAMPLE_DATASET_LIST))

    const { useDataStore } = await import("@/stores/data")
    const store = useDataStore()

    await store.fetchDatasets()

    const calledUrl = fetchSpy.mock.calls[0][0] as string
    expect(calledUrl).toContain("/data/datasets.json")
    expect(calledUrl).not.toContain("/api/")
    expect(store.datasets).toEqual(["wealth-shares", "housing-affordability"])
  })

  it("fetchDataset uses static URL /data/{name}.json", async () => {
    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(mockFetchResponse(SAMPLE_PAGINATED))

    const { useDataStore } = await import("@/stores/data")
    const store = useDataStore()

    await store.fetchDataset("wealth-shares")

    const calledUrl = fetchSpy.mock.calls[0][0] as string
    expect(calledUrl).toContain("/data/wealth-shares.json")
  })

  it("fetchMetadata uses static URL /data/{name}-metadata.json", async () => {
    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(mockFetchResponse(SAMPLE_METADATA))

    const { useDataStore } = await import("@/stores/data")
    const store = useDataStore()

    await store.fetchMetadata("wealth-shares")

    const calledUrl = fetchSpy.mock.calls[0][0] as string
    expect(calledUrl).toContain("/data/wealth-shares-metadata.json")
  })

  it("fetchAllMetadata uses static URL /data/all-metadata.json", async () => {
    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(mockFetchResponse(SAMPLE_ALL_METADATA))

    const { useDataStore } = await import("@/stores/data")
    const store = useDataStore()

    await store.fetchAllMetadata()

    const calledUrl = fetchSpy.mock.calls[0][0] as string
    expect(calledUrl).toContain("/data/all-metadata.json")
  })

  it("static mode does NOT retry on failure (maxRetries=0)", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("Network error"))

    const { useDataStore } = await import("@/stores/data")
    const store = useDataStore()

    await store.fetchDatasets()

    // In static mode, fetchWithRetry is called with maxRetries=0
    expect(fetchSpy).toHaveBeenCalledTimes(1)
    expect(store.error).toBe("Could not reach the server")
  })
})

// ---------------------------------------------------------------------------
// Tests: useChartData composable integration
// ---------------------------------------------------------------------------

describe("useChartData composable", () => {
  beforeEach(() => {
    vi.resetModules()
    vi.stubEnv("VITE_STATIC_DATA", "false")
    vi.stubEnv("BASE_URL", "/")
    setActivePinia(createPinia())
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.unstubAllEnvs()
    vi.restoreAllMocks()
    vi.useRealTimers()
  })

  it("returns { rows, loading, error } and fetches data on mount", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(mockFetchResponse(SAMPLE_PAGINATED))

    const { useChartData } = await import("@/composables/useChartData")

    // useChartData must be called inside a component setup (uses onMounted)
    const TestComponent = defineComponent({
      setup() {
        return useChartData("wealth-shares")
      },
      template: "<div />",
    })

    const wrapper = mount(TestComponent)

    // Initially loading
    expect(wrapper.vm.loading).toBe(true)
    expect(wrapper.vm.rows).toEqual([])
    expect(wrapper.vm.error).toBeNull()

    await flushPromises()

    // After fetch resolves
    expect(wrapper.vm.loading).toBe(false)
    expect(wrapper.vm.rows).toEqual(SAMPLE_PAGINATED.data)
    expect(wrapper.vm.error).toBeNull()
  })

  it("propagates network error to error ref", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("Network error"))

    const { useChartData } = await import("@/composables/useChartData")

    const TestComponent = defineComponent({
      setup() {
        return useChartData("wealth-shares")
      },
      template: "<div />",
    })

    const wrapper = mount(TestComponent)

    // Advance through all retry backoffs (300ms + 600ms + 1200ms)
    await vi.advanceTimersByTimeAsync(300)
    await vi.advanceTimersByTimeAsync(600)
    await vi.advanceTimersByTimeAsync(1200)
    await flushPromises()
    await nextTick()

    expect(wrapper.vm.loading).toBe(false)
    expect(wrapper.vm.error).toBe("Could not reach the server")
    expect(wrapper.vm.rows).toEqual([])
  })

  it("propagates HTTP error to error ref", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(mockFetchResponse(null, 404))

    const { useChartData } = await import("@/composables/useChartData")

    const TestComponent = defineComponent({
      setup() {
        return useChartData("nonexistent-dataset")
      },
      template: "<div />",
    })

    const wrapper = mount(TestComponent)
    await flushPromises()
    await nextTick()

    expect(wrapper.vm.loading).toBe(false)
    expect(wrapper.vm.error).toBe("HTTP 404")
    expect(wrapper.vm.rows).toEqual([])
  })

  it("sets loading=false after successful fetch", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(mockFetchResponse(SAMPLE_PAGINATED))

    const { useChartData } = await import("@/composables/useChartData")

    const TestComponent = defineComponent({
      setup() {
        return useChartData("wealth-shares")
      },
      template: "<div />",
    })

    const wrapper = mount(TestComponent)
    await flushPromises()
    await nextTick()

    expect(wrapper.vm.loading).toBe(false)
  })
})
