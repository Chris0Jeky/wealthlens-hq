import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import { createRouter, createMemoryHistory } from "vue-router";
import ContributeView from "../ContributeView.vue";

function mountWithRouter() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: "/", component: { template: "<div />" } },
      { path: "/contribute", component: ContributeView },
    ],
  });
  return mount(ContributeView, {
    global: { plugins: [router] },
  });
}

describe("ContributeView", () => {
  it("renders the page heading", () => {
    const wrapper = mountWithRouter();
    expect(wrapper.find("h1").text()).toBe("Contribute to WealthLens UK");
  });

  it("contains contribution categories", () => {
    const wrapper = mountWithRouter();
    const text = wrapper.text();
    expect(text).toContain("Code");
    expect(text).toContain("Data");
    expect(text).toContain("Design");
    expect(text).toContain("Content");
    expect(text).toContain("Research");
  });

  it("contains a GitHub link", () => {
    const wrapper = mountWithRouter();
    const link = wrapper.find('a[href="https://github.com/Chris0Jeky/wealthlens-hq"]');
    expect(link.exists()).toBe(true);
  });

  it("has breadcrumb navigation", () => {
    const wrapper = mountWithRouter();
    const nav = wrapper.find('nav[aria-label="Breadcrumb"]');
    expect(nav.exists()).toBe(true);
    expect(nav.text()).toContain("Home");
    expect(nav.text()).toContain("Contribute");
  });

  it("contains values section", () => {
    const wrapper = mountWithRouter();
    const text = wrapper.text();
    expect(text).toContain("Our Values");
    expect(text).toContain("Open source always");
    expect(text).toContain("Data first, opinion second");
    expect(text).toContain("Accessible by default");
    expect(text).toContain("Independent and non-partisan");
  });

  it("contains getting started steps", () => {
    const wrapper = mountWithRouter();
    const text = wrapper.text();
    expect(text).toContain("Fork the repository");
    expect(text).toContain("Read CONTRIBUTING.md");
    expect(text).toContain("Pick a good first issue");
    expect(text).toContain("Open a pull request");
  });

  it("contains code of conduct section", () => {
    const wrapper = mountWithRouter();
    expect(wrapper.text()).toContain("Code of Conduct");
  });

  it("contains contact section", () => {
    const wrapper = mountWithRouter();
    const text = wrapper.text();
    expect(text).toContain("Contact");
    expect(text).toContain("GitHub Issues");
  });
});
