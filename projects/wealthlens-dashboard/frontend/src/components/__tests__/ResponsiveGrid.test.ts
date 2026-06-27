import { describe, it, expect } from "vitest"
import { mount } from "@vue/test-utils"
import ResponsiveGrid from "@/components/ResponsiveGrid.vue"

describe("ResponsiveGrid", () => {
  it("renders a grid container", () => {
    const wrapper = mount(ResponsiveGrid, {
      slots: { default: "<div>A</div><div>B</div>" },
    })
    expect(wrapper.find(".grid").exists()).toBe(true)
  })

  it("applies default minWidth of 280px", () => {
    const wrapper = mount(ResponsiveGrid, {
      slots: { default: "<div>A</div>" },
    })
    expect(wrapper.attributes("style")).toContain("repeat(auto-fill, minmax(280px, 1fr))")
  })

  it("applies default gap of 1.5rem", () => {
    const wrapper = mount(ResponsiveGrid, {
      slots: { default: "<div>A</div>" },
    })
    expect(wrapper.attributes("style")).toContain("gap: 1.5rem")
  })

  it("accepts custom minWidth", () => {
    const wrapper = mount(ResponsiveGrid, {
      props: { minWidth: "320px" },
      slots: { default: "<div>A</div>" },
    })
    expect(wrapper.attributes("style")).toContain("minmax(320px, 1fr)")
  })

  it("accepts custom gap", () => {
    const wrapper = mount(ResponsiveGrid, {
      props: { gap: "2rem" },
      slots: { default: "<div>A</div>" },
    })
    expect(wrapper.attributes("style")).toContain("gap: 2rem")
  })

  it("renders slot content", () => {
    const wrapper = mount(ResponsiveGrid, {
      slots: { default: '<div class="item">Card</div>' },
    })
    expect(wrapper.find(".item").text()).toBe("Card")
  })
})
