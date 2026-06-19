import { describe, it, expect, vi, beforeEach } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { ref, shallowRef } from "vue";

/**
 * GenerationalWealthChart tests — focused on the ADDITION in the a11y slice:
 * the accessible data-table fallback (WCAG 1.1.1). The shared
 * loading/error/no-data/happy-path behaviour is covered in
 * ChartComponents.test.ts. Here we test that:
 *   - the data table renders the chart's exact column headers,
 *   - the tbody has one row per plotted bar (generation x age milestone),
 *   - per-row CELL MAPPING is verbatim (not just value presence), so a column
 *     swap or reorder fails the assertion,
 *   - the "Projected?" column distinguishes projected estimates from measured
 *     figures (data honesty — an estimate must never read as a measurement).
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

// Stub vue-echarts so we exercise table behaviour without ECharts internals.
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

import GenerationalWealthChart from "@/components/GenerationalWealthChart.vue";

/**
 * Verbatim rows from the curated dataset (automation/data-pipelines/
 * fetch_generational_wealth.py). A mix of measured rows and a projected one so
 * we can assert the "Projected?" cell. Every value below is unique per cell so a
 * column swap/reorder would break the per-cell mapping assertions.
 */
const GEN_ROWS = [
  // Baby Boomers — measured, age 30
  {
    generation: "Baby Boomers",
    birth_years: "1946-1964",
    age_milestone: 30,
    median_wealth_gbp: 68000,
    year_measured: 1994,
    projected: false,
  },
  // Baby Boomers — measured, age 60 (distinct wealth/year)
  {
    generation: "Baby Boomers",
    birth_years: "1946-1964",
    age_milestone: 60,
    median_wealth_gbp: 395000,
    year_measured: 2024,
    projected: false,
  },
  // Millennials — PROJECTED, age 40 (must show "Yes" in Projected?)
  {
    generation: "Millennials",
    birth_years: "1981-1996",
    age_milestone: 40,
    median_wealth_gbp: 82000,
    year_measured: 2026,
    projected: true,
  },
];

describe("GenerationalWealthChart accessible data table", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setActivePinia(createPinia());
    mockRows = shallowRef(GEN_ROWS);
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
    const wrapper = mount(GenerationalWealthChart);
    expect(wrapper.text()).toContain("View data as table");
    const headers = wrapper.findAll("thead th").map((th) => th.text());
    expect(headers).toEqual([
      "Generation",
      "Birth years",
      "Age",
      "Median wealth (£)",
      "Year measured",
      "Projected?",
    ]);
  });

  it("has one tbody row per plotted bar (generation x age milestone)", () => {
    const wrapper = mount(GenerationalWealthChart);
    const bodyRows = wrapper.findAll("tbody tr");
    expect(bodyRows).toHaveLength(GEN_ROWS.length);
  });

  it("populates the table with VERBATIM per-row figures (correct cell mapping)", () => {
    const wrapper = mount(GenerationalWealthChart);
    const bodyRows = wrapper.findAll("tbody tr");
    const cells = (i: number) => bodyRows[i].findAll("td").map((td) => td.text());

    // Compute the wealth cell text the SAME way AccessibleDataTable does (en-GB
    // locale formatting) so the assertion is robust without running the suite.
    // Columns: Generation, Birth years, Age, Median wealth (£), Year measured, Projected?
    expect(cells(0)).toEqual([
      "Baby Boomers",
      "1946-1964",
      "30",
      Number(68000).toLocaleString("en-GB"),
      "1994",
      "No",
    ]);
    expect(cells(1)).toEqual([
      "Baby Boomers",
      "1946-1964",
      "60",
      Number(395000).toLocaleString("en-GB"),
      "2024",
      "No",
    ]);
    expect(cells(2)).toEqual([
      "Millennials",
      "1981-1996",
      "40",
      Number(82000).toLocaleString("en-GB"),
      "2026",
      "Yes",
    ]);
  });

  it("flags projected estimates in the Projected? column (data honesty)", () => {
    const wrapper = mount(GenerationalWealthChart);
    const bodyRows = wrapper.findAll("tbody tr");
    // Last column is "Projected?"; measured rows read "No", projected reads "Yes".
    const projectedCells = bodyRows.map(
      (r) => r.findAll("td")[5].text(),
    );
    expect(projectedCells).toEqual(["No", "No", "Yes"]);
  });

  it("renders a year without thousands separators (calendar year, not a count)", () => {
    const wrapper = mount(GenerationalWealthChart);
    const firstRowCells = wrapper
      .findAll("tbody tr")[0]
      .findAll("td")
      .map((td) => td.text());
    // Year measured is column index 4; must be "1994", never "1,994".
    expect(firstRowCells[4]).toBe("1994");
  });

  it("keeps the table caption honest about the source and projected caveat", () => {
    const wrapper = mount(GenerationalWealthChart);
    const caption = wrapper.find("table caption").text();
    expect(caption).toContain("Median total household wealth by generation");
    expect(caption).toContain("Projected estimates are flagged");
    expect(caption).toContain(
      "Resolution Foundation / ONS Wealth and Assets Survey",
    );
  });
});
