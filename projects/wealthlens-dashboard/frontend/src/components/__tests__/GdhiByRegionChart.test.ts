import { describe, it, expect, vi, beforeEach } from "vitest"
import { mount } from "@vue/test-utils"
import { createPinia, setActivePinia } from "pinia"
import { ref, shallowRef } from "vue"

/**
 * GdhiByRegionChart tests — focused on the ADDITION in the a11y slice: the
 * accessible data-table fallback (WCAG 1.1.1). The shared loading/error/no-data
 * behaviour is covered uniformly in ChartComponents.test.ts. Here we test that:
 *   - the table exposes the chart's exact human-readable column headers,
 *   - the table mirrors the chart's plotted rows verbatim — one row per region,
 *     highest GDHI first, with the "United Kingdom" aggregate excluded exactly as
 *     the chart bars are — with correct per-row CELL mapping (not just presence).
 *
 * The component reads data through useChartData(), so we mock that composable
 * (mirroring the other chart tests) to drive rows/loading/error directly.
 */

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

// Stub vue-echarts so we exercise the table without ECharts internals.
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

import GdhiByRegionChart from "@/components/GdhiByRegionChart.vue"

/**
 * Mock rows deliberately out of GDHI order and including the "United Kingdom"
 * aggregate, so the test proves the table inherits the chart's sort (descending)
 * and UK-exclusion. Every GDHI value is unique so a column swap would fail.
 */
const GDHI_ROWS = [
  { region: "Scotland", gdhi_per_head: 22891, year: 2023 },
  { region: "London", gdhi_per_head: 37564, year: 2023 },
  { region: "United Kingdom", gdhi_per_head: 25502, year: 2023 },
  { region: "North East", gdhi_per_head: 19735, year: 2023 },
  { region: "South East", gdhi_per_head: 28147, year: 2023 },
]

// Expected plotted order after dropping "United Kingdom" and sorting GDHI desc.
const EXPECTED_ORDER = [
  { region: "London", gdhi_per_head: 37564, year: 2023 },
  { region: "South East", gdhi_per_head: 28147, year: 2023 },
  { region: "Scotland", gdhi_per_head: 22891, year: 2023 },
  { region: "North East", gdhi_per_head: 19735, year: 2023 },
]

// Derive expected numeric cell text the same way AccessibleDataTable does, so the
// assertion stays correct regardless of the host machine's default locale.
const gbp = (n: number) => Number(n).toLocaleString("en-GB")

describe("GdhiByRegionChart accessible data table", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    setActivePinia(createPinia())
    mockRows = shallowRef(GDHI_ROWS)
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
    const wrapper = mount(GdhiByRegionChart)
    expect(wrapper.text()).toContain("View data as table")
    const headers = wrapper.findAll("thead th").map((th) => th.text())
    expect(headers).toEqual(["Region", "GDHI per head (£)", "Year"])
  })

  it("excludes the United Kingdom aggregate from the table rows", () => {
    const wrapper = mount(GdhiByRegionChart)
    const bodyRows = wrapper.findAll("tbody tr")
    // 5 source rows minus the "United Kingdom" aggregate = 4 plotted rows.
    expect(bodyRows).toHaveLength(4)
    expect(wrapper.find("tbody").text()).not.toContain("United Kingdom")
  })

  it("mirrors the chart's plotted rows VERBATIM, highest GDHI first (cell mapping)", () => {
    const wrapper = mount(GdhiByRegionChart)
    const bodyRows = wrapper.findAll("tbody tr")
    const cells = (i: number) => bodyRows[i].findAll("td").map((td) => td.text())

    // Per-CELL mapping for the top two rows so a column swap/reorder fails here.
    // London > South East proves descending sort regardless of source order.
    expect(cells(0)).toEqual(["London", gbp(37564), "2023"])
    expect(cells(1)).toEqual(["South East", gbp(28147), "2023"])
  })

  it("orders every row by GDHI descending, matching the chart", () => {
    const wrapper = mount(GdhiByRegionChart)
    const bodyRows = wrapper.findAll("tbody tr")
    bodyRows.forEach((tr, i) => {
      const cells = tr.findAll("td").map((td) => td.text())
      expect(cells).toEqual([
        EXPECTED_ORDER[i].region,
        gbp(EXPECTED_ORDER[i].gdhi_per_head),
        String(EXPECTED_ORDER[i].year),
      ])
    })
  })

  it("cites the ONS Regional GDHI source in the table caption", () => {
    const wrapper = mount(GdhiByRegionChart)
    const caption = wrapper.find("table caption").text()
    expect(caption).toContain("Gross Disposable Household Income per head")
    expect(caption).toContain("ONS Regional GDHI")
  })

  it("announces the UK average when the UK row carries a real value", () => {
    const wrapper = mount(GdhiByRegionChart)
    const label = wrapper.find('[role="img"]').attributes("aria-label") ?? ""
    expect(label).toContain(`UK average is £${gbp(25502)}.`)
  })

  it("omits the UK-average reference when the UK row's value is missing (no fabricated £0)", () => {
    // UK row present but its gdhi_per_head is null: bare Number() would have made
    // a £0 average and announced "UK average is £0." to screen readers.
    mockRows.value = [
      { region: "London", gdhi_per_head: 37564, year: 2023 },
      { region: "Scotland", gdhi_per_head: 22891, year: 2023 },
      { region: "United Kingdom", gdhi_per_head: null, year: 2023 },
    ]
    const wrapper = mount(GdhiByRegionChart)
    const label = wrapper.find('[role="img"]').attributes("aria-label") ?? ""
    expect(label).not.toContain("UK average")
    expect(label).not.toContain("£0")
    expect(label).not.toContain("NaN")
    // The genuine regions are still announced.
    expect(label).toContain("2 UK regions")
  })
})
