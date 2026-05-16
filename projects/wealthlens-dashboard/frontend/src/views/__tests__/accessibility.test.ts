/**
 * Automated accessibility tests using axe-core via vitest-axe.
 *
 * Validates WCAG AA compliance for key views. Color contrast checks
 * are disabled because jsdom does not support real CSS rendering.
 *
 * These tests catch structural accessibility issues: missing labels,
 * invalid ARIA, landmark violations, heading order, etc.
 */
import { describe, it, expect, vi } from "vitest";
import { mount } from "@vue/test-utils";
import { axe } from "vitest-axe";
import { createRouter, createMemoryHistory } from "vue-router";
import { createTestingPinia } from "@pinia/testing";

import HomeView from "../HomeView.vue";
import AboutView from "../AboutView.vue";
import WealthCalculatorView from "../WealthCalculatorView.vue";
import NotFoundView from "../NotFoundView.vue";

/**
 * Shared axe configuration.
 * - color-contrast: disabled (requires real browser rendering, not jsdom)
 */
const AXE_OPTIONS = {
  rules: {
    "color-contrast": { enabled: false },
  },
};

/** Create router + pinia plugins for mounting views. */
function createMountPlugins() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: "/", component: { template: "<div />" } },
      { path: "/about", component: { template: "<div />" } },
      { path: "/charts/:name", component: { template: "<div />" } },
      { path: "/tools/wealth-calculator", component: { template: "<div />" } },
    ],
  });

  const pinia = createTestingPinia({
    createSpy: vi.fn,
    initialState: {
      data: { datasets: ["wealth-shares"], loading: false, error: null },
    },
  });

  return { router, pinia };
}

/**
 * Filter violations to only critical and serious impact.
 * Minor and moderate issues are logged but don't fail the test,
 * allowing incremental accessibility improvement.
 */
function filterSeriousViolations(
  results: Awaited<ReturnType<typeof axe>>,
): typeof results.violations {
  return results.violations.filter(
    (v) => v.impact === "critical" || v.impact === "serious",
  );
}

describe("Accessibility (axe-core)", () => {
  it("HomeView has no critical accessibility violations", async () => {
    const { router, pinia } = createMountPlugins();
    const wrapper = mount(HomeView, {
      global: { plugins: [router, pinia] },
    });

    const results = await axe(wrapper.element, AXE_OPTIONS);
    const serious = filterSeriousViolations(results);

    expect(serious).toHaveLength(0);
  });

  it("AboutView has no critical accessibility violations", async () => {
    const { router } = createMountPlugins();
    const wrapper = mount(AboutView, {
      global: { plugins: [router] },
    });

    const results = await axe(wrapper.element, AXE_OPTIONS);
    const serious = filterSeriousViolations(results);

    expect(serious).toHaveLength(0);
  });

  it("WealthCalculatorView has no critical accessibility violations", async () => {
    const { router } = createMountPlugins();
    const wrapper = mount(WealthCalculatorView, {
      global: { plugins: [router] },
    });

    const results = await axe(wrapper.element, AXE_OPTIONS);
    const serious = filterSeriousViolations(results);

    expect(serious).toHaveLength(0);
  });

  it("NotFoundView has no critical accessibility violations", async () => {
    const { router } = createMountPlugins();
    const wrapper = mount(NotFoundView, {
      global: { plugins: [router] },
    });

    const results = await axe(wrapper.element, AXE_OPTIONS);
    const serious = filterSeriousViolations(results);

    expect(serious).toHaveLength(0);
  });
});
