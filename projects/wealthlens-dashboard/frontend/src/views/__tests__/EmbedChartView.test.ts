import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import { mount, flushPromises } from "@vue/test-utils"
import { defineComponent, h } from "vue"
import { createPinia, setActivePinia } from "pinia"

const mockRoute = { params: { name: "wealth-shares" }, meta: { embed: true } }

vi.mock("vue-router", () => ({
  useRoute: () => mockRoute,
}))

// Stub the chart loader so the test doesn't pull the echarts graph.
vi.mock("@/config/chartComponents", () => ({
  CHART_COMPONENT_LOADERS: {
    "wealth-shares": async () => ({
      __esModule: true,
      default: {
        name: "WealthSharesChart",
        setup() {
          return () => null
        },
      },
    }),
  },
}))

const mockFetchMetadata = vi.fn()
vi.mock("@/stores/data", () => ({
  useDataStore: () => ({
    fetchMetadata: mockFetchMetadata,
  }),
}))

import EmbedChartView from "@/views/EmbedChartView.vue"

function mountEmbed() {
  return mount(EmbedChartView, {
    global: {
      plugins: [createPinia()],
      stubs: {
        RouterLink: defineComponent({
          setup(_, { slots }) {
            return () => h("a", slots.default?.())
          },
        }),
      },
    },
  })
}

describe("EmbedChartView (RFC-001f)", () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    mockFetchMetadata.mockReset()
    mockFetchMetadata.mockResolvedValue({
      name: "wealth-shares",
      source: "World Inequality Database",
      source_url: "https://wid.world/",
      access_date: "2026-05-14",
      data_type: null,
    })
    document.head.querySelectorAll("[data-wl-meta]").forEach((el) => el.remove())
  })

  afterEach(() => {
    document.head.querySelectorAll("[data-wl-meta]").forEach((el) => el.remove())
  })

  it("renders the chart title and a backlink to the full article", async () => {
    const wrapper = mountEmbed()
    await flushPromises()
    expect(wrapper.text()).toContain("Who owns wealth in the UK?")
    const backlink = wrapper.find(".embed-backlink")
    expect(backlink.attributes("href")).toBe(
      "https://chris0jeky.github.io/wealthlens-hq/charts/wealth-shares",
    )
    expect(backlink.attributes("target")).toBe("_blank")
  })

  it("shows the source line with licence from the single provenance source", async () => {
    const wrapper = mountEmbed()
    await flushPromises()
    const source = wrapper.find(".embed-source")
    expect(source.text()).toContain("World Inequality Database")
    expect(source.text()).toContain("CC-BY 4.0")
  })

  it("is noindex with the article page as canonical", async () => {
    mountEmbed()
    await flushPromises()
    expect(document.head.querySelector('meta[name="robots"]')?.getAttribute("content")).toBe(
      "noindex",
    )
    expect(document.head.querySelector('link[rel="canonical"]')?.getAttribute("href")).toBe(
      "https://chris0jeky.github.io/wealthlens-hq/charts/wealth-shares",
    )
  })

  it("shows the illustrative-composite caveat when the dataset declares it", async () => {
    mockFetchMetadata.mockResolvedValue({
      name: "wealth-shares",
      source: "X",
      source_url: "https://x",
      access_date: "2026-01-01",
      data_type: "illustrative_fallback",
    })
    const wrapper = mountEmbed()
    await flushPromises()
    expect(wrapper.find(".embed-caveat").text()).toContain("Illustrative composite")
  })

  it("posts its height to the parent window for iframe auto-resize", async () => {
    const postMessage = vi.fn()
    const originalParent = window.parent
    Object.defineProperty(window, "parent", { value: { postMessage }, configurable: true })
    try {
      mountEmbed()
      await flushPromises()
      expect(postMessage).toHaveBeenCalledWith(
        expect.objectContaining({
          source: "wealthlens-embed",
          chart: "wealth-shares",
          height: expect.any(Number),
        }),
        "*",
      )
    } finally {
      Object.defineProperty(window, "parent", { value: originalParent, configurable: true })
    }
  })
})
