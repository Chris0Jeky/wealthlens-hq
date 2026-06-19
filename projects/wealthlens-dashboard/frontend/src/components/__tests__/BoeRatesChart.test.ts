import { describe, it, expect, vi, beforeEach } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { ref, shallowRef } from "vue";

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

import BoeRatesChart from "@/components/BoeRatesChart.vue";

/**
 * Mirror the component's own date-label derivation so the expected labels stay
 * timezone-independent: it parses the ISO date and formats YYYY-MM from the
 * resulting Date (falling back to the raw string for an unparseable date).
 */
function expectedDateLabel(iso: string): string {
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
}

/** en-GB locale formatting, computed (never hardcoded) — matches AccessibleDataTable. */
const gb = (n: number): string => Number(n).toLocaleString("en-GB");

/** A few representative rows from the BoE/CPI series (chronological). */
const BOE_ROWS = [
  { date: "2008-01-01", bank_rate: 5.5, cpi_annual: 3.6 },
  { date: "2009-01-01", bank_rate: 1.5, cpi_annual: 2.2 },
  { date: "2022-10-01", bank_rate: 2.25, cpi_annual: 11.1 },
];

describe("BoeRatesChart accessible data table", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setActivePinia(createPinia());
    mockRows = shallowRef<Record<string, unknown>[]>(BOE_ROWS);
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
    const wrapper = mount(BoeRatesChart);
    expect(wrapper.text()).toContain("View data as table");
    const headers = wrapper.findAll("thead th").map((th) => th.text());
    expect(headers).toEqual(["Date", "Bank rate (%)", "CPI annual (%)"]);
  });

  it("populates the table with VERBATIM per-row figures (correct cell mapping)", () => {
    const wrapper = mount(BoeRatesChart);
    const bodyRows = wrapper.findAll("tbody tr");
    expect(bodyRows).toHaveLength(3);

    const cells = (i: number) =>
      bodyRows[i].findAll("td").map((td) => td.text());
    // Per-CELL mapping so a column swap/reorder fails here. Numeric expectations
    // are computed via toLocaleString (no hardcoded locale strings).
    expect(cells(0)).toEqual([
      expectedDateLabel("2008-01-01"),
      gb(5.5),
      gb(3.6),
    ]);
    expect(cells(1)).toEqual([
      expectedDateLabel("2009-01-01"),
      gb(1.5),
      gb(2.2),
    ]);
    expect(cells(2)).toEqual([
      expectedDateLabel("2022-10-01"),
      gb(2.25),
      gb(11.1),
    ]);
  });

  it("sorts rows chronologically, mirroring the chart's own sort", () => {
    // Feed rows out of order; the chart sorts by date, so the table must too.
    mockRows.value = [
      { date: "2022-10-01", bank_rate: 2.25, cpi_annual: 11.1 },
      { date: "2008-01-01", bank_rate: 5.5, cpi_annual: 3.6 },
      { date: "2009-01-01", bank_rate: 1.5, cpi_annual: 2.2 },
    ];
    const wrapper = mount(BoeRatesChart);
    const firstCol = wrapper
      .findAll("tbody tr")
      .map((tr) => tr.findAll("td")[0].text());
    expect(firstCol).toEqual([
      expectedDateLabel("2008-01-01"),
      expectedDateLabel("2009-01-01"),
      expectedDateLabel("2022-10-01"),
    ]);
  });

  it("drops the SAME rows the chart drops (non-numeric bank_rate or cpi_annual)", () => {
    // The chart's filter keeps only rows where Number(bank_rate) AND
    // Number(cpi_annual) are both finite (its mapping does Number(...) then
    // !isNaN(...)). A row whose rate or CPI is omitted/non-numeric → NaN and is
    // excluded from the plot, so it must be excluded from the table too — never
    // silently shown with a fabricated value. (Number(null)/Number("") === 0, so
    // those would NOT be dropped; we use undefined/garbage to force NaN, exactly
    // as the chart does.)
    mockRows.value = [
      { date: "2008-01-01", bank_rate: 5.5, cpi_annual: 3.6 },
      { date: "2009-01-01", cpi_annual: 2.2 }, // bank_rate undefined → NaN → dropped
      { date: "2010-01-01", bank_rate: 0.5, cpi_annual: "n/a" }, // NaN → dropped
    ];
    const wrapper = mount(BoeRatesChart);
    const bodyRows = wrapper.findAll("tbody tr");
    expect(bodyRows).toHaveLength(1);
    expect(bodyRows[0].findAll("td").map((td) => td.text())).toEqual([
      expectedDateLabel("2008-01-01"),
      gb(5.5),
      gb(3.6),
    ]);
    // The dropped dates must not leak into the table anywhere.
    expect(wrapper.text()).not.toContain(expectedDateLabel("2009-01-01"));
    expect(wrapper.text()).not.toContain(expectedDateLabel("2010-01-01"));
    expect(wrapper.text()).not.toContain("NaN");
  });
});
