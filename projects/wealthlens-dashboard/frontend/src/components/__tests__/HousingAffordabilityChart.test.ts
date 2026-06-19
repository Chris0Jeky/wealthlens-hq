import { describe, it, expect, vi, beforeEach } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { ref, shallowRef, type Ref, type ShallowRef } from "vue";

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

let mockRows: ShallowRef<Record<string, unknown>[]>;
let mockLoading: Ref<boolean>;
let mockError: Ref<string | null>;

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
const gb = (n: number): string => n.toLocaleString("en-GB");

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
    mockError = ref<string | null>(null);

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

  it("drops rows with a null/empty ratio or year instead of fabricating 0", () => {
    // Number(null) and Number("") are both 0, so a naive Number() coercion would
    // silently invent a "year 0" / a 0 ratio. These rows must be DROPPED from
    // BOTH chart and table — never rendered as "0". A genuine numeric 0 stays.
    mockRows.value = [
      { region: "London", year: 2010, ratio: 6.5 }, // valid → kept
      { region: "London", year: 2011, ratio: null }, // null ratio → dropped
      { region: "London", year: 2012, ratio: "" }, // empty ratio → dropped
      { region: "London", year: null, ratio: 7.0 }, // null year → dropped
      { region: "London", year: "", ratio: 7.5 }, // empty year → dropped
      { region: "London", year: 2013, ratio: 0 }, // genuine 0 → kept as "0"
    ];

    const wrapper = mount(HousingAffordabilityChart);
    const bodyRows = wrapper.findAll("tbody tr");
    // Only the two real points survive (2010 / 6.5 and 2013 / 0).
    expect(bodyRows).toHaveLength(2);

    const cells = (i: number) =>
      bodyRows[i].findAll("td").map((td) => td.text());
    expect(cells(0)).toEqual(["London", "2010", gb(6.5)]);
    // The genuine 0 ratio renders as "0" (not dropped, not "—").
    expect(cells(1)).toEqual(["London", "2013", gb(0)]);

    // No fabricated "year 0" leaked into the table from the null/empty rows.
    const allYears = bodyRows.map((r) => r.findAll("td")[1].text());
    expect(allYears).not.toContain("0");
  });

  it("coalesces duplicate (region, year) rows to a single last-wins point", () => {
    // If the API returns two rows for the same region/year, the line series keeps
    // only the last ratio (its per-year dataMap). The table must coalesce the
    // same way so non-visual users do not see extra/stale points.
    mockRows.value = [
      { region: "London", year: 2020, ratio: 8.0 }, // superseded
      { region: "London", year: 2020, ratio: 8.4 }, // last wins
      { region: "London", year: 2021, ratio: 9.1 },
    ];

    const wrapper = mount(HousingAffordabilityChart);
    const bodyRows = wrapper.findAll("tbody tr");
    // Two duplicate 2020 rows collapse to one → 2 table rows total.
    expect(bodyRows).toHaveLength(2);

    const cells = (i: number) =>
      bodyRows[i].findAll("td").map((td) => td.text());
    expect(cells(0)).toEqual(["London", "2020", gb(8.4)]);
    expect(cells(1)).toEqual(["London", "2021", gb(9.1)]);
  });

  it("cites the registered ONS source in the table caption", () => {
    const wrapper = mount(HousingAffordabilityChart);
    const caption = wrapper.find("table caption").text();
    expect(caption).toContain(
      "House price to workplace-based earnings ratio by region (England and Wales) and year",
    );
    // Geography is England and Wales only; the caption must not overstate "UK".
    expect(caption).not.toContain("UK region");
    expect(caption).toContain("Source: ONS Housing Affordability.");
    // No truncation note when regions <= MAX_REGIONS.
    expect(caption).not.toContain("Showing the top");
  });
});
