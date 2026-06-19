import { describe, it, expect, vi, beforeEach } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { ref, shallowRef } from "vue";

/**
 * WealthByDecileChart tests — focused on the ADDITION in the a11y slice: the
 * accessible data-table fallback (WCAG 1.1.1). The shared loading/error/no-data
 * behaviour is covered uniformly in ChartComponents.test.ts. Here we test that:
 *   - the table renders the chart's exact column headers,
 *   - the tbody has one row per (filtered) decile, in poorest-to-richest order,
 *   - per-row CELL MAPPING matches the chart's verbatim figures (not just value
 *     presence), so a column swap/reorder would fail the assertion.
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
}));

import WealthByDecileChart from "@/components/WealthByDecileChart.vue";

/**
 * Ten deciles with UNIQUE total_wealth_bn values (poorest negative, richest
 * largest), so a column swap or row reorder cannot accidentally pass. Values
 * 1,058.5 / 1,742.1 / 4,983.6 also exercise en-GB thousands grouping.
 */
const DECILE_ROWS = [
  { decile: "1st (poorest)", total_wealth_bn: -3.7 },
  { decile: "2nd", total_wealth_bn: 12.4 },
  { decile: "3rd", total_wealth_bn: 58.9 },
  { decile: "4th", total_wealth_bn: 121.6 },
  { decile: "5th", total_wealth_bn: 245.3 },
  { decile: "6th", total_wealth_bn: 410.8 },
  { decile: "7th", total_wealth_bn: 689.2 },
  { decile: "8th", total_wealth_bn: 1058.5 },
  { decile: "9th", total_wealth_bn: 1742.1 },
  { decile: "10th (richest)", total_wealth_bn: 4983.6 },
];

/** Expected numeric cell text, derived (not hardcoded) via the same locale path. */
const fmt = (v: number): string => Number(v).toLocaleString("en-GB");

describe("WealthByDecileChart accessible data table", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setActivePinia(createPinia());
    mockRows = shallowRef(DECILE_ROWS);
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
    const wrapper = mount(WealthByDecileChart);
    expect(wrapper.text()).toContain("View data as table");
    const headers = wrapper.findAll("thead th").map((th) => th.text());
    expect(headers).toEqual(["Decile", "Total wealth (£bn)"]);
  });

  it("renders one tbody row per filtered decile, poorest-to-richest", () => {
    const wrapper = mount(WealthByDecileChart);
    const bodyRows = wrapper.findAll("tbody tr");
    expect(bodyRows).toHaveLength(DECILE_ROWS.length);
    // First and last rows preserve the chart's poorest→richest ordering.
    expect(bodyRows[0].findAll("td")[0].text()).toBe("1st (poorest)");
    expect(bodyRows[bodyRows.length - 1].findAll("td")[0].text()).toBe(
      "10th (richest)",
    );
  });

  it("populates the table with VERBATIM per-row figures (correct cell mapping)", () => {
    const wrapper = mount(WealthByDecileChart);
    const bodyRows = wrapper.findAll("tbody tr");
    const cells = (i: number) =>
      bodyRows[i].findAll("td").map((td) => td.text());

    // Per-CELL assertions so a column swap or reorder fails here. Values are
    // formatted through Number(x).toLocaleString("en-GB") to stay locale-robust.
    expect(cells(0)).toEqual(["1st (poorest)", fmt(-3.7)]);
    expect(cells(7)).toEqual(["8th", fmt(1058.5)]); // grouped: "1,058.5"
    expect(cells(9)).toEqual(["10th (richest)", fmt(4983.6)]); // grouped: "4,983.6"
  });

  it("cites the ONS source in the table caption", () => {
    const wrapper = mount(WealthByDecileChart);
    const caption = wrapper.find("table caption").text();
    expect(caption).toContain("Total household wealth by decile");
    expect(caption).toContain("ONS Wealth and Assets Survey");
  });

  it("drops rows with a non-numeric value and never shows the literal 'NaN'", () => {
    // A malformed wealth value must be filtered out by parsedData (mirroring the
    // chart), so it never reaches the table; the valid rows still render.
    mockRows.value = [
      { decile: "1st (poorest)", total_wealth_bn: -3.7 },
      { decile: "2nd", total_wealth_bn: "not-a-number" },
      { decile: "3rd", total_wealth_bn: 58.9 },
    ];
    const wrapper = mount(WealthByDecileChart);
    const bodyRows = wrapper.findAll("tbody tr");
    expect(bodyRows).toHaveLength(2);
    expect(bodyRows[0].findAll("td").map((td) => td.text())).toEqual([
      "1st (poorest)",
      fmt(-3.7),
    ]);
    expect(bodyRows[1].findAll("td").map((td) => td.text())).toEqual([
      "3rd",
      fmt(58.9),
    ]);
    expect(wrapper.text()).not.toContain("NaN");
  });
});
