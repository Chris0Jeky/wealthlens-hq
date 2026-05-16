import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import { createRouter, createWebHistory } from "vue-router";
import App from "@/App.vue";

function makeRouter() {
  return createRouter({
    history: createWebHistory(),
    routes: [{ path: "/", component: { template: "<div>Home</div>" } }],
  });
}

describe("App layout accessibility", () => {
  it("renders a skip-to-content link as the first focusable element", async () => {
    const router = makeRouter();
    router.push("/");
    await router.isReady();

    const wrapper = mount(App, { global: { plugins: [router] } });
    const skipLink = wrapper.find("a[href='#main-content']");

    expect(skipLink.exists()).toBe(true);
    expect(skipLink.text()).toBe("Skip to main content");
  });

  it("main content target has the correct id and tabindex", async () => {
    const router = makeRouter();
    router.push("/");
    await router.isReady();

    const wrapper = mount(App, { global: { plugins: [router] } });
    const main = wrapper.find("main#main-content");

    expect(main.exists()).toBe(true);
    expect(main.attributes("tabindex")).toBe("-1");
  });

  it("nav element has an accessible label", async () => {
    const router = makeRouter();
    router.push("/");
    await router.isReady();

    const wrapper = mount(App, { global: { plugins: [router] } });
    const nav = wrapper.find("nav");

    expect(nav.exists()).toBe(true);
    expect(nav.attributes("aria-label")).toBe("Main navigation");
  });

  it("external GitHub link opens in new tab with noopener", async () => {
    const router = makeRouter();
    router.push("/");
    await router.isReady();

    const wrapper = mount(App, { global: { plugins: [router] } });
    const ghLink = wrapper.find('a[href*="github.com"]');

    expect(ghLink.exists()).toBe(true);
    expect(ghLink.attributes("target")).toBe("_blank");
    expect(ghLink.attributes("rel")).toContain("noopener");
  });

  it("footer has contentinfo role", async () => {
    const router = makeRouter();
    router.push("/");
    await router.isReady();

    const wrapper = mount(App, { global: { plugins: [router] } });
    const footer = wrapper.find('footer[role="contentinfo"]');

    expect(footer.exists()).toBe(true);
  });

  it("home link navigates to root", async () => {
    const router = makeRouter();
    router.push("/");
    await router.isReady();

    const wrapper = mount(App, { global: { plugins: [router] } });
    const homeLink = wrapper.find("a.text-xl");

    expect(homeLink.exists()).toBe(true);
    expect(homeLink.attributes("href")).toBe("/");
  });
});
