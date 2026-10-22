import { describe, it, expect, vi, beforeEach } from "vitest"
import { flushPromises, mount } from "@vue/test-utils"
import { createPinia, setActivePinia } from "pinia"
import { ref, shallowRef } from "vue"

/**
 * ChildPovertyChart tests — focused on the ADDITION in the a11y slice: the
 * accessible data-table fallback (WCAG 1.1.1). The shared loading/error/no-data
 * and happy-path render behaviour is covered uniformly in ChartComponents.test.ts.
 * Here we test that:
 *   - the data table exposes the chart's exact column headers,
 *   - the table has one tbody row per plotted region,
 *   - each row maps the chart's VERBATIM, poverty-rate-descending figures into the
 *     right cells (per-CELL mapping, so a column swap/reorder fails here).
 *
 * The component reads data through useChartData(), so we mock that composable
 * (mirroring the other chart tests) to drive rows/loading/error directly.
 */

const { mockFetchMetadata } = vi.hoisted(() => ({ mockFetchMetadata: vi.fn() }))
vi.mock("@/stores/data", () => ({
  useDataStore: () => ({ fetchMetadata: mockFetchMetadata }),
}))

let mockRows: ReturnType<typeof shallowRef>
let mockLoading: ReturnType<typeof ref>
let mockError: ReturnType<typeof ref>

vi.mock("@/composables/useChartData", () => ({
  useChartData: () => ({
    rows: mockRows,
    loading: mockLoading,
    error: mockError,
  }),
}))

// Stub vue-echarts so we exercise the table behaviour without ECharts internals.
vi.mock("vue-echarts", () => ({
  default: {
    name: "VChart",
    template: '<div class="vchart-stub" />',
    props: ["option", "autoresize"],
  },
}))

vi.mock("echarts/core", () => ({ use: vi.fn() }))
vi.mock("echarts/renderers", () => ({ CanvasRenderer: {} }))
vi.mock("echarts/charts", () => ({ BarChart: {} }))
vi.mock("echarts/components", () => ({
  GridComponent: {},
  TooltipComponent: {},
  TitleComponent: {},
  LegendComponent: {},
  MarkLineComponent: {},
}))

import ChildPovertyChart from "@/components/ChildPovertyChart.vue"
import { chartConfigs } from "@/config/chartArticles"

/**
 * Two regions with deliberately distinct values per column so a column swap would
 * fail the per-cell assertions. The chart sorts by poverty rate DESCENDING, so the
 * deliberately-lower-rate row is listed second here to also prove the table mirrors
 * the chart's sort order rather than the raw input order.
 */
const CHILD_POVERTY_ROWS = [
  {
    region: "South East",
    child_poverty_pct: 22,
    children_in_poverty: 310000,
    national_avg_pct: 29.8,
    above_national_avg: false,
  },
  {
    region: "North East",
    child_poverty_pct: 38,
    children_in_poverty: 185000,
    national_avg_pct: 29.8,
    above_national_avg: true,
  },
]

describe("ChildPovertyChart accessible data table", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockFetchMetadata.mockResolvedValue({
      source: "DWP HBAI, tables 4.16ts and 4.17ts",
      source_url:
        "https://www.gov.uk/government/statistics/households-below-average-income-for-financial-years-ending-1995-to-2024",
      access_date: "2026-10-22",
      data_type: "live_ons",
    })
    setActivePinia(createPinia())
    mockRows = shallowRef(CHILD_POVERTY_ROWS)
    mockLoading = ref(false)
    mockError = ref(null)

    Object.defineProperty(window, "matchMedia", {
      writable: true,
      configurable: true,
      value: vi.fn().mockImplementation((query: string) => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    })
  })

  it("renders an accessible data table with the chart's column headers", () => {
    const wrapper = mount(ChildPovertyChart)
    expect(wrapper.text()).toContain("View data as table")
    const headers = wrapper.findAll("thead th").map((th) => th.text())
    expect(headers).toEqual([
      "Region",
      "Child poverty (%)",
      "Children in poverty",
      "National average (%)",
    ])
  })

  it("has one tbody row per plotted region", () => {
    const wrapper = mount(ChildPovertyChart)
    expect(wrapper.findAll("tbody tr")).toHaveLength(2)
  })

  it("maps the chart's VERBATIM, poverty-rate-descending figures per cell", () => {
    const wrapper = mount(ChildPovertyChart)
    const bodyRows = wrapper.findAll("tbody tr")
    const cells = (i: number) => bodyRows[i].findAll("td").map((td) => td.text())

    // en-GB locale-formatting is computed (not hardcoded) so the expectation stays
    // correct regardless of grouping rules: e.g. 185000 -> "185,000".
    const fmt = (n: number) => Number(n).toLocaleString("en-GB")

    // Row 0 = highest poverty rate (North East), proving the table follows the
    // chart's descending sort, NOT the raw input order (South East was first in).
    expect(cells(0)).toEqual(["North East", fmt(38), fmt(185000), fmt(29.8)])
    // Row 1 = lower poverty rate (South East).
    expect(cells(1)).toEqual(["South East", fmt(22), fmt(310000), fmt(29.8)])
  })

  it("cites the official AHC tables, averaging period and published precision", async () => {
    const wrapper = mount(ChildPovertyChart)
    await flushPromises()
    const caption = wrapper.find("table caption").text()
    expect(caption).toContain("after housing costs (AHC)")
    expect(caption).toContain("2021/22 to 2023/24 (three-year average)")
    expect(caption).toContain("Source: DWP HBAI, tables 4.16ts and 4.17ts")
    expect(caption).toContain("nearest hundred thousand")
    expect(caption).not.toContain("Children in Low Income Families")
    expect(wrapper.find("[role='note']").exists()).toBe(false)
    expect(wrapper.find("a").attributes("href")).toContain("households-below-average-income")
    expect(wrapper.text()).toContain("accessed 2026-10-22")
    expect(wrapper.find("[role='img']").attributes("aria-label")).toContain("three-year average")
  })

  it.each([null, "unverified", "illustrative_fallback"])(
    "exposes an accessible caveat for %s provenance",
    async (dataType) => {
      mockFetchMetadata.mockResolvedValue({ data_type: dataType })
      const wrapper = mount(ChildPovertyChart)
      await flushPromises()
      const caveat = wrapper.find("[role='note']").text()
      expect(caveat).toMatch(/unverified|Unverified/)
      expect(wrapper.find("table caption").text()).toContain(caveat)
      expect(wrapper.find("[role='img']").attributes("aria-label")).toContain(caveat)
      expect(wrapper.find("a").exists()).toBe(false)
    },
  )

  it("rejects the former CiLIF citation even when marked static published", async () => {
    mockFetchMetadata.mockResolvedValue({
      data_type: "static_published",
      source_url:
        "https://www.gov.uk/government/statistics/children-in-low-income-families-local-area-statistics-2014-to-2023",
    })
    const wrapper = mount(ChildPovertyChart)
    await flushPromises()
    expect(wrapper.find("[role='note']").text()).toContain("Unverified provenance")
    expect(wrapper.find("a").exists()).toBe(false)
  })

  it("keeps unverified provenance visible when metadata cannot be fetched", async () => {
    mockFetchMetadata.mockRejectedValue(new Error("metadata unavailable"))
    const wrapper = mount(ChildPovertyChart)
    await flushPromises()
    expect(wrapper.find("[role='note']").text()).toContain("Unverified provenance")
  })

  it("renders a missing children-in-poverty count as —, not 0", () => {
    // A null source value must NOT be coerced to 0 (which would falsely claim
    // zero children in poverty). chartData parses with Number(), and
    // Number(null)===0, so the table must re-derive from the raw row and map
    // missing values to null so AccessibleDataTable renders the em-dash "—".
    mockRows = shallowRef([
      {
        region: "North East",
        child_poverty_pct: 38,
        children_in_poverty: null,
        national_avg_pct: 29.8,
        above_national_avg: true,
      },
    ])
    const wrapper = mount(ChildPovertyChart)
    const cells = wrapper
      .findAll("tbody tr")[0]
      .findAll("td")
      .map((td) => td.text())
    // Region, Child poverty (%), Children in poverty, National average (%)
    expect(cells[2]).toBe("—")
    expect(cells[2]).not.toBe("0")
  })

  it("renders a missing national average as —, and omits it from the aria-label (not 'NaN%'/'0%')", () => {
    // national_avg_pct via bare Number() would make a null read as a fabricated
    // 0% in both the aria-label and the table column. toNumberOrNaN maps it to
    // NaN so the table shows "—" and the aria-label drops the sentence entirely.
    mockRows = shallowRef([
      {
        region: "North East",
        child_poverty_pct: 38,
        children_in_poverty: 185000,
        national_avg_pct: null,
        above_national_avg: true,
      },
    ])
    const wrapper = mount(ChildPovertyChart)
    const cells = wrapper
      .findAll("tbody tr")[0]
      .findAll("td")
      .map((td) => td.text())
    expect(cells[3]).toBe("—") // National average (%) column
    const label = wrapper.find("[role='img']").attributes("aria-label") ?? ""
    expect(label).not.toContain("NaN")
    expect(label).not.toContain("national average is 0%")
    expect(label).not.toContain("The national average is") // sentence omitted
  })

  it("drops a region whose child-poverty rate is missing instead of plotting a fabricated 0%", () => {
    mockRows = shallowRef([
      {
        region: "North East",
        child_poverty_pct: 38,
        children_in_poverty: 185000,
        national_avg_pct: 29.8,
        above_national_avg: true,
      },
      {
        region: "Nowhere",
        child_poverty_pct: null,
        children_in_poverty: 1000,
        national_avg_pct: 29.8,
        above_national_avg: false,
      },
    ])
    const wrapper = mount(ChildPovertyChart)
    const bodyRows = wrapper.findAll("tbody tr")
    expect(bodyRows).toHaveLength(1)
    expect(bodyRows[0].findAll("td")[0].text()).toBe("North East")
    expect(wrapper.text()).not.toContain("Nowhere")
  })
})

describe("child-poverty article provenance", () => {
  it("uses the generated measure and citation without retaining legacy headline claims", () => {
    const article = chartConfigs["child-poverty"]
    expect(article.source.url).toContain("households-below-average-income")
    expect(article.source.accessed).toBe("2026-10-22")
    expect(article.source.name).toContain("4.16ts and 4.17ts")
    expect(article.methodology).toContain("2021/22 to 2023/24, three-year average")
    expect(article.stats).toEqual([])
    expect(article.lede).not.toContain("38%")
    expect(article.lede).not.toContain("3.3 million")
  })
})
