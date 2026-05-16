import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { mount, VueWrapper } from "@vue/test-utils";
import { createRouter, createWebHistory, Router } from "vue-router";
import App from "@/App.vue";

function makeRouter(): Router {
  return createRouter({
    history: createWebHistory(),
    routes: [{ path: "/", component: { template: "<div>Home</div>" } }],
  });
}

describe("App layout accessibility", () => {
  let wrapper: VueWrapper;

  beforeEach(async () => {
    const router = makeRouter();
    router.push("/");
    await router.isReady();
    wrapper = mount(App, { global: { plugins: [router] } });
  });

  afterEach(() => {
    wrapper.unmount();
  });

  it("renders a skip-to-content link", () => {
    const skipLink = wrapper.find("a[href='#main-content']");

    expect(skipLink.exists()).toBe(true);
    expect(skipLink.text()).toBe("Skip to main content");
  });

  it("skip-to-content link is the first anchor in the DOM", () => {
    const firstAnchor = wrapper.find("a");

    expect(firstAnchor.attributes("href")).toBe("#main-content");
  });

  it("main content target has the correct id and tabindex", () => {
    const main = wrapper.find("main#main-content");

    expect(main.exists()).toBe(true);
    expect(main.attributes("tabindex")).toBe("-1");
  });

  it("nav element has an accessible label", () => {
    const nav = wrapper.find("nav");

    expect(nav.exists()).toBe(true);
    expect(nav.attributes("aria-label")).toBe("Site header");
  });

  it("external GitHub link opens in new tab with noopener", () => {
    const ghLink = wrapper.find('a[href*="github.com"]');

    expect(ghLink.exists()).toBe(true);
    expect(ghLink.attributes("target")).toBe("_blank");
    expect(ghLink.attributes("rel")).toContain("noopener");
  });

  it("footer element exists with expected content", () => {
    const footer = wrapper.find("footer");

    expect(footer.exists()).toBe(true);
    expect(footer.attributes("role")).toBe("contentinfo");
    expect(footer.text()).toContain("WealthLens UK");
  });

  it("home link points to root path", () => {
    const homeLink = wrapper
      .findAll("a")
      .find((a) => a.text().includes("WealthLens"));

    expect(homeLink).toBeDefined();
    expect(homeLink!.attributes("href")).toBe("/");
  });
});
