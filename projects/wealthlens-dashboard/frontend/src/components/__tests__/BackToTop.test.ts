import { describe, it, expect, vi, beforeEach } from "vitest"
import { mount } from "@vue/test-utils"
import BackToTop from "@/components/BackToTop.vue"

describe("BackToTop", () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    Object.defineProperty(window, "scrollY", { value: 0, writable: true })
    window.scrollTo = vi.fn()
  })

  it("is hidden when scrollY is below threshold", () => {
    const wrapper = mount(BackToTop)
    expect(wrapper.find("button").exists()).toBe(false)
  })

  it("shows button when scrolled past threshold", async () => {
    const wrapper = mount(BackToTop)
    Object.defineProperty(window, "scrollY", { value: 400, writable: true })
    window.dispatchEvent(new Event("scroll"))
    await wrapper.vm.$nextTick()
    expect(wrapper.find("button").exists()).toBe(true)
  })

  it("has accessible label", async () => {
    const wrapper = mount(BackToTop)
    Object.defineProperty(window, "scrollY", { value: 400, writable: true })
    window.dispatchEvent(new Event("scroll"))
    await wrapper.vm.$nextTick()
    expect(wrapper.find("button").attributes("aria-label")).toBe("Scroll to top")
  })

  it("calls scrollTo on click", async () => {
    const wrapper = mount(BackToTop)
    Object.defineProperty(window, "scrollY", { value: 400, writable: true })
    window.dispatchEvent(new Event("scroll"))
    await wrapper.vm.$nextTick()
    await wrapper.find("button").trigger("click")
    expect(window.scrollTo).toHaveBeenCalledWith({ top: 0, behavior: "smooth" })
  })

  it("button has type=button", async () => {
    const wrapper = mount(BackToTop)
    Object.defineProperty(window, "scrollY", { value: 400, writable: true })
    window.dispatchEvent(new Event("scroll"))
    await wrapper.vm.$nextTick()
    expect(wrapper.find("button").attributes("type")).toBe("button")
  })
})
