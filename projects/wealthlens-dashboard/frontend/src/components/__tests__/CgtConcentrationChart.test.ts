import { describe, it, expect, vi, beforeEach } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { ref, shallowRef } from "vue";

/**
 * CgtConcentrationChart tests — focused on the ADDITIVE concentration-curve
 * (Lorenz) view added in WL-011. The shared loading/error/no-data behaviour is
 * covered uniformly in ChartComponents.test.ts; here we test that:
 *   - the existing "By gain band" view is the default (backward-compatible),
 *   - activating the "Concentration curve" tab renders the curve + a data table,
 *   - the data table holds the VERBATIM cumulative values from the data file
 *     (including a >100 rounding artifact that is kept raw in the table even
 *     though it is clamped for the plotted curve),
 *   - per-row cell mapping is correct (not just value presence),
 *   - the curve points are ordered from the top band down.
 *
 * The component reads data through useChartData(), so we mock that composable
 * (mirroring ChartComponents.test.ts) to drive rows/loading/error directly.
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

/**
 * Mock vue-echarts: VChart needs a full ECharts registry. Replace it with a
 * stub so we can test view/table behaviour without ECharts internals.
 */
vi.mock("vue-echarts", () => ({
  default: {
    name: "VChart",
    template: '<div class="vchart-stub" />',
    props: ["option", "autoresize"],
  },
}));

vi.mock("echarts/core", () => ({
  use: vi.fn(),
}));
vi.mock("echarts/renderers", () => ({
  CanvasRenderer: {},
}));
vi.mock("echarts/charts", () => ({
  LineChart: {},
  BarChart: {},
}));
vi.mock("echarts/components", () => ({
  GridComponent: {},
  TooltipComponent: {},
  TitleComponent: {},
  LegendComponent: {},
}));

import CgtConcentrationChart from "@/components/CgtConcentrationChart.vue";

/**
 * Fixture mirroring the real HMRC CGT concentration columns. The cumulative
 * columns are "from the top" (top band has the smallest taxpayer share). The
 * bottom band (£0+) is given a deliberate >100 rounding artifact (100.6 /
 * 100.1) to exercise the clamp-for-display vs verbatim-in-table behaviour.
 * Provided in arbitrary order to prove the component sorts, not the fixture.
 */
const CGT_ROWS = [
  {
    gain_band: "£100k+",
    band_lower: 100000,
    share_of_gains_pct: 18.0,
    share_of_taxpayers_pct: 9.0,
    cumul_gains_from_top_pct: 85.0,
    cumul_taxpayers_from_top_pct: 22.0,
  },
  {
    gain_band: "£0+",
    band_lower: 0,
    share_of_gains_pct: 7.0,
    share_of_taxpayers_pct: 60.0,
    cumul_gains_from_top_pct: 100.6, // >100 rounding artifact
    cumul_taxpayers_from_top_pct: 100.1, // >100 rounding artifact
  },
  {
    gain_band: "£1m+",
    band_lower: 1000000,
    share_of_gains_pct: 45.0,
    share_of_taxpayers_pct: 1.5,
    cumul_gains_from_top_pct: 45.0,
    cumul_taxpayers_from_top_pct: 1.5,
  },
  {
    gain_band: "£50k+",
    band_lower: 50000,
    share_of_gains_pct: 8.0,
    share_of_taxpayers_pct: 18.0,
    cumul_gains_from_top_pct: 93.0,
    cumul_taxpayers_from_top_pct: 40.0,
  },
  {
    gain_band: "£500k+",
    band_lower: 500000,
    share_of_gains_pct: 22.0,
    share_of_taxpayers_pct: 3.0,
    cumul_gains_from_top_pct: 67.0,
    cumul_taxpayers_from_top_pct: 13.0,
  },
];

describe("CgtConcentrationChart concentration-curve view (WL-011)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setActivePinia(createPinia());
    mockRows = shallowRef(CGT_ROWS);
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

  it("defaults to the by-gain-band view (curve view is opt-in)", () => {
    const wrapper = mount(CgtConcentrationChart);

    // Two view tabs are present, with "By gain band" selected by default.
    const tabs = wrapper.findAll("[role='tab']");
    expect(tabs).toHaveLength(2);
    const bandTab = tabs.find((t) => t.text() === "By gain band");
    const curveTab = tabs.find((t) => t.text() === "Concentration curve");
    expect(bandTab?.attributes("aria-selected")).toBe("true");
    expect(curveTab?.attributes("aria-selected")).toBe("false");

    // Default view renders the dual-axis chart and does NOT show the curve
    // view's accessible data table — behaviour is unchanged from before WL-011.
    expect(wrapper.find(".vchart-stub").exists()).toBe(true);
    expect(wrapper.text()).not.toContain("View data as table");

    // The default view keeps the original headline aria-label.
    const label = wrapper.find("[role='img']").attributes("aria-label") ?? "";
    expect(label).toContain("Dual-axis chart showing capital gains concentration");
  });

  it("renders the concentration curve and its data table when the tab is activated", async () => {
    const wrapper = mount(CgtConcentrationChart);

    const curveTab = wrapper
      .findAll("[role='tab']")
      .find((t) => t.text() === "Concentration curve");
    expect(curveTab).toBeDefined();
    await curveTab!.trigger("click");

    // The curve view shows a single chart plus the accessible data table.
    expect(wrapper.findAll(".vchart-stub")).toHaveLength(1);
    expect(wrapper.text()).toContain("View data as table");
  });

  it("populates the data table with VERBATIM cumulative values, ordered from the top band down", async () => {
    const wrapper = mount(CgtConcentrationChart);

    const curveTab = wrapper
      .findAll("[role='tab']")
      .find((t) => t.text() === "Concentration curve");
    await curveTab!.trigger("click");

    // One row per band (5 in the fixture), ordered by cumulative taxpayer share
    // ascending — i.e. top band (£1m+) first, bottom band (£0+) last.
    const bodyRows = wrapper.findAll("tbody tr");
    expect(bodyRows).toHaveLength(5);

    const cellTexts = (rowIdx: number) =>
      bodyRows[rowIdx].findAll("td").map((td) => td.text());

    // Assert per-row CELL MAPPING (column order: band, cumul taxpayers, cumul
    // gains) — not just presence — so a field/column swap or reorder fails here.
    // Values are the verbatim cumulative figures; numeric columns are locale-
    // formatted (en-GB) by AccessibleDataTable.
    expect(cellTexts(0)).toEqual(["£1m+", "1.5", "45"]);
    expect(cellTexts(1)).toEqual(["£500k+", "13", "67"]);
    expect(cellTexts(2)).toEqual(["£100k+", "22", "85"]);
    expect(cellTexts(3)).toEqual(["£50k+", "40", "93"]);
    // Bottom band keeps the RAW >100 rounding artifact in the table verbatim
    // (it is only clamped for the plotted curve, never in the data table).
    expect(cellTexts(4)).toEqual(["£0+", "100.1", "100.6"]);
  });

  it("describes the curve with a data-driven aria-label reading the most concentrated (top) band", async () => {
    const wrapper = mount(CgtConcentrationChart);

    const curveTab = wrapper
      .findAll("[role='tab']")
      .find((t) => t.text() === "Concentration curve");
    await curveTab!.trigger("click");

    // The curve view's role=img label reads the top band straight from the
    // data, mentions the equality line, and does not rely on colour alone.
    const label = wrapper.find("[role='img']").attributes("aria-label") ?? "";
    expect(label).toContain("Concentration curve plotting");
    expect(label).toContain('"£1m+ or more" band');
    expect(label).toContain("top 1.5% of taxpayers");
    expect(label).toContain("45.0% of all gains");
    expect(label).toContain("equality line");
  });

  it("keeps the HMRC source citation on the curve view", async () => {
    const wrapper = mount(CgtConcentrationChart);

    const curveTab = wrapper
      .findAll("[role='tab']")
      .find((t) => t.text() === "Concentration curve");
    await curveTab!.trigger("click");

    const link = wrapper.find(
      "a[href='https://www.gov.uk/government/statistics/capital-gains-tax-statistics']",
    );
    expect(link.exists()).toBe(true);
    expect(wrapper.text()).toContain("accessed 2026-05-14");
  });

  it("shows a graceful message when the curve view has no plottable rows", async () => {
    // The real data uses an explicit null for a missing cumulative taxpayer
    // figure. Number(null) === 0, so without the toFiniteOrNaN guard this row
    // would be plotted at the origin; it must instead be treated as missing →
    // curve guard message, no table.
    mockRows.value = [
      {
        gain_band: "£0+",
        band_lower: 0,
        share_of_gains_pct: 7.0,
        cumul_gains_from_top_pct: 100.0,
        cumul_taxpayers_from_top_pct: null,
      },
    ];
    const wrapper = mount(CgtConcentrationChart);

    const curveTab = wrapper
      .findAll("[role='tab']")
      .find((t) => t.text() === "Concentration curve");
    await curveTab!.trigger("click");

    expect(wrapper.text()).toContain(
      "No concentration-curve data available for this chart.",
    );
    expect(wrapper.text()).not.toContain("View data as table");
  });

  it("drops a band with a null cumulative-taxpayer value from the curve, not plots it at the origin", async () => {
    // Mirrors the real data: the "£3,000+" band has cumul_taxpayers_from_top_pct
    // null but a valid cumul_gains_from_top_pct (~100). Number(null) === 0 would
    // fabricate a (0, 100.1) point that sorts FIRST and would hijack the
    // headline/aria-label. Assert it is dropped from the curve + table and the
    // real top band (£1m+) remains the most-concentrated point.
    mockRows.value = [
      ...CGT_ROWS,
      {
        gain_band: "£3k+",
        band_lower: 3000,
        share_of_gains_pct: 0.0,
        share_of_taxpayers_pct: 0.6,
        cumul_gains_from_top_pct: 100.1,
        cumul_taxpayers_from_top_pct: null,
      },
    ];
    const wrapper = mount(CgtConcentrationChart);

    const curveTab = wrapper
      .findAll("[role='tab']")
      .find((t) => t.text() === "Concentration curve");
    await curveTab!.trigger("click");

    // The null-taxpayer band is NOT plotted (still 5 valid rows, not 6) and does
    // not appear in the curve table.
    const bodyRows = wrapper.findAll("tbody tr");
    expect(bodyRows).toHaveLength(5);
    const tableText = bodyRows.map((r) => r.text()).join(" ");
    expect(tableText).not.toContain("£3k+");

    // The headline aria-label still reads the genuine top band, not the fabricated 0%.
    const label = wrapper.find("[role='img']").attributes("aria-label") ?? "";
    expect(label).toContain('"£1m+ or more" band');
    expect(label).toContain("top 1.5% of taxpayers");
    expect(label).not.toContain("0.0% of taxpayers");
  });

  it("clamps only the plotted >100 point, keeping the raw value in the table", async () => {
    const wrapper = mount(CgtConcentrationChart);

    const curveTab = wrapper
      .findAll("[role='tab']")
      .find((t) => t.text() === "Concentration curve");
    await curveTab!.trigger("click");

    // Read the curve VChart's option directly (vue-echarts is stubbed with an
    // `option` prop) to assert the clamp is applied to the PLOTTED series.
    const vchart = wrapper.findComponent({ name: "VChart" });
    const option = vchart.props("option") as {
      series: { name: string; data: number[][] }[];
    };
    const curve = option.series.find((s) => s.name === "Concentration curve");
    // Bottom band (£0+, raw 100.1/100.6) is last after the ascending sort and is
    // clamped to the (100, 100) corner for the plot.
    expect(curve?.data[curve.data.length - 1]).toEqual([100, 100]);
    // The equality reference line is the fixed static diagonal.
    const equality = option.series.find((s) => s.name === "Equality line (y = x)");
    expect(equality?.data).toEqual([
      [0, 0],
      [100, 100],
    ]);
    // (The verbatim 100.1 / 100.6 staying in the TABLE is asserted above.)
  });
});
