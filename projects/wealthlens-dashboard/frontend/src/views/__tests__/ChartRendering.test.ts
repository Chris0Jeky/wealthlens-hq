import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { enableAutoUnmount, flushPromises, mount } from "@vue/test-utils"
import { createTestingPinia } from "@pinia/testing"
import { createMemoryHistory, createRouter } from "vue-router"
import WealthSharesChart from "@/components/WealthSharesChart.vue"
import ChartView from "@/views/ChartView.vue"
import { useDataStore, type DatasetRow } from "@/stores/data"

vi.mock("@/composables/useAnalytics", () => ({
  useAnalytics: () => ({ trackEvent: vi.fn() }),
}))
vi.mock("vue-echarts", () => ({
  default: { name: "VChart", props: ["option"], template: '<div class="chart-stub" />' },
}))
vi.mock("echarts/core", () => ({ use: vi.fn() }))
vi.mock("echarts/renderers", () => ({ CanvasRenderer: {} }))
vi.mock("echarts/charts", () => ({ LineChart: {}, BarChart: {} }))
vi.mock("echarts/components", () => ({
  GridComponent: {},
  TooltipComponent: {},
  TitleComponent: {},
  LegendComponent: {},
  MarkLineComponent: {},
  MarkPointComponent: {},
}))

// Synthetic rows exercise transport shapes and window boundaries, not source figures.
const liveRows = [1820, 1999, 2000, 2024].flatMap((year) => [
  { year, variable: "shweal_p90p100_992_j", value: 0.5 },
  { year, variable: "shweal_p99p100_992_j", value: 0.2 },
])
const staticRows = liveRows.map((row) => ({
  ...row,
  percentile: row.variable.includes("p90p100") ? "p90p100" : "p99p100",
}))

function piniaWithRows(rows: DatasetRow[]) {
  const pinia = createTestingPinia({ createSpy: vi.fn })
  vi.mocked(useDataStore(pinia).fetchDataset).mockResolvedValue({
    data: rows,
    total: rows.length,
    page: 1,
    limit: 1000,
    total_pages: 1,
  })
  return pinia
}

type ChartOption = { xAxis: { data: number[] }; series: { data: number[] }[] }

enableAutoUnmount(afterEach)
beforeEach(() => {
  vi.stubGlobal("matchMedia", vi.fn().mockReturnValue({ matches: false }))
  // The #716 range controls ship default off; these specs exercise them switched on.
  vi.stubEnv("VITE_CHART_RANGE_FILTER", "on")
})
afterEach(() => {
  vi.restoreAllMocks()
  vi.unstubAllGlobals()
  vi.unstubAllEnvs()
})

describe("chart rendering regressions", () => {
  it("#696 plots live WID variable rows exactly like static percentile rows", async () => {
    const exported = mount(WealthSharesChart, { global: { plugins: [piniaWithRows(staticRows)] } })
    await flushPromises()
    const expected = exported.findComponent({ name: "VChart" }).props("option") as ChartOption
    expect(expected.xAxis.data).toEqual([1820, 1999, 2000, 2024])
    expect(expected.series.map((s) => s.data)).toEqual([
      [50, 50, 50, 50],
      [20, 20, 20, 20],
    ])

    const live = mount(WealthSharesChart, { global: { plugins: [piniaWithRows(liveRows)] } })
    await flushPromises()
    expect(live.text()).not.toContain("No data available")
    const actual = live.findComponent({ name: "VChart" }).props("option") as ChartOption
    expect(actual.xAxis).toEqual(expected.xAxis)
    expect(actual.series).toEqual(expected.series)
    expect(live.findComponent({ name: "AccessibleDataTable" }).props("rows")).toEqual(
      exported.findComponent({ name: "AccessibleDataTable" }).props("rows"),
    )
    exported.unmount()
    live.unmount()
  })

  it("#716 applies the selected 25y range to plotted years and accessible data", async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: "/charts/:name", component: ChartView },
        { path: "/", component: { template: "<div />" } },
      ],
    })
    await router.push("/charts/wealth-shares")
    await router.isReady()
    const wrapper = mount(ChartView, {
      attachTo: document.body,
      global: {
        plugins: [router, piniaWithRows(staticRows)],
        stubs: {
          StatStrip: true,
          ShareBar: true,
          RelatedCharts: true,
          DataFreshnessBadge: { props: ["dataset"], template: "<div />" },
          ExportButton: true,
        },
      },
    })
    await flushPromises()
    const option = () => wrapper.findComponent({ name: "VChart" }).props("option") as ChartOption
    expect(option().xAxis.data).toEqual([1820, 1999, 2000, 2024])
    const all = wrapper.findAll('[role="tab"]').find((tab) => tab.text() === "All")!
    expect(all.attributes("aria-selected")).toBe("true")
    const shortRange = wrapper.findAll('[role="tab"]').find((tab) => tab.text() === "25y")!
    await shortRange.trigger("click")
    expect(shortRange.attributes("aria-selected")).toBe("true")
    expect(shortRange.attributes("tabindex")).toBe("0")
    expect(option().xAxis.data).toEqual([2000, 2024])
    expect(option().series.map((s) => s.data)).toEqual([
      [50, 50],
      [20, 20],
    ])
    expect(wrapper.findComponent({ name: "AccessibleDataTable" }).props("rows")).toEqual([
      { Year: 2000, "Top 1% share": "20.0%", "Top 10% share": "50.0%" },
      { Year: 2024, "Top 1% share": "20.0%", "Top 10% share": "50.0%" },
    ])
    expect(wrapper.find('[role="img"]').attributes("aria-label")).toContain("from 2000 to 2024")

    await shortRange.trigger("keydown", { key: "Home" })
    expect(all.attributes("aria-selected")).toBe("true")
    expect(shortRange.attributes("aria-selected")).toBe("false")
    expect(shortRange.attributes("tabindex")).toBe("-1")
    expect(document.activeElement).toBe(all.element)
    expect(option().xAxis.data).toEqual([1820, 1999, 2000, 2024])

    await all.trigger("keydown", { key: "End" })
    expect(document.activeElement).toBe(shortRange.element)
    expect(shortRange.attributes("aria-selected")).toBe("true")
    expect(option().xAxis.data).toEqual([2000, 2024])

    await router.push("/charts/generational-wealth")
    await flushPromises()
    expect(wrapper.find('[role="tablist"]').exists()).toBe(false)
    await router.push("/charts/wealth-shares")
    await flushPromises()
    expect(wrapper.find('[role="tab"][aria-selected="true"]').text()).toBe("All")
    expect(option().xAxis.data).toEqual([1820, 1999, 2000, 2024])
    wrapper.unmount()
  })

  it.each([
    {
      name: "productivity-pay",
      range: "10y",
      rows: [2000, 2014, 2015, 2024].map((year) => ({
        year,
        productivity_index: 100,
        pay_index: 90,
        gap_pct: 10,
      })),
      all: [2000, 2014, 2015, 2024],
      filtered: [2015, 2024],
    },
    {
      name: "boe-rates",
      range: "5y",
      rows: ["2000-01-01", "2019-12-31", "2020-01-01", "2024-10-01"].map((date) => ({
        date,
        bank_rate: 1,
        cpi_annual: 2,
      })),
      all: ["2000-01", "2019-12", "2020-01", "2024-10"],
      filtered: ["2020-01", "2024-10"],
    },
  ])(
    "#716 filters $name through the page toolbar",
    async ({ name, range, rows, all, filtered }) => {
      const router = createRouter({
        history: createMemoryHistory(),
        routes: [
          { path: "/charts/:name", component: ChartView },
          { path: "/", component: { template: "<div />" } },
        ],
      })
      await router.push(`/charts/${name}`)
      const pinia = piniaWithRows(rows)
      vi.mocked(useDataStore(pinia).fetchMetadata).mockResolvedValue({
        name,
        description: "",
        source: "",
        source_url: "",
        access_date: "",
        columns: [],
        row_count: rows.length,
        data_type: "static_published",
      })
      const wrapper = mount(ChartView, {
        global: {
          plugins: [router, pinia],
          stubs: {
            StatStrip: true,
            ShareBar: true,
            RelatedCharts: true,
            ExportButton: true,
            DataFreshnessBadge: { props: ["dataset"], template: "<div />" },
          },
        },
      })
      await flushPromises()
      await vi.dynamicImportSettled()
      await flushPromises()
      const option = () => wrapper.findComponent({ name: "VChart" }).props("option") as ChartOption
      expect(option().xAxis.data).toEqual(all)
      await wrapper
        .findAll('[role="tab"]')
        .find((tab) => tab.text() === range)!
        .trigger("click")
      expect(option().xAxis.data).toEqual(filtered)
      expect(option().series.every((series) => series.data.length === filtered.length)).toBe(true)
      expect(wrapper.findComponent({ name: "AccessibleDataTable" }).props("rows")).toHaveLength(2)
      expect(useDataStore(pinia).fetchDataset).toHaveBeenCalledTimes(1)
      wrapper.unmount()
    },
  )
  it("#716 hides the range controls by default (VITE_CHART_RANGE_FILTER unset)", async () => {
    vi.unstubAllEnvs()
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: "/charts/:name", component: ChartView },
        { path: "/", component: { template: "<div />" } },
      ],
    })
    await router.push("/charts/wealth-shares")
    const pinia = piniaWithRows([])
    vi.mocked(useDataStore(pinia).fetchMetadata).mockResolvedValue({
      name: "wealth-shares",
      description: "",
      source: "",
      source_url: "",
      access_date: "",
      columns: [],
      row_count: 0,
      data_type: "static_published",
    })
    const wrapper = mount(ChartView, {
      global: {
        plugins: [router, pinia],
        stubs: {
          StatStrip: true,
          ShareBar: true,
          RelatedCharts: true,
          ExportButton: true,
          DataFreshnessBadge: { props: ["dataset"], template: "<div />" },
        },
      },
    })
    await flushPromises()
    expect(wrapper.findAll('[role="tab"]').map((tab) => tab.text())).not.toContain("25y")
    expect(wrapper.findComponent(WealthSharesChart).props("range")).toBe("All")
    wrapper.unmount()
  })
})
