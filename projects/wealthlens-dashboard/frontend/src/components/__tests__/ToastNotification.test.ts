import { describe, it, expect, vi, beforeEach } from "vitest"
import { mount } from "@vue/test-utils"
import ToastNotification from "@/components/ToastNotification.vue"

describe("ToastNotification", () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  it("renders message text", () => {
    const wrapper = mount(ToastNotification, {
      props: { message: "Data loaded", durationMs: 0 },
    })
    expect(wrapper.text()).toContain("Data loaded")
  })

  it('has role="alert" for screen readers', () => {
    const wrapper = mount(ToastNotification, {
      props: { message: "Alert", durationMs: 0 },
    })
    expect(wrapper.find('[role="alert"]').exists()).toBe(true)
  })

  it("auto-dismisses after duration", async () => {
    const wrapper = mount(ToastNotification, {
      props: { message: "Temp", durationMs: 3000 },
    })
    expect(wrapper.find('[role="alert"]').exists()).toBe(true)

    vi.advanceTimersByTime(3000)
    await wrapper.vm.$nextTick()
    expect(wrapper.find('[role="alert"]').exists()).toBe(false)
    expect(wrapper.emitted("dismiss")).toHaveLength(1)
  })

  it("dismisses on button click", async () => {
    const wrapper = mount(ToastNotification, {
      props: { message: "Click me", durationMs: 0 },
    })
    await wrapper.find("button").trigger("click")
    expect(wrapper.find('[role="alert"]').exists()).toBe(false)
    expect(wrapper.emitted("dismiss")).toHaveLength(1)
  })

  it("applies info styles by default", () => {
    const wrapper = mount(ToastNotification, {
      props: { message: "Info", durationMs: 0 },
    })
    const alert = wrapper.find('[role="alert"]')
    expect(alert.classes()).toContain("bg-blue-50")
  })

  it("applies error styles", () => {
    const wrapper = mount(ToastNotification, {
      props: { message: "Error", type: "error", durationMs: 0 },
    })
    const alert = wrapper.find('[role="alert"]')
    expect(alert.classes()).toContain("bg-red-50")
  })

  it("applies success styles", () => {
    const wrapper = mount(ToastNotification, {
      props: { message: "Done", type: "success", durationMs: 0 },
    })
    const alert = wrapper.find('[role="alert"]')
    expect(alert.classes()).toContain("bg-green-50")
  })

  it("dismiss button has accessible label", () => {
    const wrapper = mount(ToastNotification, {
      props: { message: "Test", durationMs: 0 },
    })
    expect(wrapper.find("button").attributes("aria-label")).toBe("Dismiss notification")
  })
})
