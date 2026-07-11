import { describe, it, expect, vi } from "vitest"
import { mount, flushPromises } from "@vue/test-utils"
import { createTestingPinia } from "@pinia/testing"
import { createRouter, createMemoryHistory } from "vue-router"
import HomeView from "../HomeView.vue"
import { useDataStore } from "@/stores/data"

// The front page lazy-loads the featured chart; mock it so tests don't race
// the echarts dynamic import against environment teardown.
vi.mock("@/components/WealthSharesChart.vue", async () => {
  const { defineComponent, h } = await import("vue")
  return {
    __esModule: true,
    default: defineComponent({
      name: "WealthSharesChart",
      setup() {
        return () =>
          h("div", {
            class: "wealth-shares-chart-stub",
            role: "img",
            "aria-label": "Featured chart stub",
          })
      },
    }),
  }
})

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
  describe("lead story", () => {
    it("leads with the sourced 57% headline figure in the h1", () => {
      const wrapper = mount(HomeView, createMountOptions())
      const h1 = wrapper.find("h1")
      expect(h1.text()).toContain("wealthiest 10%")
      expect(h1.text()).toContain("57")
      expect(h1.text()).toContain("UK personal wealth")
    })

    it("cites the WID source with access date next to the figure", () => {
      const wrapper = mount(HomeView, createMountOptions())
      const source = wrapper.find(".lead-source")
      expect(source.text()).toContain("World Inequality Database")
      expect(source.text()).toContain("accessed 14 May 2026")
      expect(source.text()).toContain("CC-BY 4.0")
    })

    it("grounds the standfirst in the same verified series (21% / 43%)", () => {
      const wrapper = mount(HomeView, createMountOptions())
      expect(wrapper.text()).toContain("top 1% alone hold 21%")
      expect(wrapper.text()).toContain("share 43%")
    })

    it("links the lead to the full wealth-shares article", () => {
      const wrapper = mount(HomeView, createMountOptions())
      const links = wrapper.findAll('a[href="/charts/wealth-shares"]')
      expect(links.length).toBeGreaterThan(0)
    })
  })

  describe("honesty regressions (reality-check F10)", () => {
    it("no longer claims a Weekly update frequency", () => {
      const wrapper = mount(HomeView, createMountOptions())
      expect(wrapper.text()).not.toContain("Weekly")
      expect(wrapper.text()).not.toContain("Update Frequency")
    })
  })

  describe("tools row (de-orphaning, F6)", () => {
    it("links all four tools and the FAQ", () => {
      const wrapper = mount(HomeView, createMountOptions())
      for (const href of [
        "/tools/wealth-scale",
        "/tools/wealth-calculator",
        "/tools/tax-calculator",
        "/tools/wealth-tax-simulator",
        "/faq",
      ]) {
        expect(wrapper.find(`a[href="${href}"]`).exists()).toBe(true)
      }
    })
  })

  describe("chart index by pillar", () => {
    it("links all 12 charts exactly once each", () => {
      const wrapper = mount(HomeView, createMountOptions())
      const hrefs = wrapper
        .findAll(".pillar-link")
        .map((a) => a.attributes("href"))
        .sort()
      expect(hrefs.length).toBe(12)
      expect(new Set(hrefs).size).toBe(12)
      expect(hrefs).toContain("/charts/wage-stagnation")
      expect(hrefs).toContain("/charts/inheritance-tax")
    })

    it("shows the four pillar labels", () => {
      const wrapper = mount(HomeView, createMountOptions())
      const labels = wrapper.findAll(".pillar-label").map((el) => el.text())
      expect(labels).toEqual(["Wealth", "Housing", "Tax", "Income & work"])
    })

    it("derives chart titles from the article config (no drifting copy)", () => {
      const wrapper = mount(HomeView, createMountOptions())
      expect(wrapper.text()).toContain("Who owns wealth in the UK? Same lot, mostly.")
      expect(wrapper.text()).toContain("Real Wage Stagnation")
    })
  })

  describe("featured chart", () => {
    it("renders a figure with a cited caption", () => {
      const wrapper = mount(HomeView, createMountOptions())
      const caption = wrapper.find(".featured-caption")
      expect(caption.text()).toContain("World Inequality Database")
      expect(caption.text()).toContain("1820–2024")
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
    it("has aria-labelledby on the lead section", () => {
      const wrapper = mount(HomeView, createMountOptions())
      const section = wrapper.find('[aria-labelledby="lead-heading"]')
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

    it("voices the hero figure unit for screen readers", () => {
      const wrapper = mount(HomeView, createMountOptions())
      const srOnly = wrapper.find(".lead-figure .sr-only")
      expect(srOnly.text()).toContain("per cent")
    })
  })
})
