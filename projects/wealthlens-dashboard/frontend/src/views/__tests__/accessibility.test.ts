import { describe, it, expect, vi } from "vitest"
import { mount, flushPromises } from "@vue/test-utils"
import { axe } from "vitest-axe"
import "vitest-axe/extend-expect"
import { createRouter, createMemoryHistory } from "vue-router"
import { createTestingPinia } from "@pinia/testing"

import HomeView from "../HomeView.vue"
import AboutView from "../AboutView.vue"
import WealthCalculatorView from "../WealthCalculatorView.vue"
import NotFoundView from "../NotFoundView.vue"

// The front page lazy-loads the featured chart; mock it so tests don't race
// the echarts dynamic import against environment teardown.
vi.mock("@/components/WealthSharesChart.vue", async () => {
  const { defineComponent, h } = await import("vue")
  return {
    __esModule: true,
    default: defineComponent({
      name: "WealthSharesChart",
      setup() {
        return () =>
          h("div", {
            class: "wealth-shares-chart-stub",
            role: "img",
            "aria-label": "Featured chart stub",
          })
      },
    }),
  }
})

const AXE_OPTIONS = {
  rules: {
    "color-contrast": { enabled: false },
  },
}

function createMountPlugins() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: "/", component: { template: "<div />" } },
      { path: "/about", component: { template: "<div />" } },
      { path: "/charts/:name", component: { template: "<div />" } },
      { path: "/tools/wealth-calculator", component: { template: "<div />" } },
    ],
  })

  const pinia = createTestingPinia({
    createSpy: vi.fn,
    initialState: {
      data: { datasets: ["wealth-shares"], loading: false, error: null },
    },
  })

  return { router, pinia }
}

function filterSeriousViolations(
  results: Awaited<ReturnType<typeof axe>>,
): typeof results.violations {
  const dominated = results.violations.filter(
    (v) => v.impact !== "critical" && v.impact !== "serious",
  )
  if (dominated.length > 0) {
    console.warn(
      `[a11y] ${dominated.length} non-critical violation(s) suppressed:`,
      dominated.map((v) => `${v.id} [${v.impact}]`),
    )
  }
  return results.violations.filter((v) => v.impact === "critical" || v.impact === "serious")
}

describe("Accessibility (axe-core)", () => {
  it("HomeView has no critical accessibility violations", async () => {
    const { router, pinia } = createMountPlugins()
    router.push("/")
    await router.isReady()
    const wrapper = mount(HomeView, {
      global: { plugins: [router, pinia] },
    })
    await flushPromises()

    const results = await axe(wrapper.element, AXE_OPTIONS)
    expect(
      results.passes.length + results.violations.length + results.incomplete.length,
    ).toBeGreaterThan(0)
    const serious = filterSeriousViolations(results)
    expect(serious).toHaveLength(0)
  })

  it("AboutView has no critical accessibility violations", async () => {
    const { router } = createMountPlugins()
    router.push("/about")
    await router.isReady()
    const wrapper = mount(AboutView, {
      global: { plugins: [router] },
    })
    await flushPromises()

    const results = await axe(wrapper.element, AXE_OPTIONS)
    expect(
      results.passes.length + results.violations.length + results.incomplete.length,
    ).toBeGreaterThan(0)
    const serious = filterSeriousViolations(results)
    expect(serious).toHaveLength(0)
  })

  it("WealthCalculatorView has no critical accessibility violations", async () => {
    const { router } = createMountPlugins()
    router.push("/tools/wealth-calculator")
    await router.isReady()
    const wrapper = mount(WealthCalculatorView, {
      global: { plugins: [router] },
    })
    await flushPromises()

    const results = await axe(wrapper.element, AXE_OPTIONS)
    expect(
      results.passes.length + results.violations.length + results.incomplete.length,
    ).toBeGreaterThan(0)
    const serious = filterSeriousViolations(results)
    expect(serious).toHaveLength(0)
  })

  it("NotFoundView has no critical accessibility violations", async () => {
    const { router } = createMountPlugins()
    router.push("/nowhere")
    await router.isReady()
    const wrapper = mount(NotFoundView, {
      global: { plugins: [router] },
    })
    await flushPromises()

    const results = await axe(wrapper.element, AXE_OPTIONS)
    expect(
      results.passes.length + results.violations.length + results.incomplete.length,
    ).toBeGreaterThan(0)
    const serious = filterSeriousViolations(results)
    expect(serious).toHaveLength(0)
  })
})
