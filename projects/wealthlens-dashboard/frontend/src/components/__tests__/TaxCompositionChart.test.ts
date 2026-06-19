import { describe, it, expect, vi, beforeEach } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { ref, shallowRef } from "vue";

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

let mockRows: ReturnType<typeof shallowRef>;
let mockLoading: ReturnType<typeof ref>;
let mockError: ReturnType<typeof ref>;

vi.mock("@/composables/useChartData", () => ({
  useChartData: () => ({
    rows: mockRows,
    loading: mockLoading,
    error: mockError,
  }),
}));

// Stub vue-echarts so we exercise table/caveat behaviour without ECharts internals.
vi.mock("vue-echarts", () => ({
  default: {
    name: "VChart",
    template: '<div class="vchart-stub" />',
    props: ["option", "autoresize"],
  },
}));

vi.mock("echarts/core", () => ({ use: vi.fn() }));
vi.mock("echarts/renderers", () => ({ CanvasRenderer: {} }));
vi.mock("echarts/charts", () => ({ BarChart: {} }));
vi.mock("echarts/components", () => ({
  GridComponent: {},
  TooltipComponent: {},
  TitleComponent: {},
  LegendComponent: {},
}));

import TaxCompositionChart from "@/components/TaxCompositionChart.vue";

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
];

describe("TaxCompositionChart accessible table + illustrative caveat", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setActivePinia(createPinia());
    mockRows = shallowRef(TAX_ROWS);
    mockLoading = ref(false);
    mockError = ref(null);

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
    });
  });

  it("renders an accessible data table with the chart's column headers", () => {
    const wrapper = mount(TaxCompositionChart);
    expect(wrapper.text()).toContain("View data as table");
    const headers = wrapper.findAll("thead th").map((th) => th.text());
    expect(headers).toEqual([
      "Tax year",
      "Income Tax (£bn)",
      "NICs (£bn)",
      "CGT (£bn)",
      "IHT (£bn)",
      "SDLT (£bn)",
      "Work taxes (%)",
      "Wealth taxes (%)",
    ]);
  });

  it("populates the table with VERBATIM per-row figures (correct cell mapping)", () => {
    const wrapper = mount(TaxCompositionChart);
    const bodyRows = wrapper.findAll("tbody tr");
    expect(bodyRows).toHaveLength(2);

    const cells = (i: number) => bodyRows[i].findAll("td").map((td) => td.text());
    // en-GB locale-formatting renders these whole/one-dp numbers without group
    // separators; assert per-CELL mapping so a column swap/reorder fails here.
    expect(cells(0)).toEqual(["2018-19", "191", "137", "9.2", "5.4", "12", "92.5", "7.5"]);
    expect(cells(1)).toEqual(["2023-24", "270", "180", "15", "7.5", "12", "92.9", "7.1"]);
  });

  it("shows the illustrative caveat when rows are marked illustrative", () => {
    const wrapper = mount(TaxCompositionChart);
    expect(wrapper.text()).toContain(
      "Illustrative composite. Approximated from HMRC receipts, not exact published values.",
    );
  });

  it("hides the caveat when the data is NOT illustrative (no crying wolf)", () => {
    mockRows.value = TAX_ROWS.map((r) => ({ ...r, data_source: "hmrc-actual" }));
    const wrapper = mount(TaxCompositionChart);
    // The table still renders (a11y is unconditional)...
    expect(wrapper.text()).toContain("View data as table");
    // ...but the illustrative caveat must NOT appear for genuine data.
    expect(wrapper.text()).not.toContain("Illustrative composite. Approximated");
  });

  it("keeps the table caption honest about the illustrative provenance", () => {
    const wrapper = mount(TaxCompositionChart);
    const caption = wrapper.find("table caption").text();
    expect(caption).toContain("Illustrative composite figures approximated from HMRC receipts");
  });
});
