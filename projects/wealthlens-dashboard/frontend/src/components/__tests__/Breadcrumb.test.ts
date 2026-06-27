import { describe, it, expect } from "vitest"
import { mount } from "@vue/test-utils"
import Breadcrumb from "@/components/Breadcrumb.vue"

const routerLinkStub = {
  template: '<a :href="to"><slot /></a>',
  props: ["to"],
}

describe("Breadcrumb", () => {
  function factory(items: Array<{ label: string; to?: string }>) {
    return mount(Breadcrumb, {
      props: { items },
      global: { stubs: { "router-link": routerLinkStub } },
    })
  }

  it("renders all breadcrumb items", () => {
    const wrapper = factory([
      { label: "Home", to: "/" },
      { label: "Charts", to: "/charts" },
      { label: "Wealth Shares" },
    ])
    expect(wrapper.findAll("li")).toHaveLength(3)
  })

  it('renders links for items with "to" prop', () => {
    const wrapper = factory([{ label: "Home", to: "/" }, { label: "Current" }])
    const links = wrapper.findAll("a")
    expect(links).toHaveLength(1)
    expect(links[0].attributes("href")).toBe("/")
  })

  it("renders span with aria-current for last item without link", () => {
    const wrapper = factory([{ label: "Home", to: "/" }, { label: "Current Page" }])
    const current = wrapper.find('[aria-current="page"]')
    expect(current.exists()).toBe(true)
    expect(current.text()).toBe("Current Page")
  })

  it("has nav with aria-label", () => {
    const wrapper = factory([{ label: "Home" }])
    expect(wrapper.find("nav").attributes("aria-label")).toBe("Breadcrumb")
  })

  it("renders separators between items", () => {
    const wrapper = factory([{ label: "A", to: "/" }, { label: "B", to: "/b" }, { label: "C" }])
    const separators = wrapper.findAll('[aria-hidden="true"]')
    expect(separators).toHaveLength(2)
  })
})
