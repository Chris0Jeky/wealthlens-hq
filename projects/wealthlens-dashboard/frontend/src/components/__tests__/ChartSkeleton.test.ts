import { describe, it, expect } from "vitest"
import { mount } from "@vue/test-utils"
import ChartSkeleton from "@/components/ChartSkeleton.vue"

describe("ChartSkeleton", () => {
  it("renders with default 7 bars", () => {
    const wrapper = mount(ChartSkeleton)
    const barsContainer = wrapper.find(".flex.items-end")
    expect(barsContainer.element.children).toHaveLength(7)
  })

  it("renders custom number of bars", () => {
    const wrapper = mount(ChartSkeleton, { props: { bars: 4 } })
    const barsContainer = wrapper.find(".flex.items-end")
    expect(barsContainer.element.children).toHaveLength(4)
  })

  it("clamps bars to minimum 1 when zero given", () => {
    const wrapper = mount(ChartSkeleton, { props: { bars: 0 } })
    const barsContainer = wrapper.find(".flex.items-end")
    expect(barsContainer.element.children).toHaveLength(1)
  })

  it("has accessible role=status", () => {
    const wrapper = mount(ChartSkeleton)
    const container = wrapper.find('[role="status"]')
    expect(container.exists()).toBe(true)
  })

  it("has sr-only loading text", () => {
    const wrapper = mount(ChartSkeleton)
    const srOnly = wrapper.find(".sr-only")
    expect(srOnly.text()).toContain("Loading")
  })

  it("uses motion-safe animation class", () => {
    const wrapper = mount(ChartSkeleton)
    expect(wrapper.find(".motion-safe\\:animate-pulse").exists()).toBe(true)
  })
})
