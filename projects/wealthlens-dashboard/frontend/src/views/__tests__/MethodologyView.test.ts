import { describe, it, expect } from "vitest"
import { mount } from "@vue/test-utils"
import { createRouter, createMemoryHistory } from "vue-router"
import MethodologyView from "../MethodologyView.vue"

function mountWithRouter() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: "/", component: { template: "<div />" } },
      { path: "/methodology", component: MethodologyView },
    ],
  })
  return mount(MethodologyView, {
    global: { plugins: [router] },
  })
}

describe("MethodologyView", () => {
  it("renders the page heading", () => {
    const wrapper = mountWithRouter()
    expect(wrapper.find("h1").text()).toBe("Methodology")
  })

  it("contains all 10 dataset source citations", () => {
    const wrapper = mountWithRouter()
    const expectedDatasets = [
      "wealth-shares",
      "housing-affordability",
      "wealth-by-decile",
      "cgt-concentration",
      "productivity-pay",
      "gdhi-by-region",
      "tax-composition",
      "boe-rates",
      "child-poverty",
      "generational-wealth",
    ]
    for (const name of expectedDatasets) {
      expect(wrapper.text()).toContain(name)
    }
  })

  it("contains privacy note", () => {
    const wrapper = mountWithRouter()
    expect(wrapper.text()).toContain("does not collect personal data")
  })

  it("has breadcrumb navigation", () => {
    const wrapper = mountWithRouter()
    const nav = wrapper.find('nav[aria-label="Breadcrumb"]')
    expect(nav.exists()).toBe(true)
    expect(nav.text()).toContain("Home")
    expect(nav.text()).toContain("Methodology")
  })
})
