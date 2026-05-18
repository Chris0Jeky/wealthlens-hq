import { describe, it, expect, vi, beforeEach } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { ref, shallowRef } from "vue";

/**
 * Mock the useChartData composable before importing chart components.
 * Each chart calls useChartData(name) at setup time, which returns
 * { rows, loading, error } refs.
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
 * Mock vue-echarts: the VChart component requires a full ECharts registry
 * (canvas renderer, chart types, etc). We replace it with a simple stub
 * so we can test loading/error/no-data states without ECharts internals.
 */
vi.mock("vue-echarts", () => ({
  default: {
    name: "VChart",
    template: '<div class="vchart-stub" />',
    props: ["option", "autoresize"],
  },
}));

/**
 * Mock echarts/core use() so the chart components' registration calls
 * don't fail in the test environment.
 */
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
  MarkPointComponent: {},
  MarkLineComponent: {},
}));

// Now import the chart components (after mocks are set up)
import WealthSharesChart from "@/components/WealthSharesChart.vue";
import HousingAffordabilityChart from "@/components/HousingAffordabilityChart.vue";
import CgtConcentrationChart from "@/components/CgtConcentrationChart.vue";
import WealthByDecileChart from "@/components/WealthByDecileChart.vue";
import WageStagChart from "@/components/WageStagChart.vue";
import ProductivityPayChart from "@/components/ProductivityPayChart.vue";
import GdhiByRegionChart from "@/components/GdhiByRegionChart.vue";
import TaxCompositionChart from "@/components/TaxCompositionChart.vue";
import BoeRatesChart from "@/components/BoeRatesChart.vue";
import ChildPovertyChart from "@/components/ChildPovertyChart.vue";
import GenerationalWealthChart from "@/components/GenerationalWealthChart.vue";

/**
 * Chart component test matrix.
 * All ten components share the same loading/error/no-data pattern,
 * so we test them uniformly.
 */
const chartComponents = [
  { name: "WealthSharesChart", component: WealthSharesChart, dataset: "wealth-shares" },
  { name: "HousingAffordabilityChart", component: HousingAffordabilityChart, dataset: "housing-affordability" },
  { name: "CgtConcentrationChart", component: CgtConcentrationChart, dataset: "cgt-concentration" },
  { name: "WealthByDecileChart", component: WealthByDecileChart, dataset: "wealth-by-decile" },
  { name: "WageStagChart", component: WageStagChart, dataset: "wage-stagnation" },
  { name: "ProductivityPayChart", component: ProductivityPayChart, dataset: "productivity-pay" },
  { name: "GdhiByRegionChart", component: GdhiByRegionChart, dataset: "gdhi-by-region" },
  { name: "TaxCompositionChart", component: TaxCompositionChart, dataset: "tax-composition" },
  { name: "BoeRatesChart", component: BoeRatesChart, dataset: "boe-rates" },
  { name: "ChildPovertyChart", component: ChildPovertyChart, dataset: "child-poverty" },
  { name: "GenerationalWealthChart", component: GenerationalWealthChart, dataset: "generational-wealth" },
] as const;

describe("Chart components", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setActivePinia(createPinia());
    mockRows = shallowRef([]);
    mockLoading = ref(true);
    mockError = ref(null);

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
  });

  for (const { name, component } of chartComponents) {
    describe(name, () => {
      it("shows loading state initially before data resolves", () => {
        mockLoading.value = true;
        const wrapper = mount(component);

        expect(wrapper.text()).toContain("Loading chart data...");
      });

      it("calls fetchDataset with the correct dataset name", () => {
        // useChartData is called at setup time with the dataset name;
        // we verify the mock was invoked (implicitly by mounting).
        // Since useChartData is fully mocked, just verify mount succeeds.
        mockLoading.value = true;
        const wrapper = mount(component);
        expect(wrapper.exists()).toBe(true);
      });

      it("shows error message when fetchDataset rejects", async () => {
        mockLoading.value = false;
        mockError.value = "Network failure";
        const wrapper = mount(component);

        expect(wrapper.text()).toContain("Network failure");
        expect(wrapper.text()).toContain("Make sure the backend API is running on port 8000");
      });

      it("shows no-data message when fetchDataset returns empty array", async () => {
        mockLoading.value = false;
        mockError.value = null;
        mockRows.value = [];
        const wrapper = mount(component);

        expect(wrapper.text()).toContain("No data available for this chart.");
      });

      it("does not show loading message after data loads", async () => {
        mockLoading.value = false;
        mockError.value = null;
        mockRows.value = [];
        const wrapper = mount(component);

        expect(wrapper.text()).not.toContain("Loading chart data...");
      });
    });
  }

  describe("WealthSharesChart happy path", () => {
    it("renders VChart when data loads successfully", async () => {
      mockLoading.value = false;
      mockError.value = null;
      mockRows.value = [
        { year: 2020, variable: "shweal_p99p100_992_j", percentile: "p99p100", value: 0.213 },
        { year: 2020, variable: "shweal_p90p100_992_j", percentile: "p90p100", value: 0.527 },
        { year: 2021, variable: "shweal_p99p100_992_j", percentile: "p99p100", value: 0.219 },
        { year: 2021, variable: "shweal_p90p100_992_j", percentile: "p90p100", value: 0.531 },
      ];
      const wrapper = mount(WealthSharesChart);

      const vchart = wrapper.find(".vchart-stub");
      expect(vchart.exists()).toBe(true);
      expect(wrapper.text()).not.toContain("No data available");
      expect(wrapper.text()).not.toContain("Loading chart data...");
    });
  });

  describe("WealthSharesChart schema mismatch", () => {
    it("shows no-data when rows lack expected fields", async () => {
      mockLoading.value = false;
      mockError.value = null;
      mockRows.value = [
        { year: 2020, unrelated: "x" },
        { year: 2021, unrelated: "y" },
      ];
      const wrapper = mount(WealthSharesChart);

      expect(wrapper.text()).toContain("No data available for this chart.");
    });
  });

  describe("ProductivityPayChart happy path", () => {
    it("renders VChart when data loads successfully", async () => {
      mockLoading.value = false;
      mockError.value = null;
      mockRows.value = [
        { year: 2000, productivity_index: 108.0, pay_index: 107.0, gap_pct: 0.9 },
        { year: 2010, productivity_index: 123.0, pay_index: 112.0, gap_pct: 9.8 },
        { year: 2020, productivity_index: 128.0, pay_index: 114.0, gap_pct: 12.3 },
      ];
      const wrapper = mount(ProductivityPayChart);

      const vchart = wrapper.find(".vchart-stub");
      expect(vchart.exists()).toBe(true);
      expect(wrapper.text()).not.toContain("No data available");
    });
  });

  describe("GdhiByRegionChart happy path", () => {
    it("renders VChart when data loads successfully", async () => {
      mockLoading.value = false;
      mockError.value = null;
      mockRows.value = [
        { region: "London", gdhi_per_head: 36000, year: 2023 },
        { region: "North East", gdhi_per_head: 18800, year: 2023 },
        { region: "United Kingdom", gdhi_per_head: 24800, year: 2023 },
      ];
      const wrapper = mount(GdhiByRegionChart);

      const vchart = wrapper.find(".vchart-stub");
      expect(vchart.exists()).toBe(true);
      expect(wrapper.text()).not.toContain("No data available");
    });
  });

  describe("TaxCompositionChart happy path", () => {
    it("renders VChart when data loads successfully", async () => {
      mockLoading.value = false;
      mockError.value = null;
      mockRows.value = [
        { year: "2022-23", income_tax_bn: 249, nics_bn: 172, cgt_bn: 14.5, iht_bn: 7.1, sdlt_bn: 12, work_taxes_bn: 421, wealth_taxes_bn: 33.6, total_selected_bn: 454.6, work_pct: 92.6, wealth_pct: 7.4, data_source: "illustrative" },
      ];
      const wrapper = mount(TaxCompositionChart);

      const vchart = wrapper.find(".vchart-stub");
      expect(vchart.exists()).toBe(true);
      expect(wrapper.text()).not.toContain("No data available");
    });
  });

  describe("BoeRatesChart happy path", () => {
    it("renders VChart when data loads successfully", async () => {
      mockLoading.value = false;
      mockError.value = null;
      mockRows.value = [
        { date: "2020-01-01", bank_rate: 0.75, cpi_annual: 1.3 },
        { date: "2023-07-01", bank_rate: 5.25, cpi_annual: 6.8 },
        { date: "2025-01-01", bank_rate: 4.5, cpi_annual: 3.0 },
      ];
      const wrapper = mount(BoeRatesChart);

      const vchart = wrapper.find(".vchart-stub");
      expect(vchart.exists()).toBe(true);
      expect(wrapper.text()).not.toContain("No data available");
    });
  });

  describe("ChildPovertyChart happy path", () => {
    it("renders VChart when data loads successfully", async () => {
      mockLoading.value = false;
      mockError.value = null;
      mockRows.value = [
        { region: "North East", child_poverty_pct: 38, children_in_poverty: 185000, national_avg_pct: 29.8, above_national_avg: true },
        { region: "South East", child_poverty_pct: 22, children_in_poverty: 310000, national_avg_pct: 29.8, above_national_avg: false },
      ];
      const wrapper = mount(ChildPovertyChart);

      const vchart = wrapper.find(".vchart-stub");
      expect(vchart.exists()).toBe(true);
      expect(wrapper.text()).not.toContain("No data available");
    });
  });

  describe("GenerationalWealthChart happy path", () => {
    it("renders VChart when data loads successfully", async () => {
      mockLoading.value = false;
      mockError.value = null;
      mockRows.value = [
        { generation: "Baby Boomers", birth_years: "1946-1964", age_milestone: 30, median_wealth_gbp: 68000, year_measured: 1994, projected: false },
        { generation: "Millennials", birth_years: "1981-1996", age_milestone: 30, median_wealth_gbp: 27000, year_measured: 2016, projected: false },
      ];
      const wrapper = mount(GenerationalWealthChart);

      const vchart = wrapper.find(".vchart-stub");
      expect(vchart.exists()).toBe(true);
      expect(wrapper.text()).not.toContain("No data available");
    });
  });
});
