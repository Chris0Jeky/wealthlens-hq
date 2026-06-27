import { describe, it, expect } from "vitest"
import { mount } from "@vue/test-utils"
import LoadingSpinner from "@/components/LoadingSpinner.vue"

describe("LoadingSpinner", () => {
  it('renders with role="status"', () => {
    const wrapper = mount(LoadingSpinner)
    expect(wrapper.find('[role="status"]').exists()).toBe(true)
  })

  it("has sr-only label defaulting to Loading", () => {
    const wrapper = mount(LoadingSpinner)
    const srOnly = wrapper.find(".sr-only")
    expect(srOnly.text()).toBe("Loading")
  })

  it("accepts custom label", () => {
    const wrapper = mount(LoadingSpinner, { props: { label: "Fetching data" } })
    expect(wrapper.find(".sr-only").text()).toBe("Fetching data")
  })

  it("applies medium size by default", () => {
    const wrapper = mount(LoadingSpinner)
    const spinner = wrapper.find('[aria-hidden="true"]')
    expect(spinner.classes()).toContain("h-8")
    expect(spinner.classes()).toContain("w-8")
  })

  it("applies small size classes", () => {
    const wrapper = mount(LoadingSpinner, { props: { size: "sm" } })
    const spinner = wrapper.find('[aria-hidden="true"]')
    expect(spinner.classes()).toContain("h-4")
    expect(spinner.classes()).toContain("w-4")
  })

  it("applies large size classes", () => {
    const wrapper = mount(LoadingSpinner, { props: { size: "lg" } })
    const spinner = wrapper.find('[aria-hidden="true"]')
    expect(spinner.classes()).toContain("h-12")
    expect(spinner.classes()).toContain("w-12")
  })

  it("uses motion-safe animation", () => {
    const wrapper = mount(LoadingSpinner)
    const spinner = wrapper.find('[aria-hidden="true"]')
    expect(spinner.classes()).toContain("motion-safe:animate-spin")
  })

  it("hides spinner from screen readers", () => {
    const wrapper = mount(LoadingSpinner)
    const spinner = wrapper.find('[aria-hidden="true"]')
    expect(spinner.exists()).toBe(true)
  })
})
