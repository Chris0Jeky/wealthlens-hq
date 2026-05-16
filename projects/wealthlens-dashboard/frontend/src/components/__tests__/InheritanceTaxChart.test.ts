import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { mount } from "@vue/test-utils";

/**
 * Mock vue-echarts: the VChart component requires a full ECharts registry.
 * We replace it with a simple stub to test loading/error/data states.
 */
vi.mock("vue-echarts", () => ({
  default: {
    name: "VChart",
    template: '<div class="vchart-stub" />',
    props: ["option", "autoresize"],
  },
}));

/**
 * Mock echarts/core use() so registration calls don't fail in test env.
 */
vi.mock("echarts/core", () => ({
  use: vi.fn(),
}));
vi.mock("echarts/renderers", () => ({
  CanvasRenderer: {},
}));
vi.mock("echarts/charts", () => ({
  PieChart: {},
  BarChart: {},
}));
vi.mock("echarts/components", () => ({
  GridComponent: {},
  TooltipComponent: {},
  TitleComponent: {},
  LegendComponent: {},
}));

vi.mock("@/utils/fetchWithRetry", () => ({
  fetchWithRetry: (...args: unknown[]) => (globalThis as any).fetch(...args),
}));

import InheritanceTaxChart from "@/components/InheritanceTaxChart.vue";

/** Sample valid IHT data matching the static JSON structure. */
const MOCK_IHT_DATA = {
  meta: {
    source: "HMRC Inheritance Tax Statistics 2021-22",
    url: "https://www.gov.uk/government/statistics/inheritance-tax-statistics",
    accessed: "2026-05-16",
    notes: "Table 12.1",
  },
  summary: {
    total_deaths: 600000,
    estates_liable: 27800,
    liability_rate_pct: 4.6,
    total_iht_revenue_bn: 7.1,
    nil_rate_band: 325000,
    residence_nil_rate_band: 175000,
  },
  by_year: [
    { year: "2016-17", deaths: 597200, liable: 24500, rate_pct: 4.1, revenue_bn: 5.0 },
    { year: "2021-22", deaths: 600000, liable: 27800, rate_pct: 4.6, revenue_bn: 7.1 },
  ],
  by_estate_size: [
    { band: "£325k-£500k", estates: 8900, tax_paid_m: 570 },
  ],
};

describe("InheritanceTaxChart", () => {
  let fetchMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    vi.clearAllMocks();

    // Stub window.matchMedia (not available in jsdom by default)
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

    // Default fetch mock: resolves with valid data
    fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(MOCK_IHT_DATA),
    });
    vi.stubGlobal("fetch", fetchMock);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders loading state initially", () => {
    // Make fetch never resolve so the component stays in loading state
    fetchMock.mockReturnValue(new Promise(() => {}));
    const wrapper = mount(InheritanceTaxChart);

    expect(wrapper.text()).toContain("Loading chart data...");
  });

  it("renders error state on fetch failure", async () => {
    fetchMock.mockResolvedValue({ ok: false, status: 404 });
    const wrapper = mount(InheritanceTaxChart);

    // Wait for onMounted to complete
    await vi.waitFor(() => {
      expect(wrapper.text()).toContain("HTTP 404");
    });
    expect(wrapper.text()).toContain(
      "Could not load inheritance tax data",
    );
  });

  it("renders error state on network failure", async () => {
    fetchMock.mockRejectedValue(new Error("Network failure"));
    const wrapper = mount(InheritanceTaxChart);

    await vi.waitFor(() => {
      expect(wrapper.text()).toContain("Network failure");
    });
  });

  it("renders chart container on successful data load", async () => {
    const wrapper = mount(InheritanceTaxChart);

    await vi.waitFor(() => {
      expect(wrapper.find(".vchart-stub").exists()).toBe(true);
    });
    // Should have two chart panels (donut + bar)
    expect(wrapper.findAll(".vchart-stub")).toHaveLength(2);
    // Should not show loading or error
    expect(wrapper.text()).not.toContain("Loading chart data...");
    expect(wrapper.text()).not.toContain("Could not load");
  });

  it("has correct accessibility attributes", async () => {
    const wrapper = mount(InheritanceTaxChart);

    await vi.waitFor(() => {
      expect(wrapper.find("[role='img']").exists()).toBe(true);
    });

    const imgDiv = wrapper.find("[role='img']");
    const ariaLabel = imgDiv.attributes("aria-label") ?? "";
    expect(ariaLabel).toContain("4.6%");
    expect(ariaLabel).toContain("Inheritance Tax");
  });

  it("shows loading with aria-live for screen readers", () => {
    fetchMock.mockReturnValue(new Promise(() => {}));
    const wrapper = mount(InheritanceTaxChart);

    const loadingDiv = wrapper.find("[aria-live='polite']");
    expect(loadingDiv.exists()).toBe(true);
  });

  it("shows error with role=alert for screen readers", async () => {
    fetchMock.mockResolvedValue({ ok: false, status: 500 });
    const wrapper = mount(InheritanceTaxChart);

    await vi.waitFor(() => {
      expect(wrapper.find("[role='alert']").exists()).toBe(true);
    });
  });

  it("includes source citation with correct URL", async () => {
    const wrapper = mount(InheritanceTaxChart);

    await vi.waitFor(() => {
      expect(wrapper.find(".vchart-stub").exists()).toBe(true);
    });

    const link = wrapper.find(
      "a[href='https://www.gov.uk/government/statistics/inheritance-tax-statistics']",
    );
    expect(link.exists()).toBe(true);
    expect(wrapper.text()).toContain("accessed 2026-05-16");
  });
});
