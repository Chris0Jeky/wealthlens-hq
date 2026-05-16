import { describe, it, expect, vi, beforeEach } from "vitest";
import { mount, VueWrapper } from "@vue/test-utils";
import { defineComponent } from "vue";
import { useRoute } from "vue-router";
import HomeView from "@/views/HomeView.vue";
import ChartView from "@/views/ChartView.vue";
import NotFoundView from "@/views/NotFoundView.vue";

// --- Mocks ---

const mockFetchDatasets = vi.fn();
let mockStoreState = {
  datasets: [] as string[],
  loading: false,
  error: null as string | null,
  fetchDatasets: mockFetchDatasets,
};

vi.mock("@/stores/data", () => ({
  useDataStore: () => mockStoreState,
}));

vi.mock("vue-router", () => ({
  useRoute: vi.fn(),
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

// --- HomeView ---

describe("HomeView", () => {
  beforeEach(() => {
    mockFetchDatasets.mockClear();
    mockStoreState = {
      datasets: [],
      loading: false,
      error: null,
      fetchDatasets: mockFetchDatasets,
    };
  });

  it("renders heading", () => {
    const wrapper = mount(HomeView);
    expect(wrapper.find("h1").text()).toBe("UK Wealth Inequality Dashboard");
  });

  it("calls fetchDatasets on mount", () => {
    mount(HomeView);
    expect(mockFetchDatasets).toHaveBeenCalledOnce();
  });

  it("shows loading message when store.loading is true", () => {
    mockStoreState.loading = true;
    const wrapper = mount(HomeView);
    expect(wrapper.text()).toContain("Loading datasets...");
  });

  it("shows error message when store.error is set", () => {
    mockStoreState.error = "Something went wrong";
    const wrapper = mount(HomeView);
    expect(wrapper.text()).toContain("Something went wrong");
  });

  it("renders a DatasetCard for each dataset", () => {
    mockStoreState.datasets = ["wealth-shares", "housing-affordability"];
    const wrapper = mount(HomeView);
    const cards = wrapper.findAll(".dataset-card-stub");
    expect(cards).toHaveLength(2);
    expect(cards[0].text()).toBe("wealth-shares");
    expect(cards[1].text()).toBe("housing-affordability");
  });

  it("uses role=list on the dataset grid", () => {
    mockStoreState.datasets = ["wealth-shares"];
    const wrapper = mount(HomeView);
    expect(wrapper.find('[role="list"]').exists()).toBe(true);
  });
});

// --- ChartView ---

describe("ChartView", () => {
  const chartStubs = {
    "router-link": RouterLinkStub,
    WealthSharesChart: true,
    HousingAffordabilityChart: true,
    CgtConcentrationChart: true,
    WealthByDecileChart: true,
  };

  function mountChart(name: string): VueWrapper {
    vi.mocked(useRoute).mockReturnValue({
      params: { name },
    } as any);
    return mount(ChartView, {
      global: { stubs: chartStubs },
    });
  }

  it("shows chart title for a supported chart", () => {
    const wrapper = mountChart("wealth-shares");
    expect(wrapper.find("h1").text()).toBe(
      "Wealth Shares — Top 1% and Top 10%",
    );
  });

  it('shows "Chart not found" for unsupported chart', () => {
    const wrapper = mountChart("nonexistent");
    expect(wrapper.text()).toContain("Chart not found");
  });

  it('shows "Back to datasets" link', () => {
    const wrapper = mountChart("wealth-shares");
    const link = wrapper.find('a[href="/"]');
    expect(link.exists()).toBe(true);
    expect(link.text()).toContain("Back to datasets");
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

  it('shows "404" heading', () => {
    const wrapper = mount(NotFoundView, mountOpts);
    expect(wrapper.find("h1").text()).toBe("404");
  });

  it('shows "Page not found" text', () => {
    const wrapper = mount(NotFoundView, mountOpts);
    expect(wrapper.find("h2").text()).toBe("Page not found");
  });

  it('shows "Back to dashboard" link pointing to /', () => {
    const wrapper = mount(NotFoundView, mountOpts);
    const link = wrapper.find('a[href="/"]');
    expect(link.exists()).toBe(true);
    expect(link.text()).toContain("Back to dashboard");
  });
});
