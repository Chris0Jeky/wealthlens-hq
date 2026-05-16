import { describe, it, expect, vi } from "vitest";
import { mount, RouterLinkStub } from "@vue/test-utils";
import { createRouter, createMemoryHistory } from "vue-router";
import ChartView from "@/views/ChartView.vue";

function createMockRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: "/charts/:name", name: "chart", component: ChartView },
      { path: "/", name: "home", component: { template: "<div />" } },
    ],
  });
}

async function mountChartView(chartName: string) {
  const router = createMockRouter();
  router.push(`/charts/${chartName}`);
  await router.isReady();

  return mount(ChartView, {
    global: {
      plugins: [router],
      stubs: {
        RouterLink: RouterLinkStub,
        WealthSharesChart: { template: '<div data-testid="wealth-shares-chart" />' },
        HousingAffordabilityChart: { template: '<div data-testid="housing-chart" />' },
        CgtConcentrationChart: { template: '<div data-testid="cgt-chart" />' },
        WealthByDecileChart: { template: '<div data-testid="decile-chart" />' },
      },
    },
  });
}

describe("ChartView", () => {
  it("renders the title for a supported chart", async () => {
    const wrapper = await mountChartView("wealth-shares");
    expect(wrapper.find("h1").text()).toContain("Wealth Shares");
  });

  it("renders back-to-datasets link", async () => {
    const wrapper = await mountChartView("wealth-shares");
    const link = wrapper.findComponent(RouterLinkStub);
    expect(link.exists()).toBe(true);
    expect(link.props("to")).toBe("/");
  });

  it("renders the correct chart component for wealth-shares", async () => {
    const wrapper = await mountChartView("wealth-shares");
    expect(wrapper.find('[data-testid="wealth-shares-chart"]').exists()).toBe(true);
  });

  it("renders the correct chart component for housing-affordability", async () => {
    const wrapper = await mountChartView("housing-affordability");
    expect(wrapper.find('[data-testid="housing-chart"]').exists()).toBe(true);
  });

  it("renders the correct chart component for cgt-concentration", async () => {
    const wrapper = await mountChartView("cgt-concentration");
    expect(wrapper.find('[data-testid="cgt-chart"]').exists()).toBe(true);
  });

  it("renders the correct chart component for wealth-by-decile", async () => {
    const wrapper = await mountChartView("wealth-by-decile");
    expect(wrapper.find('[data-testid="decile-chart"]').exists()).toBe(true);
  });

  it("shows 'chart not found' for unsupported chart names", async () => {
    const wrapper = await mountChartView("unknown-chart");
    expect(wrapper.text()).toContain("Chart not found");
  });

  it("displays the chart name in the not-found message", async () => {
    const wrapper = await mountChartView("bad-name");
    expect(wrapper.find(".font-mono").text()).toBe("bad-name");
  });

  it("shows return-to-dashboard link for unsupported charts", async () => {
    const wrapper = await mountChartView("unknown-chart");
    const links = wrapper.findAllComponents(RouterLinkStub);
    const returnLink = links.find((l) => l.text().includes("Return to dashboard"));
    expect(returnLink).toBeDefined();
    expect(returnLink!.props("to")).toBe("/");
  });

  it.each([
    ["housing-affordability", "Housing Affordability"],
    ["cgt-concentration", "Capital Gains Tax"],
    ["wealth-by-decile", "Total Household Wealth"],
  ])("renders correct title for %s", async (name, titleFragment) => {
    const wrapper = await mountChartView(name);
    expect(wrapper.find("h1").text()).toContain(titleFragment);
  });
});
