import { describe, it, expect } from "vitest";
import { mount, RouterLinkStub } from "@vue/test-utils";
import { createRouter, createMemoryHistory } from "vue-router";
import App from "@/App.vue";

function createMockRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: "/", name: "home", component: { template: "<div>Home</div>" } },
    ],
  });
}

async function mountApp() {
  const router = createMockRouter();
  router.push("/");
  await router.isReady();

  return mount(App, {
    global: {
      plugins: [router],
      stubs: {
        RouterLink: RouterLinkStub,
        ErrorBoundary: { template: "<div><slot /></div>" },
      },
    },
  });
}

describe("App", () => {
  it("renders the skip-to-content link", async () => {
    const wrapper = await mountApp();
    const skipLink = wrapper.find('a[href="#main-content"]');
    expect(skipLink.exists()).toBe(true);
    expect(skipLink.text()).toContain("Skip to main content");
  });

  it("renders the header with brand name", async () => {
    const wrapper = await mountApp();
    expect(wrapper.find("header").exists()).toBe(true);
    expect(wrapper.text()).toContain("WealthLens");
    expect(wrapper.text()).toContain("UK");
  });

  it("renders the main content area with correct id", async () => {
    const wrapper = await mountApp();
    const main = wrapper.find("main#main-content");
    expect(main.exists()).toBe(true);
  });

  it("renders the footer with contentinfo role", async () => {
    const wrapper = await mountApp();
    const footer = wrapper.find('footer[role="contentinfo"]');
    expect(footer.exists()).toBe(true);
    expect(footer.text()).toContain("Open source");
  });

  it("includes GitHub link in navigation", async () => {
    const wrapper = await mountApp();
    const nav = wrapper.find('nav[aria-label="Main navigation"]');
    expect(nav.exists()).toBe(true);
    const ghLink = nav.find('a[href="https://github.com/Chris0Jeky/wealthlens-hq"]');
    expect(ghLink.exists()).toBe(true);
    expect(ghLink.attributes("target")).toBe("_blank");
  });
});
