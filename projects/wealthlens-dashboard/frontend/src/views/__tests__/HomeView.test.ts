import { describe, it, expect, vi, beforeEach } from "vitest";
import { mount, RouterLinkStub } from "@vue/test-utils";
import { createTestingPinia } from "@pinia/testing";
import HomeView from "@/views/HomeView.vue";

describe("HomeView", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  function mountView(datasets: string[] = [], loading = false, error: string | null = null) {
    return mount(HomeView, {
      global: {
        stubs: { RouterLink: RouterLinkStub },
        plugins: [
          createTestingPinia({
            createSpy: vi.fn,
            initialState: {
              data: { datasets, loading, error },
            },
          }),
        ],
      },
    });
  }

  it("renders the dashboard heading", () => {
    const wrapper = mountView();
    expect(wrapper.find("h1").text()).toContain("UK Wealth Inequality Dashboard");
  });

  it("shows loading state", () => {
    const wrapper = mountView([], true);
    expect(wrapper.text()).toContain("Loading datasets...");
  });

  it("shows error state", () => {
    const wrapper = mountView([], false, "Network error");
    expect(wrapper.text()).toContain("Network error");
  });

  it("renders dataset cards when data is loaded", () => {
    const wrapper = mountView(["wealth-shares", "housing-affordability"]);
    const items = wrapper.findAll('[role="listitem"]');
    expect(items).toHaveLength(2);
  });

  it("displays dataset descriptions", () => {
    const wrapper = mountView(["wealth-shares"]);
    expect(wrapper.text()).toContain("Top 1% and 10% share of UK net personal wealth");
  });
});
