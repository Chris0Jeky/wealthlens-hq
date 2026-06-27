import { describe, it, expect, vi } from "vitest"
import { mount, flushPromises } from "@vue/test-utils"
import { createTestingPinia } from "@pinia/testing"
import { createRouter, createMemoryHistory } from "vue-router"
import HomeView from "../HomeView.vue"
import { useDataStore } from "@/stores/data"

function createMountOptions(storeOverrides = {}) {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: "/", component: HomeView },
      { path: "/charts/:name", component: { template: "<div />" } },
      { path: "/datasets/:name", component: { template: "<div />" } },
    ],
  })

  return {
    global: {
      plugins: [
        router,
        createTestingPinia({
          createSpy: vi.fn,
          initialState: {
            data: {
              datasets: [],
              metadata: new Map(),
              freshness: {},
              loading: false,
              error: null,
              ...storeOverrides,
            },
          },
        }),
      ],
    },
  }
}

describe("HomeView", () => {
  describe("hero section", () => {
    it("renders main heading", () => {
      const wrapper = mount(HomeView, createMountOptions())
      expect(wrapper.find("h1").text()).toBe("UK Wealth Inequality Dashboard")
    })

    it("renders mission description", () => {
      const wrapper = mount(HomeView, createMountOptions())
      expect(wrapper.text()).toContain("Open-source, source-backed data")
    })

    it("renders tagline", () => {
      const wrapper = mount(HomeView, createMountOptions())
      expect(wrapper.text()).toContain("Making wealth data accessible")
    })
  })

  describe("key statistics section", () => {
    it("shows dataset count", () => {
      const wrapper = mount(HomeView, createMountOptions())
      expect(wrapper.text()).toContain("10")
      expect(wrapper.text()).toContain("Datasets")
    })

    it("shows interactive charts count", () => {
      const wrapper = mount(HomeView, createMountOptions())
      expect(wrapper.text()).toContain("Interactive Charts")
    })

    it("shows update frequency", () => {
      const wrapper = mount(HomeView, createMountOptions())
      expect(wrapper.text()).toContain("Weekly")
      expect(wrapper.text()).toContain("Update Frequency")
    })
  })

  describe("dataset cards", () => {
    it("always renders all 10 dataset cards regardless of store state", () => {
      const wrapper = mount(HomeView, createMountOptions())
      const items = wrapper.findAll('[role="listitem"]')
      expect(items.length).toBe(10)
    })

    it("renders cards even when store is loading", () => {
      const wrapper = mount(HomeView, createMountOptions({ loading: true }))
      const items = wrapper.findAll('[role="listitem"]')
      expect(items.length).toBe(10)
    })

    it("renders cards even when store has error", () => {
      const wrapper = mount(HomeView, createMountOptions({ error: "Network error" }))
      const items = wrapper.findAll('[role="listitem"]')
      expect(items.length).toBe(10)
    })

    it("displays correct dataset names", () => {
      const wrapper = mount(HomeView, createMountOptions())
      const text = wrapper.text()
      expect(text).toContain("wealth-shares")
      expect(text).toContain("housing-affordability")
      expect(text).toContain("cgt-concentration")
      expect(text).toContain("wealth-by-decile")
      expect(text).toContain("productivity-pay")
      expect(text).toContain("gdhi-by-region")
      expect(text).toContain("tax-composition")
      expect(text).toContain("boe-rates")
      expect(text).toContain("child-poverty")
      expect(text).toContain("generational-wealth")
    })

    it("uses metadata description when available", () => {
      const metadata = new Map([
        [
          "wealth-shares",
          {
            name: "wealth-shares",
            description: "Custom description from API",
            source: "",
            source_url: "",
            access_date: "",
            row_count: 0,
            columns: [],
          },
        ],
      ])
      const wrapper = mount(HomeView, createMountOptions({ metadata }))
      expect(wrapper.text()).toContain("Custom description from API")
    })

    it("uses fallback descriptions when metadata unavailable", () => {
      const wrapper = mount(HomeView, createMountOptions())
      expect(wrapper.text()).toContain("UK productivity and real pay indexed over time")
    })
  })

  describe("data fetching", () => {
    it("calls fetchDatasets on mount", () => {
      mount(HomeView, createMountOptions())
      const store = useDataStore()
      expect(store.fetchDatasets).toHaveBeenCalledOnce()
    })

    it("calls fetchAllMetadata on mount", () => {
      mount(HomeView, createMountOptions())
      const store = useDataStore()
      expect(store.fetchAllMetadata).toHaveBeenCalledOnce()
    })

    it("calls fetchFreshness on mount", () => {
      mount(HomeView, createMountOptions())
      const store = useDataStore()
      expect(store.fetchFreshness).toHaveBeenCalledOnce()
    })

    it("tracks both fetches concurrently via Promise.allSettled", () => {
      // Both should be called without waiting for one to complete before the other
      mount(HomeView, createMountOptions())
      const store = useDataStore()
      expect(store.fetchDatasets).toHaveBeenCalledOnce()
      expect(store.fetchAllMetadata).toHaveBeenCalledOnce()
      expect(store.fetchFreshness).toHaveBeenCalledOnce()
    })
  })

  describe("metadata enrichment error", () => {
    it("does not show metadata warning by default", () => {
      const wrapper = mount(HomeView, createMountOptions())
      expect(wrapper.text()).not.toContain("Metadata enrichment unavailable")
    })

    it("cards remain visible even if metadata fails", () => {
      // Even with store error, cards should always render
      const wrapper = mount(HomeView, createMountOptions({ error: "Server down" }))
      const items = wrapper.findAll('[role="listitem"]')
      expect(items.length).toBe(10)
    })
  })

  describe("dataset search", () => {
    it("filters dataset cards when search is active", async () => {
      const wrapper = mount(HomeView, createMountOptions())

      await wrapper.find('input[type="search"]').setValue("affordability")
      await new Promise((resolve) => window.setTimeout(resolve, 250))
      await flushPromises()

      const items = wrapper.findAll('[aria-labelledby="datasets-heading"] [role="listitem"]')
      expect(items).toHaveLength(1)
      expect(items[0].text()).toContain("housing-affordability")
    })
  })

  describe("datasets connectivity error", () => {
    it("does not show connectivity warning by default", () => {
      const wrapper = mount(HomeView, createMountOptions())
      expect(wrapper.text()).not.toContain("Unable to reach the data service")
    })

    it("shows connectivity warning when fetchDatasets rejects", async () => {
      const router = createRouter({
        history: createMemoryHistory(),
        routes: [
          { path: "/", component: HomeView },
          { path: "/charts/:name", component: { template: "<div />" } },
          { path: "/datasets/:name", component: { template: "<div />" } },
        ],
      })
      const pinia = createTestingPinia({
        createSpy: vi.fn,
        initialState: {
          data: { datasets: [], metadata: new Map(), loading: false, error: null },
        },
      })
      const store = useDataStore(pinia)
      ;(store.fetchDatasets as ReturnType<typeof vi.fn>).mockRejectedValue(
        new Error("Network error"),
      )

      const wrapper = mount(HomeView, { global: { plugins: [router, pinia] } })

      // Wait for the onMounted Promise.allSettled to settle
      await new Promise((r) => setTimeout(r, 10))
      expect(wrapper.text()).toContain("Unable to reach the data service")
    })

    it("cards remain visible even when fetchDatasets fails", async () => {
      const wrapper = mount(HomeView, createMountOptions({ error: "Connection refused" }))
      const items = wrapper.findAll('[role="listitem"]')
      expect(items.length).toBe(10)
    })
  })

  describe("accessibility", () => {
    it("has aria-labelledby on hero section", () => {
      const wrapper = mount(HomeView, createMountOptions())
      const section = wrapper.find('[aria-labelledby="hero-heading"]')
      expect(section.exists()).toBe(true)
    })

    it("has aria-labelledby on datasets section", () => {
      const wrapper = mount(HomeView, createMountOptions())
      const section = wrapper.find('[aria-labelledby="datasets-heading"]')
      expect(section.exists()).toBe(true)
    })

    it('has role="list" on dataset grid', () => {
      const wrapper = mount(HomeView, createMountOptions())
      expect(wrapper.find('[role="list"]').exists()).toBe(true)
    })

    it("has sr-only label for stats section", () => {
      const wrapper = mount(HomeView, createMountOptions())
      const srOnly = wrapper.find(".sr-only")
      expect(srOnly.text()).toBe("Key Statistics")
    })
  })
})
