import { describe, it, expect, vi, beforeEach } from "vitest"
import { mount, flushPromises } from "@vue/test-utils"
import { defineComponent, h } from "vue"
import { createPinia, setActivePinia } from "pinia"

const mockRoute = { params: { name: "wealth-shares" } }

const mockMetadata = {
  name: "wealth-shares",
  description: "Top 1%/10% wealth shares in GB",
  source: "World Inequality Database",
  source_url: "https://wid.world/",
  access_date: "2026-05-14",
  row_count: 150,
  columns: ["year", "percentile", "value"],
}

const mockRows = [
  { year: 2020, percentile: "p99p100", value: 21.3 },
  { year: 2020, percentile: "p90p100", value: 52.1 },
]

const RouterLinkStub = defineComponent({
  name: "RouterLink",
  props: { to: { type: String, required: true } },
  setup(props, { slots }) {
    return () => h("a", { href: props.to }, slots.default?.())
  },
})

vi.mock("vue-router", () => ({
  useRoute: () => mockRoute,
}))

/**
 * Mock the data store. The view loads both metadata and rows through the
 * store (static-deploy aware), so we mock useDataStore directly and never
 * touch global fetch.
 */
const mockFetchDataset = vi.fn()
const mockFetchMetadata = vi.fn()

vi.mock("@/stores/data", () => ({
  useDataStore: () => ({
    fetchDataset: mockFetchDataset,
    fetchMetadata: mockFetchMetadata,
  }),
}))

import DatasetDetailView from "@/views/DatasetDetailView.vue"

function mountView() {
  return mount(DatasetDetailView, {
    global: {
      stubs: { RouterLink: RouterLinkStub },
      plugins: [createPinia()],
    },
  })
}

/**
 * Helper: stub the store's metadata + rows calls for tests that need
 * successful data loading.
 */
function stubSuccessfulFetches() {
  mockFetchMetadata.mockResolvedValue(mockMetadata)
  mockFetchDataset.mockResolvedValue({
    data: mockRows,
    page: 1,
    limit: 100,
    total: mockRows.length,
    total_pages: 1,
  })
}

describe("DatasetDetailView", () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
    mockFetchDataset.mockReset()
    mockFetchMetadata.mockReset()
  })

  it("shows loading state initially", () => {
    mockFetchMetadata.mockReturnValue(new Promise(() => {}))
    mockFetchDataset.mockReturnValue(new Promise(() => {}))
    const wrapper = mountView()
    expect(wrapper.text()).toContain("Loading dataset...")
  })

  it("shows error state when fetch fails", async () => {
    mockFetchMetadata.mockRejectedValue(new Error("Network error"))
    mockFetchDataset.mockRejectedValue(new Error("Network error"))
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.text()).toContain("Network error")
  })

  it("renders metadata after successful fetch", async () => {
    stubSuccessfulFetches()

    const wrapper = mountView()
    await flushPromises()

    expect(wrapper.text()).toContain("wealth-shares")
    expect(wrapper.text()).toContain("World Inequality Database")
    expect(wrapper.text()).toContain("2026-05-14")
  })

  it("renders a data preview table with column headers", async () => {
    stubSuccessfulFetches()

    const wrapper = mountView()
    await flushPromises()

    const headers = wrapper.findAll("th")
    const headerTexts = headers.map((h) => h.text())
    expect(headerTexts).toContain("year")
    expect(headerTexts).toContain("percentile")
    expect(headerTexts).toContain("value")
  })

  it("shows a View Chart link for supported datasets", async () => {
    stubSuccessfulFetches()

    const wrapper = mountView()
    await flushPromises()

    const chartLink = wrapper.find('a[href="/charts/wealth-shares"]')
    expect(chartLink.exists()).toBe(true)
  })

  it("has a back link to the dashboard", () => {
    mockFetchMetadata.mockReturnValue(new Promise(() => {}))
    mockFetchDataset.mockReturnValue(new Promise(() => {}))
    const wrapper = mountView()
    const backLink = wrapper.find('a[href="/"]')
    expect(backLink.exists()).toBe(true)
    expect(backLink.text()).toContain("Back to datasets")
  })

  it("uses semantic sections with aria-labelledby", async () => {
    stubSuccessfulFetches()

    const wrapper = mountView()
    await flushPromises()

    expect(wrapper.find('[aria-labelledby="source-heading"]').exists()).toBe(true)
    expect(wrapper.find('[aria-labelledby="preview-heading"]').exists()).toBe(true)
  })
})
