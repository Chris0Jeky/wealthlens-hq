import { describe, it, expect, vi, beforeEach } from "vitest";
import { mount, flushPromises } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";

/**
 * Mock the data store before importing chart components.
 * Each chart calls useDataStore().fetchDataset(name) during onMounted.
 */
const mockFetchDataset = vi.fn();

vi.mock("@/stores/data", () => ({
  useDataStore: () => ({
    fetchDataset: mockFetchDataset,
  }),
  // Re-export the type so chart imports don't break
  DatasetRow: undefined,
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
}));

// Now import the chart components (after mocks are set up)
import WealthSharesChart from "@/components/WealthSharesChart.vue";
import HousingAffordabilityChart from "@/components/HousingAffordabilityChart.vue";
import CgtConcentrationChart from "@/components/CgtConcentrationChart.vue";
import WealthByDecileChart from "@/components/WealthByDecileChart.vue";

/**
 * Chart component test matrix.
 * All four components share the same loading/error/no-data pattern,
 * so we test them uniformly.
 */
const chartComponents = [
  { name: "WealthSharesChart", component: WealthSharesChart, dataset: "wealth-shares" },
  { name: "HousingAffordabilityChart", component: HousingAffordabilityChart, dataset: "housing-affordability" },
  { name: "CgtConcentrationChart", component: CgtConcentrationChart, dataset: "cgt-concentration" },
  { name: "WealthByDecileChart", component: WealthByDecileChart, dataset: "wealth-by-decile" },
] as const;

describe("Chart components", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setActivePinia(createPinia());
  });

  for (const { name, component, dataset } of chartComponents) {
    describe(name, () => {
      it("shows loading state initially before data resolves", () => {
        // fetchDataset returns a promise that never resolves, keeping loading=true
        mockFetchDataset.mockReturnValue(new Promise(() => {}));
        const wrapper = mount(component);

        expect(wrapper.text()).toContain("Loading chart data...");
      });

      it("calls fetchDataset with the correct dataset name", () => {
        mockFetchDataset.mockReturnValue(new Promise(() => {}));
        mount(component);

        expect(mockFetchDataset).toHaveBeenCalledWith(dataset);
      });

      it("shows error message when fetchDataset rejects", async () => {
        mockFetchDataset.mockRejectedValue(new Error("Network failure"));
        const wrapper = mount(component);

        await flushPromises();

        expect(wrapper.text()).toContain("Network failure");
        expect(wrapper.text()).toContain("Make sure the backend API is running on port 8000");
      });

      it("shows no-data message when fetchDataset returns empty array", async () => {
        mockFetchDataset.mockResolvedValue([]);
        const wrapper = mount(component);

        await flushPromises();

        expect(wrapper.text()).toContain("No data available for this chart.");
      });

      it("does not show loading message after data loads", async () => {
        mockFetchDataset.mockResolvedValue([]);
        const wrapper = mount(component);

        await flushPromises();

        expect(wrapper.text()).not.toContain("Loading chart data...");
      });
    });
  }
});
