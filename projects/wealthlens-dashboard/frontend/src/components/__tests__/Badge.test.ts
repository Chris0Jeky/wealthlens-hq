import { describe, it, expect } from "vitest"
import { mount } from "@vue/test-utils"
import Badge from "@/components/Badge.vue"

describe("Badge", () => {
  it("renders slot content", () => {
    const wrapper = mount(Badge, { slots: { default: "New" } })
    expect(wrapper.text()).toBe("New")
  })

  it("renders as a span element", () => {
    const wrapper = mount(Badge, { slots: { default: "x" } })
    expect(wrapper.element.tagName).toBe("SPAN")
  })

  it("defaults to gray (default) variant", () => {
    const wrapper = mount(Badge, { slots: { default: "x" } })
    expect(wrapper.classes()).toContain("bg-gray-100")
  })

  it("applies success variant", () => {
    const wrapper = mount(Badge, {
      props: { variant: "success" },
      slots: { default: "Active" },
    })
    expect(wrapper.classes()).toContain("bg-green-100")
  })

  it("applies warning variant", () => {
    const wrapper = mount(Badge, {
      props: { variant: "warning" },
      slots: { default: "Stale" },
    })
    expect(wrapper.classes()).toContain("bg-yellow-100")
  })

  it("applies error variant", () => {
    const wrapper = mount(Badge, {
      props: { variant: "error" },
      slots: { default: "Error" },
    })
    expect(wrapper.classes()).toContain("bg-red-100")
  })

  it("applies info variant", () => {
    const wrapper = mount(Badge, {
      props: { variant: "info" },
      slots: { default: "Info" },
    })
    expect(wrapper.classes()).toContain("bg-blue-100")
  })

  it("defaults to md size", () => {
    const wrapper = mount(Badge, { slots: { default: "x" } })
    expect(wrapper.classes()).toContain("text-xs")
  })

  it("applies sm size", () => {
    const wrapper = mount(Badge, {
      props: { size: "sm" },
      slots: { default: "x" },
    })
    expect(wrapper.classes()).toContain("text-[10px]")
  })

  it("has rounded-full pill shape", () => {
    const wrapper = mount(Badge, { slots: { default: "x" } })
    expect(wrapper.classes()).toContain("rounded-full")
  })
})
