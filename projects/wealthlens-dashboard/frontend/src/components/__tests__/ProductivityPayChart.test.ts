import { describe, it, expect, vi, beforeEach } from "vitest";
import { mount, flushPromises } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { ref, shallowRef } from "vue";

/**
 * ProductivityPayChart tests — focused on the ADDITION in the a11y slice: the
 * accessible data-table fallback (WCAG 1.1.1). The shared loading/error/no-data
 * behaviour and the illustrative caveat toggle are already covered in
 * ChartComponents.test.ts. Here we test that:
 *   - the table headers match the chart's columns exactly,
 *   - the table mirrors the chart's verbatim per-year figures with correct
 *     per-row cell mapping (not just value presence),
 *   - the table reproduces the chart's own filter + ascending-year sort,
 *   - a missing gap_pct renders as "—" (never a fabricated "0"),
 *   - the caption carries the illustrative hedge only when the data is
 *     illustrative (consistent with the on-page caveat; no crying wolf).
 *
 * The component reads rows through useChartData() and the illustrative flag
 * through useDataStore().fetchMetadata() in onMounted; we mock both (mirroring
 * the other chart tests) to drive rows + data_type directly.
 */

let mockRows: ReturnType<typeof shallowRef<Record<string, unknown>[]>>;
let mockLoading: ReturnType<typeof ref>;
let mockError: ReturnType<typeof ref>;
let mockDataType: string | null = null;

vi.mock("@/composables/useChartData", () => ({
  useChartData: () => ({
    rows: mockRows,
    loading: mockLoading,
    error: mockError,
  }),
}));

vi.mock("@/stores/data", () => ({
  useDataStore: () => ({
    fetchMetadata: vi.fn().mockResolvedValue({ data_type: mockDataType }),
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

import ProductivityPayChart from "@/components/ProductivityPayChart.vue";

/** en-GB locale-formatting used by AccessibleDataTable for numeric columns. */
const gb = (n: number) => Number(n).toLocaleString("en-GB");

/**
 * Representative rows taken VERBATIM from the real productivity-pay dataset
 * (1997, 2008, 2020 rows of the pipeline output — see
 * automation/data-pipelines/fetch_productivity_pay.py), deliberately supplied
 * OUT of year order so the test proves the table reproduces the chart's
 * ascending-year sort, not input order. Using real rows keeps the fixture from
 * misleading a reader about what the dataset actually contains.
 */
const PRODUCTIVITY_ROWS = [
  { year: 2020, productivity_index: 128.0, pay_index: 114.0, gap_pct: 12.3 },
  { year: 1997, productivity_index: 100.0, pay_index: 100.0, gap_pct: 0.0 },
  { year: 2008, productivity_index: 124.0, pay_index: 116.0, gap_pct: 6.9 },
];

describe("ProductivityPayChart accessible data table", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setActivePinia(createPinia());
    mockRows = shallowRef<Record<string, unknown>[]>([...PRODUCTIVITY_ROWS]);
    mockLoading = ref(false);
    mockError = ref(null);
    mockDataType = "illustrative_fallback";

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
    const wrapper = mount(ProductivityPayChart);
    expect(wrapper.text()).toContain("View data as table");
    const headers = wrapper.findAll("thead th").map((th) => th.text());
    expect(headers).toEqual([
      "Year",
      "Productivity index",
      "Pay index",
      "Gap (%)",
    ]);
  });

  it("populates the table with VERBATIM per-row figures in ascending-year order", () => {
    const wrapper = mount(ProductivityPayChart);
    const bodyRows = wrapper.findAll("tbody tr");
    expect(bodyRows).toHaveLength(3);

    const cells = (i: number) =>
      bodyRows[i].findAll("td").map((td) => td.text());
    // Year is NOT a numeric column → rendered as a plain string (no separators);
    // the index/gap columns are locale-formatted. Per-CELL assertions so a column
    // swap or a lost sort fails here.
    expect(cells(0)).toEqual(["1997", gb(100.0), gb(100.0), gb(0.0)]);
    expect(cells(1)).toEqual(["2008", gb(124.0), gb(116.0), gb(6.9)]);
    expect(cells(2)).toEqual(["2020", gb(128.0), gb(114.0), gb(12.3)]);
  });

  it("renders a missing gap_pct as em-dash, never a fabricated '0'", () => {
    // A row missing gap_pct still passes the chart's productivity/pay filter, so
    // it reaches the table; toNumberOrNaN(undefined) === NaN must show as "—".
    mockRows.value = [
      // gap_pct intentionally omitted
      { year: 2015, productivity_index: 124.0, pay_index: 113.5 },
    ];
    const wrapper = mount(ProductivityPayChart);
    const cells = wrapper
      .findAll("tbody tr")[0]
      .findAll("td")
      .map((td) => td.text());
    // Columns: Year, Productivity index, Pay index, Gap (%)
    expect(cells).toEqual(["2015", gb(124.0), gb(113.5), "—"]);
    expect(wrapper.text()).not.toContain("NaN");
  });

  it("drops a null / empty / whitespace gap_pct as em-dash but keeps a genuine 0", () => {
    // Data honesty: Number(null) / Number("") / Number("   ") all coerce to 0 in
    // JS. toNumberOrNaN must map each blank cell to NaN ("—") so the table never
    // fabricates a 0% gap, while a real numeric 0 must still render as "0".
    mockRows.value = [
      { year: 2010, productivity_index: 123.0, pay_index: 112.0, gap_pct: null },
      { year: 2011, productivity_index: 124.0, pay_index: 110.0, gap_pct: "" },
      { year: 2012, productivity_index: 124.5, pay_index: 109.5, gap_pct: "   " },
      // A genuine zero gap is real data, not missing — it must survive as "0".
      { year: 2013, productivity_index: 125.0, pay_index: 125.0, gap_pct: 0 },
    ];
    const wrapper = mount(ProductivityPayChart);
    const bodyRows = wrapper.findAll("tbody tr");
    const gapCell = (i: number) => bodyRows[i].findAll("td")[3].text();
    expect(gapCell(0)).toBe("—"); // 2010 null
    expect(gapCell(1)).toBe("—"); // 2011 empty string
    expect(gapCell(2)).toBe("—"); // 2012 whitespace-only
    expect(gapCell(3)).toBe(gb(0)); // 2013 genuine zero stays "0"
    expect(wrapper.text()).not.toContain("NaN");
  });

  it("adds the illustrative provenance hedge to the caption only when illustrative", async () => {
    const wrapper = mount(ProductivityPayChart);
    await flushPromises();
    const caption = wrapper.find("table caption").text();
    // Always describes the table content...
    expect(caption).toContain(
      "UK productivity index vs real-pay index by year",
    );
    // ...and adds the provenance hedge because this dataset is illustrative.
    expect(caption).toContain(
      "Illustrative figures derived from ONS bulletins",
    );
  });

  it("omits the illustrative hedge from the caption when the data is live", async () => {
    mockDataType = "live_ons";
    const wrapper = mount(ProductivityPayChart);
    await flushPromises();
    const caption = wrapper.find("table caption").text();
    // The table still renders (a11y is unconditional)...
    expect(wrapper.text()).toContain("View data as table");
    // ...but the caption carries no illustrative wording on genuine data.
    expect(caption).toContain(
      "UK productivity index vs real-pay index by year",
    );
    expect(caption.toLowerCase()).not.toContain("illustrative");
  });
});
