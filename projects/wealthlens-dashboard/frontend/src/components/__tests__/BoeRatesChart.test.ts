import { describe, it, expect, vi, beforeEach } from "vitest"
import { mount } from "@vue/test-utils"
import { createPinia, setActivePinia } from "pinia"
import { ref, shallowRef } from "vue"

/**
 * BoeRatesChart tests — focused on the ADDITION in the a11y slice: the
 * accessible data-table fallback (WCAG 1.1.1). The shared loading/error/no-data
 * behaviour is covered uniformly in ChartComponents.test.ts. Here we test that:
 *   - the data table renders the chart's exact column headers,
 *   - the table mirrors the chart's verbatim per-row figures with correct
 *     per-CELL mapping (Date, Bank rate, CPI) — not just value presence,
 *   - the table drops the SAME rows the chart's filter drops (a row missing
 *     bank_rate or cpi_annual must not appear in the table either),
 *   - a malformed numeric value never reaches the table as a fabricated number.
 *
 * The component reads data through useChartData(), so we mock that composable
 * (mirroring the other chart tests) to drive rows/loading/error directly.
 */

// Declared once as const refs whose .value is reset in beforeEach, so the
// reference identity stays stable across tests (no stale-ref risk if any code
// caches the object returned by useChartData).
const mockRows = shallowRef<Record<string, unknown>[]>([])
const mockLoading = ref(false)
const mockError = ref<string | null>(null)

vi.mock("@/composables/useChartData", () => ({
  useChartData: () => ({
    rows: mockRows,
    loading: mockLoading,
    error: mockError,
  }),
}))

// Stub vue-echarts so we exercise table behaviour without ECharts internals.
vi.mock("vue-echarts", () => ({
  default: {
    name: "VChart",
    template: '<div class="vchart-stub" />',
    props: ["option", "autoresize"],
  },
}))

vi.mock("echarts/core", () => ({ use: vi.fn() }))
vi.mock("echarts/renderers", () => ({ CanvasRenderer: {} }))
vi.mock("echarts/charts", () => ({ LineChart: {} }))
vi.mock("echarts/components", () => ({
  GridComponent: {},
  TooltipComponent: {},
  TitleComponent: {},
  LegendComponent: {},
}))

import BoeRatesChart from "@/components/BoeRatesChart.vue"

/**
 * Mirror the component's own date-label derivation so the expected labels stay
 * timezone-independent: it parses the ISO date and formats YYYY-MM from the
 * resulting Date using UTC accessors (falling back to the raw string for an
 * unparseable date). UTC matches the component so the test passes in any tz.
 */
function expectedDateLabel(iso: string): string {
  const d = new Date(iso)
  if (isNaN(d.getTime())) return iso
  return `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, "0")}`
}

/** en-GB locale formatting, computed (never hardcoded) — matches AccessibleDataTable. */
const gb = (n: number): string => Number(n).toLocaleString("en-GB")

/** A few representative rows from the BoE/CPI series (chronological). */
const BOE_ROWS = [
  { date: "2008-01-01", bank_rate: 5.5, cpi_annual: 3.6 },
  { date: "2009-01-01", bank_rate: 1.5, cpi_annual: 2.2 },
  { date: "2022-10-01", bank_rate: 2.25, cpi_annual: 11.1 },
]

describe("BoeRatesChart accessible data table", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    setActivePinia(createPinia())
    mockRows.value = BOE_ROWS
    mockLoading.value = false
    mockError.value = null

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
    const wrapper = mount(BoeRatesChart)
    expect(wrapper.text()).toContain("View data as table")
    const headers = wrapper.findAll("thead th").map((th) => th.text())
    expect(headers).toEqual(["Date", "Bank rate (%)", "CPI annual (%)"])
  })

  it("populates the table with VERBATIM per-row figures (correct cell mapping)", () => {
    const wrapper = mount(BoeRatesChart)
    const bodyRows = wrapper.findAll("tbody tr")
    expect(bodyRows).toHaveLength(3)

    const cells = (i: number) => bodyRows[i].findAll("td").map((td) => td.text())
    // Per-CELL mapping so a column swap/reorder fails here. Numeric expectations
    // are computed via toLocaleString (no hardcoded locale strings).
    expect(cells(0)).toEqual([expectedDateLabel("2008-01-01"), gb(5.5), gb(3.6)])
    expect(cells(1)).toEqual([expectedDateLabel("2009-01-01"), gb(1.5), gb(2.2)])
    expect(cells(2)).toEqual([expectedDateLabel("2022-10-01"), gb(2.25), gb(11.1)])
  })

  it("sorts rows chronologically, mirroring the chart's own sort", () => {
    // Feed rows out of order; the chart sorts by date, so the table must too.
    mockRows.value = [
      { date: "2022-10-01", bank_rate: 2.25, cpi_annual: 11.1 },
      { date: "2008-01-01", bank_rate: 5.5, cpi_annual: 3.6 },
      { date: "2009-01-01", bank_rate: 1.5, cpi_annual: 2.2 },
    ]
    const wrapper = mount(BoeRatesChart)
    const firstCol = wrapper.findAll("tbody tr").map((tr) => tr.findAll("td")[0].text())
    expect(firstCol).toEqual([
      expectedDateLabel("2008-01-01"),
      expectedDateLabel("2009-01-01"),
      expectedDateLabel("2022-10-01"),
    ])
  })

  it("drops the SAME rows the chart drops (non-numeric bank_rate or cpi_annual)", () => {
    // The chart's filter keeps only rows where the mapped bank_rate AND
    // cpi_annual are both finite (mapping does toNumberOrNaN(...) then
    // !isNaN(...)). A row whose rate or CPI is omitted/non-numeric → NaN and is
    // excluded from the plot, so it must be excluded from the table too — never
    // silently shown with a fabricated value.
    mockRows.value = [
      { date: "2008-01-01", bank_rate: 5.5, cpi_annual: 3.6 },
      { date: "2009-01-01", cpi_annual: 2.2 }, // bank_rate undefined → NaN → dropped
      { date: "2010-01-01", bank_rate: 0.5, cpi_annual: "n/a" }, // NaN → dropped
    ]
    const wrapper = mount(BoeRatesChart)
    const bodyRows = wrapper.findAll("tbody tr")
    expect(bodyRows).toHaveLength(1)
    expect(bodyRows[0].findAll("td").map((td) => td.text())).toEqual([
      expectedDateLabel("2008-01-01"),
      gb(5.5),
      gb(3.6),
    ])
    // The dropped dates must not leak into the table anywhere.
    expect(wrapper.text()).not.toContain(expectedDateLabel("2009-01-01"))
    expect(wrapper.text()).not.toContain(expectedDateLabel("2010-01-01"))
    expect(wrapper.text()).not.toContain("NaN")
  })

  it("DROPS rows with null/empty rate or CPI (no fabricated 0 from Number)", () => {
    // Regression guard for the null→0 fabrication: Number(null) and Number("")
    // both === 0, so without the toNumberOrNaN guard a blank source cell would be
    // coerced to a fabricated 0 and KEPT (plotted AND tabled). The fix maps
    // null/empty to NaN so the existing !isNaN filter drops the whole row from
    // BOTH the chart and the table — consistently, never as a real-looking 0.
    mockRows.value = [
      { date: "2008-01-01", bank_rate: 5.5, cpi_annual: 3.6 },
      { date: "2009-01-01", bank_rate: null, cpi_annual: 2.2 }, // null → NaN → dropped
      { date: "2010-01-01", bank_rate: 1.0, cpi_annual: "" }, // empty → NaN → dropped
    ]
    const wrapper = mount(BoeRatesChart)
    const bodyRows = wrapper.findAll("tbody tr")
    // Only the fully-populated 2008 row survives.
    expect(bodyRows).toHaveLength(1)
    expect(bodyRows[0].findAll("td").map((td) => td.text())).toEqual([
      expectedDateLabel("2008-01-01"),
      gb(5.5),
      gb(3.6),
    ])
    // The dropped rows must not appear, and crucially must NOT render a "0".
    expect(wrapper.text()).not.toContain(expectedDateLabel("2009-01-01"))
    expect(wrapper.text()).not.toContain(expectedDateLabel("2010-01-01"))
    expect(wrapper.text()).not.toContain("NaN")
    // gb(0) is the locale string a fabricated 0 would have produced ("0").
    expect(bodyRows[0].findAll("td").map((td) => td.text())).not.toContain(gb(0))
  })

  it("KEEPS a genuine 0 value and renders it as '0' (not dropped, not blank)", () => {
    // A real 0 (e.g. a 0% CPI reading) is valid data: it must survive the filter
    // and render as the locale string "0" — the null/empty guard must not strip
    // legitimate zeros.
    mockRows.value = [
      { date: "2015-01-01", bank_rate: 0.5, cpi_annual: 0 }, // genuine 0% CPI
      { date: "2016-01-01", bank_rate: 0, cpi_annual: 0.6 }, // genuine 0% rate
    ]
    const wrapper = mount(BoeRatesChart)
    const bodyRows = wrapper.findAll("tbody tr")
    expect(bodyRows).toHaveLength(2)
    expect(bodyRows[0].findAll("td").map((td) => td.text())).toEqual([
      expectedDateLabel("2015-01-01"),
      gb(0.5),
      gb(0), // genuine 0 renders as "0"
    ])
    expect(bodyRows[1].findAll("td").map((td) => td.text())).toEqual([
      expectedDateLabel("2016-01-01"),
      gb(0), // genuine 0 renders as "0"
      gb(0.6),
    ])
    // A real 0 must never be rendered as the missing-value placeholder.
    expect(wrapper.text()).not.toContain("—")
  })
})
