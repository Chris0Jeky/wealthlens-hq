import { describe, it, expect, vi, beforeEach } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { ref, shallowRef } from "vue";

/**
 * HousingAffordabilityChart tests — focused on the ADDITION in the a11y slice:
 * the accessible data-table fallback (WCAG 1.1.1). The shared loading/error/
 * no-data behaviour is covered uniformly in ChartComponents.test.ts. Here we
 * assert that the data table:
 *   - exposes the chart's exact column headers,
 *   - emits one row per plotted (region, year) data point,
 *   - mirrors the chart's VERBATIM figures with correct per-cell mapping, in the
 *     chart's region order and within-region year-sorted order,
 *   - drops the SAME regions the chart drops when it truncates to the top
 *     MAX_REGIONS least-affordable regions (faithful filtering).
 *
 * The component reads data through useChartData(), so we mock that composable
 * (mirroring the other chart tests) to drive rows/loading/error directly.
 */

let mockRows: ReturnType<typeof shallowRef<Record<string, unknown>[]>>;
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
vi.mock("echarts/charts", () => ({ LineChart: {} }));
vi.mock("echarts/components", () => ({
  GridComponent: {},
  TooltipComponent: {},
  TitleComponent: {},
  LegendComponent: {},
}));

import HousingAffordabilityChart from "@/components/HousingAffordabilityChart.vue";

/** en-GB formatting that matches AccessibleDataTable's numeric cells. */
const gb = (n: number): string => Number(n).toLocaleString("en-GB");

/**
 * Two regions, deliberately year-UNSORTED in source order, so the test proves
 * the table reflects the chart's year-sort (not the raw input order). Region
 * insertion order is London, then North East — the chart keeps that order when
 * there are <= MAX_REGIONS (8) regions, so the table must too.
 */
const HOUSING_ROWS = [
  { region: "London", year: 2008, ratio: 7.2 },
  { region: "London", year: 2002, ratio: 5.1 },
  { region: "North East", year: 2008, ratio: 4.9 },
  { region: "London", year: 2021, ratio: 13.345 },
  { region: "North East", year: 2002, ratio: 3.7 },
];

describe("HousingAffordabilityChart accessible data table", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setActivePinia(createPinia());
    mockRows = shallowRef<Record<string, unknown>[]>(HOUSING_ROWS);
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
    const wrapper = mount(HousingAffordabilityChart);
    expect(wrapper.text()).toContain("View data as table");
    const headers = wrapper.findAll("thead th").map((th) => th.text());
    expect(headers).toEqual(["Region", "Year", "Price-to-earnings ratio"]);
  });

  it("emits one row per plotted (region, year) data point", () => {
    const wrapper = mount(HousingAffordabilityChart);
    // 5 source rows, all valid → 5 plotted points → 5 table rows.
    expect(wrapper.findAll("tbody tr")).toHaveLength(5);
  });

  it("mirrors VERBATIM figures in the chart's region + year-sorted order", () => {
    const wrapper = mount(HousingAffordabilityChart);
    const bodyRows = wrapper.findAll("tbody tr");
    const cells = (i: number) => bodyRows[i].findAll("td").map((td) => td.text());

    // Region order = insertion order (London first, then North East) because
    // there are only 2 regions (<= MAX_REGIONS). Within each region, entries are
    // YEAR-sorted ascending — proving the table follows the chart's sort, not the
    // unsorted source order. Year is NOT locale-formatted (calendar year), ratio
    // IS (en-GB, computed not hardcoded).
    expect(cells(0)).toEqual(["London", "2002", gb(5.1)]);
    expect(cells(1)).toEqual(["London", "2008", gb(7.2)]);
    expect(cells(2)).toEqual(["London", "2021", gb(13.345)]);
    expect(cells(3)).toEqual(["North East", "2002", gb(3.7)]);
    expect(cells(4)).toEqual(["North East", "2008", gb(4.9)]);
  });

  it("drops the SAME regions the chart drops when truncating to the top 8", () => {
    // 9 regions, one point each, with distinct latest ratios. The chart keeps the
    // top 8 by latest ratio (descending) and drops the least-affordable one
    // ("R-lowest", ratio 1.0). The table must mirror that exact filter + order.
    const regions = [
      { region: "R-lowest", ratio: 1.0 },
      { region: "R-09", ratio: 9.0 },
      { region: "R-02", ratio: 2.0 },
      { region: "R-08", ratio: 8.0 },
      { region: "R-03", ratio: 3.0 },
      { region: "R-07", ratio: 7.0 },
      { region: "R-04", ratio: 4.0 },
      { region: "R-06", ratio: 6.0 },
      { region: "R-05", ratio: 5.0 },
    ];
    mockRows.value = regions.map((r) => ({
      region: r.region,
      year: 2020,
      ratio: r.ratio,
    }));

    const wrapper = mount(HousingAffordabilityChart);
    const bodyRows = wrapper.findAll("tbody tr");
    // 9 regions > MAX_REGIONS (8) → exactly 8 rows survive (one point each).
    expect(bodyRows).toHaveLength(8);

    const tableRegions = bodyRows.map((r) => r.findAll("td")[0].text());
    // Order = ranked by latest ratio descending (chart's truncation order).
    expect(tableRegions).toEqual([
      "R-09",
      "R-08",
      "R-07",
      "R-06",
      "R-05",
      "R-04",
      "R-03",
      "R-02",
    ]);
    // The least-affordable region was dropped from BOTH chart and table.
    expect(tableRegions).not.toContain("R-lowest");
    // Truncation note in the caption stays consistent with the chart.
    expect(wrapper.find("table caption").text()).toContain(
      "Showing the top 8 least-affordable regions",
    );
  });

  it("cites the registered ONS source in the table caption", () => {
    const wrapper = mount(HousingAffordabilityChart);
    const caption = wrapper.find("table caption").text();
    expect(caption).toContain(
      "House price to workplace-based earnings ratio by UK region and year",
    );
    expect(caption).toContain("Source: ONS Housing Affordability.");
    // No truncation note when regions <= MAX_REGIONS.
    expect(caption).not.toContain("Showing the top");
  });
});
