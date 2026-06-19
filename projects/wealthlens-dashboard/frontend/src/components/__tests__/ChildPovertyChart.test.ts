import { describe, it, expect, vi, beforeEach } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { ref, shallowRef } from "vue";

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

// Stub vue-echarts so we exercise the table behaviour without ECharts internals.
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
  MarkLineComponent: {},
}));

import ChildPovertyChart from "@/components/ChildPovertyChart.vue";

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
];

describe("ChildPovertyChart accessible data table", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setActivePinia(createPinia());
    mockRows = shallowRef(CHILD_POVERTY_ROWS);
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
    const wrapper = mount(ChildPovertyChart);
    expect(wrapper.text()).toContain("View data as table");
    const headers = wrapper.findAll("thead th").map((th) => th.text());
    expect(headers).toEqual([
      "Region",
      "Child poverty (%)",
      "Children in poverty",
      "National average (%)",
    ]);
  });

  it("has one tbody row per plotted region", () => {
    const wrapper = mount(ChildPovertyChart);
    expect(wrapper.findAll("tbody tr")).toHaveLength(2);
  });

  it("maps the chart's VERBATIM, poverty-rate-descending figures per cell", () => {
    const wrapper = mount(ChildPovertyChart);
    const bodyRows = wrapper.findAll("tbody tr");
    const cells = (i: number) =>
      bodyRows[i].findAll("td").map((td) => td.text());

    // en-GB locale-formatting is computed (not hardcoded) so the expectation stays
    // correct regardless of grouping rules: e.g. 185000 -> "185,000".
    const fmt = (n: number) => Number(n).toLocaleString("en-GB");

    // Row 0 = highest poverty rate (North East), proving the table follows the
    // chart's descending sort, NOT the raw input order (South East was first in).
    expect(cells(0)).toEqual([
      "North East",
      fmt(38),
      fmt(185000),
      fmt(29.8),
    ]);
    // Row 1 = lower poverty rate (South East).
    expect(cells(1)).toEqual([
      "South East",
      fmt(22),
      fmt(310000),
      fmt(29.8),
    ]);
  });

  it("captions the table with the DWP HBAI source and the estimate caveat", () => {
    const wrapper = mount(ChildPovertyChart);
    const caption = wrapper.find("table caption").text();
    expect(caption).toContain("Child poverty rate (%) by UK region");
    expect(caption).toContain("Source: DWP HBAI");
    expect(caption).toContain("estimates");
  });
});
