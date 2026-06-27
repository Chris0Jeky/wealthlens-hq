import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import { mount } from "@vue/test-utils"
import CopyButton from "@/components/CopyButton.vue"

describe("CopyButton", () => {
  let originalClipboard: Clipboard

  beforeEach(() => {
    vi.useFakeTimers()
    originalClipboard = navigator.clipboard
    Object.defineProperty(navigator, "clipboard", {
      value: { writeText: vi.fn().mockResolvedValue(undefined) },
      configurable: true,
      writable: true,
    })
  })

  afterEach(() => {
    Object.defineProperty(navigator, "clipboard", {
      value: originalClipboard,
      configurable: true,
      writable: true,
    })
    vi.useRealTimers()
  })

  it("renders a button", () => {
    const wrapper = mount(CopyButton, { props: { text: "hello" } })
    expect(wrapper.find("button").exists()).toBe(true)
  })

  it("has default aria-label", () => {
    const wrapper = mount(CopyButton, { props: { text: "test" } })
    expect(wrapper.find("button").attributes("aria-label")).toBe("Copy to clipboard")
  })

  it("accepts custom label", () => {
    const wrapper = mount(CopyButton, {
      props: { text: "x", label: "Copy URL" },
    })
    expect(wrapper.find("button").attributes("aria-label")).toBe("Copy URL")
  })

  it('shows "Copy" text initially', () => {
    const wrapper = mount(CopyButton, { props: { text: "data" } })
    expect(wrapper.text()).toContain("Copy")
  })

  it('shows "Copied!" after click', async () => {
    const wrapper = mount(CopyButton, { props: { text: "data" } })
    await wrapper.find("button").trigger("click")
    await Promise.resolve()
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain("Copied!")
  })

  it("copies the text prop to clipboard", async () => {
    const wrapper = mount(CopyButton, { props: { text: "copy me" } })
    await wrapper.find("button").trigger("click")
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith("copy me")
  })

  it("resets after 2 seconds", async () => {
    const wrapper = mount(CopyButton, { props: { text: "temp" } })
    await wrapper.find("button").trigger("click")
    await Promise.resolve()
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain("Copied!")
    vi.advanceTimersByTime(2000)
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain("Copy")
  })

  it("updates aria-label to copied state", async () => {
    const wrapper = mount(CopyButton, { props: { text: "x" } })
    await wrapper.find("button").trigger("click")
    await Promise.resolve()
    await wrapper.vm.$nextTick()
    expect(wrapper.find("button").attributes("aria-label")).toBe("Copied to clipboard")
  })

  it("announces copied state via live region", async () => {
    const wrapper = mount(CopyButton, { props: { text: "x" } })
    await wrapper.find("button").trigger("click")
    await Promise.resolve()
    await wrapper.vm.$nextTick()
    const status = wrapper.find('[role="status"]')
    expect(status.text()).toContain("Copied!")
  })

  it("does nothing when clipboard API is unavailable", async () => {
    Object.defineProperty(navigator, "clipboard", {
      value: undefined,
      configurable: true,
      writable: true,
    })
    const wrapper = mount(CopyButton, { props: { text: "x" } })
    await wrapper.find("button").trigger("click")
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain("Copy")
    const status = wrapper.find('[role="status"]')
    expect(status.text()).toBe("")
  })

  it("shows error state when writeText rejects", async () => {
    ;(navigator.clipboard.writeText as ReturnType<typeof vi.fn>).mockRejectedValueOnce(
      new Error("denied"),
    )
    const wrapper = mount(CopyButton, { props: { text: "x" } })
    await wrapper.find("button").trigger("click")
    await Promise.resolve()
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).not.toContain("Copied!")
    const status = wrapper.find('[role="status"]')
    expect(status.text()).toContain("Copy failed")
  })
})
