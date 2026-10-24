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

  it("contains all 12 dataset source citations", () => {
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
      "wage-stagnation",
      "inheritance-tax",
    ]
    for (const name of expectedDatasets) {
      expect(wrapper.text()).toContain(name)
    }
  })

  it("cites the HBAI tables, AHC period, table pack and access date for child poverty", () => {
    const wrapper = mountWithRouter()
    const card = wrapper
      .findAll(".source-card")
      .find((entry) => entry.text().includes("child-poverty"))!
    expect(card.text()).toContain(
      "DWP Households Below Average Income (HBAI), tables 4.16ts and 4.17ts",
    )
    expect(card.text()).toContain("after housing costs")
    expect(card.text()).toContain("2021/22 to 2023/24 (three-year average)")
    expect(card.text()).toContain("2026-10-22")
    expect(card.find("a").attributes("href")).toBe(
      "https://assets.publishing.service.gov.uk/media/6836dae29411f0341f323689/HBAI_2324_ods_table_pack.zip",
    )
    expect(card.text()).not.toContain("Children in Low Income Families")
    expect(card.text()).not.toContain("2026-05-16")
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
