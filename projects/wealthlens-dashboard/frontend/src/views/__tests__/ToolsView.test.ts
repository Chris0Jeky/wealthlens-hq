import { describe, expect, it } from "vitest"
import { mount } from "@vue/test-utils"
import { createRouter, createMemoryHistory } from "vue-router"
import ToolsView from "../ToolsView.vue"

function mountToolsView() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: "/tools", component: ToolsView }],
  })

  return mount(ToolsView, {
    global: { plugins: [router] },
  })
}

describe("ToolsView", () => {
  it("lists every interactive tool and the FAQ with exact routes", () => {
    const wrapper = mountToolsView()
    const links = wrapper.findAll(".tool-link")

    expect(links).toHaveLength(5)
    expect(links.map((link) => link.attributes("href"))).toEqual([
      "/tools/wealth-scale",
      "/tools/wealth-calculator",
      "/tools/tax-calculator",
      "/tools/wealth-tax-simulator",
      "/faq",
    ])
    expect(wrapper.find("h1").text()).toContain("Explore the numbers yourself")
  })

  it("uses semantic list markup with an accessible label", () => {
    const wrapper = mountToolsView()
    const list = wrapper.find('ul[role="list"]')

    expect(list.exists()).toBe(true)
    expect(list.attributes("aria-label")).toBe("Interactive tools and related help")
    expect(list.findAll("li")).toHaveLength(5)
  })

  it("declares the /tools canonical URL for prerendered metadata", () => {
    const wrapper = mountToolsView()
    expect(document.head.querySelector('link[rel="canonical"]')?.getAttribute("href")).toBe(
      "https://chris0jeky.github.io/wealthlens-hq/tools",
    )
    wrapper.unmount()
  })
})
