import { describe, it, expect, vi, beforeEach } from "vitest";
import { mount, VueWrapper } from "@vue/test-utils";
import { defineComponent, reactive } from "vue";
import { useRoute } from "vue-router";
import HomeView from "@/views/HomeView.vue";
import ChartView from "@/views/ChartView.vue";
import NotFoundView from "@/views/NotFoundView.vue";

// --- Mocks ---

const mockFetchDatasets = vi.fn();
const mockFetchAllMetadata = vi.fn();
const mockFetchFreshness = vi.fn();
const mockStoreState = reactive({
  datasets: [] as string[],
  metadata: new Map(),
  freshness: {} as Record<string, unknown>,
  loading: false,
  error: null as string | null,
  fetchDatasets: mockFetchDatasets,
  fetchAllMetadata: mockFetchAllMetadata,
  fetchFreshness: mockFetchFreshness,
});

vi.mock("@/stores/data", () => ({
  useDataStore: () => mockStoreState,
}));

vi.mock("vue-router", () => ({
  useRoute: vi.fn(),
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
}));

vi.mock("@/composables/useAnalytics", () => ({
  useAnalytics: () => ({
    init: vi.fn(),
    trackEvent: vi.fn(),
    isEnabled: false,
  }),
}));

const RouterLinkStub = {
  template: '<a :href="to"><slot /></a>',
  props: ["to"],
};

vi.mock("@/components/DatasetCard.vue", () => ({
  default: defineComponent({
    name: "DatasetCardStub",
    props: ["name", "description"],
    template: '<div class="dataset-card-stub">{{ name }}</div>',
  }),
}));

// Chart components are stubbed via global.stubs in mount options (see ChartView tests)
// to avoid vitest mock proxy issues with Vue internal markers.

// Mock echarts modules to prevent EnvironmentTeardownError when
// defineAsyncComponent resolves chart imports after test cleanup.
vi.mock("echarts/core", () => ({ use: vi.fn() }));
vi.mock("echarts/renderers", () => ({ CanvasRenderer: {} }));
vi.mock("echarts/charts", () => ({ LineChart: {}, BarChart: {} }));
vi.mock("echarts/components", () => ({
  GridComponent: {},
  TooltipComponent: {},
  TitleComponent: {},
  LegendComponent: {},
}));
vi.mock("vue-echarts", () => ({
  default: { name: "VChart", template: '<div class="vchart-stub" />', props: ["option", "autoresize"] },
}));
vi.mock("@/composables/useChartData", () => ({
  useChartData: () => ({
    rows: { value: [] },
    loading: { value: false },
    error: { value: null },
  }),
}));

// --- HomeView ---

describe("HomeView", () => {
  beforeEach(() => {
    mockFetchDatasets.mockClear();
    mockFetchAllMetadata.mockClear();
    mockFetchFreshness.mockClear();
    mockStoreState.datasets = [];
    mockStoreState.metadata = new Map();
    mockStoreState.freshness = {};
    mockStoreState.loading = false;
    mockStoreState.error = null;
  });

  it("renders heading", () => {
    const wrapper = mount(HomeView);
    expect(wrapper.find("h1").text()).toBe("UK Wealth Inequality Dashboard");
  });

  it("calls fetchDatasets on mount", () => {
    mount(HomeView);
    expect(mockFetchDatasets).toHaveBeenCalledOnce();
  });

  it("calls fetchAllMetadata on mount", () => {
    mount(HomeView);
    expect(mockFetchAllMetadata).toHaveBeenCalledOnce();
  });

  it("calls fetchFreshness on mount", () => {
    mount(HomeView);
    expect(mockFetchFreshness).toHaveBeenCalledOnce();
  });

  it("always renders all 10 hardcoded dataset cards", () => {
    const wrapper = mount(HomeView);
    const cards = wrapper.findAll(".dataset-card-stub");
    expect(cards).toHaveLength(10);
  });

  it("renders cards even when store is loading", () => {
    mockStoreState.loading = true;
    const wrapper = mount(HomeView);
    const cards = wrapper.findAll(".dataset-card-stub");
    expect(cards).toHaveLength(10);
  });

  it("renders cards even when store has error", () => {
    mockStoreState.error = "Something went wrong";
    const wrapper = mount(HomeView);
    const cards = wrapper.findAll(".dataset-card-stub");
    expect(cards).toHaveLength(10);
  });

  it("uses role=list on the dataset grid", () => {
    const wrapper = mount(HomeView);
    expect(wrapper.find('[role="list"]').exists()).toBe(true);
  });
});

// --- ChartView ---

describe("ChartView", () => {
  beforeEach(() => {
    vi.mocked(useRoute).mockReset();
  });

  const chartStubs = {
    "router-link": RouterLinkStub,
    WealthSharesChart: true,
    HousingAffordabilityChart: true,
    CgtConcentrationChart: true,
    WealthByDecileChart: true,
    StatStrip: true,
    ChartToolbar: true,
    ShareBar: true,
    RelatedCharts: true,
  };

  function mountChart(name: string): VueWrapper {
    vi.mocked(useRoute).mockReturnValue({
      params: { name },
    } as unknown as ReturnType<typeof useRoute>);
    return mount(ChartView, {
      global: { stubs: chartStubs },
    });
  }

  it.each([
    ["wealth-shares", "Who owns wealth in the UK?"],
    ["housing-affordability", "Housing Affordability — Price-to-Earnings Ratios by Region"],
    ["cgt-concentration", "Capital Gains Tax — Concentration by Size of Gain"],
    ["wealth-by-decile", "Total Household Wealth by Decile"],
  ])("shows correct title for %s", (name, expectedTitle) => {
    const wrapper = mountChart(name);
    expect(wrapper.find("h1").text()).toContain(expectedTitle);
  });

  it('shows "Chart not found" for unsupported chart', () => {
    const wrapper = mountChart("nonexistent");
    expect(wrapper.text()).toContain("Chart not found");
  });

  it('shows "Home" breadcrumb link', () => {
    const wrapper = mountChart("wealth-shares");
    const link = wrapper.find('a[href="/"]');
    expect(link.exists()).toBe(true);
    expect(link.text()).toContain("Home");
  });

  it('shows "Return to dashboard" link for unsupported chart', () => {
    const wrapper = mountChart("nonexistent");
    const links = wrapper.findAll('a[href="/"]');
    const returnLink = links.find((l) => l.text().includes("Return to dashboard"));
    expect(returnLink).toBeDefined();
  });
});

// --- NotFoundView ---

describe("NotFoundView", () => {
  const mountOpts = { global: { stubs: { "router-link": RouterLinkStub } } };

  it('shows "Page not found" heading', () => {
    const wrapper = mount(NotFoundView, mountOpts);
    expect(wrapper.find("h1").text()).toBe("Page not found");
  });

  it('shows decorative 404 text', () => {
    const wrapper = mount(NotFoundView, mountOpts);
    const decorative = wrapper.find('p[aria-hidden="true"]');
    expect(decorative.exists()).toBe(true);
    expect(decorative.text()).toBe("404");
  });

  it('shows "Back to dashboard" link pointing to /', () => {
    const wrapper = mount(NotFoundView, mountOpts);
    const link = wrapper.find('a[href="/"]');
    expect(link.exists()).toBe(true);
    expect(link.text()).toContain("Back to dashboard");
  });
});
