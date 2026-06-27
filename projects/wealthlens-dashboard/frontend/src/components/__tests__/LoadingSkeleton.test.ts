import { describe, it, expect } from "vitest"
import { mount } from "@vue/test-utils"
import LoadingSkeleton from "@/components/LoadingSkeleton.vue"

describe("LoadingSkeleton", () => {
  it("renders with role='status' and aria-label", () => {
    const wrapper = mount(LoadingSkeleton)
    expect(wrapper.attributes("role")).toBe("status")
    expect(wrapper.attributes("aria-label")).toBe("Loading content")
  })

  it("defaults to the chart variant", () => {
    const wrapper = mount(LoadingSkeleton)
    // Chart variant has the tall flex container with items-end
    const chartBars = wrapper.find(".items-end")
    expect(chartBars.exists()).toBe(true)
  })

  it("renders card variant when prop is set", () => {
    const wrapper = mount(LoadingSkeleton, { props: { variant: "card" } })
    // Card variant should NOT have the chart bars container
    const chartBars = wrapper.find(".items-end")
    expect(chartBars.exists()).toBe(false)
    // Card variant has a title-width element (w-2/3)
    const titleLine = wrapper.find(".w-2\\/3")
    expect(titleLine.exists()).toBe(true)
  })

  it("includes sr-only loading text for screen readers", () => {
    const wrapper = mount(LoadingSkeleton)
    const srOnly = wrapper.find(".sr-only")
    expect(srOnly.exists()).toBe(true)
    expect(srOnly.text()).toBe("Loading...")
  })

  it("uses animate-pulse class for animation", () => {
    const wrapper = mount(LoadingSkeleton)
    expect(wrapper.classes()).toContain("animate-pulse")
  })
})
