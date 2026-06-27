import { describe, it, expect, vi, beforeEach } from "vitest"
import { mount } from "@vue/test-utils"
import { createPinia, setActivePinia } from "pinia"
import { ref, shallowRef } from "vue"

/**
 * TaxCompositionChart tests — focused on the ADDITIONS in the a11y/data-honesty
 * slice: the accessible data-table fallback (WCAG 1.1.1) and the illustrative-
 * data caveat. The shared loading/error/no-data behaviour is covered uniformly
 * in ChartComponents.test.ts. Here we test that:
 *   - the data table mirrors the chart's verbatim per-year figures with correct
 *     per-row cell mapping (not just value presence),
 *   - the illustrative caveat shows when rows are marked illustrative,
 *   - the caveat stays hidden when the data is NOT illustrative (positive signal
 *     only — it must not cry wolf on genuine data).
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

// Stub vue-echarts so we exercise table/caveat behaviour without ECharts internals.
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
}))

import TaxCompositionChart from "@/components/TaxCompositionChart.vue"

/** Two illustrative rows (the real dataset is an illustrative composite). */
const TAX_ROWS = [
  {
    year: "2018-19",
    income_tax_bn: 191.0,
    nics_bn: 137.0,
    cgt_bn: 9.2,
    iht_bn: 5.4,
    sdlt_bn: 12.0,
    work_taxes_bn: 328.0,
    wealth_taxes_bn: 26.6,
    total_selected_bn: 354.6,
    work_pct: 92.5,
    wealth_pct: 7.5,
    data_source: "illustrative",
  },
  {
    year: "2023-24",
    income_tax_bn: 270.0,
    nics_bn: 180.0,
    cgt_bn: 15.0,
    iht_bn: 7.5,
    sdlt_bn: 12.0,
    work_taxes_bn: 450.0,
    wealth_taxes_bn: 34.5,
    total_selected_bn: 484.5,
    work_pct: 92.9,
    wealth_pct: 7.1,
    data_source: "illustrative",
  },
]

describe("TaxCompositionChart accessible table + illustrative caveat", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    setActivePinia(createPinia())
    mockRows = shallowRef(TAX_ROWS)
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
    const wrapper = mount(TaxCompositionChart)
    expect(wrapper.text()).toContain("View data as table")
    const headers = wrapper.findAll("thead th").map((th) => th.text())
    expect(headers).toEqual([
      "Tax year",
      "Income Tax (£bn)",
      "NICs (£bn)",
      "CGT (£bn)",
      "IHT (£bn)",
      "SDLT (£bn)",
      "Work taxes (%)",
      "Wealth taxes (%)",
    ])
  })

  it("populates the table with VERBATIM per-row figures (correct cell mapping)", () => {
    const wrapper = mount(TaxCompositionChart)
    const bodyRows = wrapper.findAll("tbody tr")
    expect(bodyRows).toHaveLength(2)

    const cells = (i: number) => bodyRows[i].findAll("td").map((td) => td.text())
    // en-GB locale-formatting renders these whole/one-dp numbers without group
    // separators; assert per-CELL mapping so a column swap/reorder fails here.
    expect(cells(0)).toEqual(["2018-19", "191", "137", "9.2", "5.4", "12", "92.5", "7.5"])
    expect(cells(1)).toEqual(["2023-24", "270", "180", "15", "7.5", "12", "92.9", "7.1"])
  })

  it("shows the illustrative caveat when rows are marked illustrative", () => {
    const wrapper = mount(TaxCompositionChart)
    expect(wrapper.text()).toContain(
      "Illustrative composite. Approximated from HMRC receipts, not exact published values.",
    )
  })

  it("hides ALL illustrative provenance text when the data is NOT illustrative (no crying wolf)", () => {
    mockRows.value = TAX_ROWS.map((r) => ({ ...r, data_source: "hmrc-actual" }))
    const wrapper = mount(TaxCompositionChart)
    // The table still renders (a11y is unconditional)...
    expect(wrapper.text()).toContain("View data as table")
    // ...but NO illustrative wording may appear anywhere — caveat, caption, or
    // aria-label (case-insensitive, so a wording tweak can't let it false-pass).
    expect(wrapper.text().toLowerCase()).not.toContain("illustrative")
    const caption = wrapper.find("table caption").text()
    expect(caption.toLowerCase()).not.toContain("illustrative")
    const label = wrapper.find("[role='img']").attributes("aria-label") ?? ""
    expect(label.toLowerCase()).not.toContain("illustrative")
  })

  it("keeps the table caption honest about the illustrative provenance (only when illustrative)", () => {
    const wrapper = mount(TaxCompositionChart)
    const caption = wrapper.find("table caption").text()
    // Always describes the table content...
    expect(caption).toContain("UK tax revenue composition by year")
    // ...and adds the provenance hedge because this dataset is illustrative.
    expect(caption).toContain("Illustrative composite figures approximated from HMRC receipts")
  })

  it("notes the illustrative provenance in the chart's aria-label too (and only when illustrative)", () => {
    const wrapper = mount(TaxCompositionChart)
    const label = wrapper.find("[role='img']").attributes("aria-label") ?? ""
    expect(label).toContain("illustrative composite")

    // Genuine data: the aria-label must NOT carry the illustrative hedge.
    mockRows.value = TAX_ROWS.map((r) => ({ ...r, data_source: "hmrc-actual" }))
    const real = mount(TaxCompositionChart)
    const realLabel = real.find("[role='img']").attributes("aria-label") ?? ""
    expect(realLabel).not.toContain("illustrative composite")
  })

  it("renders a malformed/missing numeric value as em-dash, never the literal 'NaN'", () => {
    // A row with a missing work_pct still passes the chart's income-tax filter,
    // so it reaches the table; Number(undefined) === NaN must show as "—".
    mockRows.value = [
      {
        year: "2024-25",
        income_tax_bn: 280.0,
        nics_bn: 185.0,
        cgt_bn: 16.0,
        iht_bn: 8.0,
        sdlt_bn: 13.0,
        wealth_taxes_bn: 37.0,
        total_selected_bn: 502.0,
        wealth_pct: 7.4,
        // work_pct intentionally omitted → Number(undefined) === NaN
        data_source: "illustrative",
      },
    ]
    const wrapper = mount(TaxCompositionChart)
    const cells = wrapper
      .findAll("tbody tr")[0]
      .findAll("td")
      .map((td) => td.text())
    // Columns: year, income, nics, cgt, iht, sdlt, work%, wealth%
    expect(cells[6]).toBe("—") // malformed Work taxes (%)
    expect(cells[7]).toBe("7.4") // valid Wealth taxes (%)
    expect(wrapper.text()).not.toContain("NaN")
  })

  it("DROPS a year missing a plotted component (no £NaN in the stacked total)", () => {
    // Unlike a missing %, a missing PLOTTED component (e.g. nics) would distort the
    // stacked total and render £NaNbn in the tooltip, so the whole year is dropped.
    mockRows.value = [
      {
        year: "2018-19",
        income_tax_bn: 191.0,
        nics_bn: 137.0,
        cgt_bn: 9.2,
        iht_bn: 5.4,
        sdlt_bn: 12.0,
        work_pct: 92.5,
        wealth_pct: 7.5,
        data_source: "illustrative",
      },
      {
        year: "2099-00",
        income_tax_bn: 200.0,
        nics_bn: null,
        cgt_bn: 10.0,
        iht_bn: 6.0,
        sdlt_bn: 12.0,
        work_pct: 92.0,
        wealth_pct: 8.0,
        data_source: "illustrative",
      },
    ]
    const wrapper = mount(TaxCompositionChart)
    const bodyRows = wrapper.findAll("tbody tr")
    expect(bodyRows).toHaveLength(1) // the null-nics 2099 row is dropped
    expect(bodyRows[0].findAll("td")[0].text()).toBe("2018-19")
    expect(wrapper.text()).not.toContain("2099-00")
    expect(wrapper.text()).not.toContain("NaN")
  })
})
