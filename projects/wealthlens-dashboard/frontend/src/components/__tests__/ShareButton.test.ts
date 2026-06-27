import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import { mount, flushPromises } from "@vue/test-utils"
import ShareButton from "@/components/ShareButton.vue"

describe("ShareButton", () => {
  let originalClipboard: unknown

  beforeEach(() => {
    originalClipboard = navigator.clipboard
    Object.defineProperty(navigator, "clipboard", {
      value: { writeText: vi.fn().mockResolvedValue(undefined) },
      writable: true,
      configurable: true,
    })
  })

  afterEach(() => {
    Object.defineProperty(navigator, "clipboard", {
      value: originalClipboard,
      writable: true,
      configurable: true,
    })
    vi.restoreAllMocks()
    vi.useRealTimers()
  })

  it('renders "Copy link" text by default', () => {
    const wrapper = mount(ShareButton)
    expect(wrapper.text()).toContain("Copy link")
  })

  it("has correct aria-label", () => {
    const wrapper = mount(ShareButton)
    const button = wrapper.find("button")
    expect(button.attributes("aria-label")).toBe("Copy chart URL to clipboard")
  })

  it("calls navigator.clipboard.writeText on click", async () => {
    const wrapper = mount(ShareButton)
    await wrapper.find("button").trigger("click")

    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(window.location.href)
  })

  it('shows "Copied!" after click and reverts after timeout', async () => {
    vi.useFakeTimers()

    const wrapper = mount(ShareButton)
    await wrapper.find("button").trigger("click")
    await flushPromises()

    expect(wrapper.text()).toContain("Copied!")

    vi.advanceTimersByTime(2000)
    await flushPromises()

    expect(wrapper.text()).toContain("Copy link")
  })

  it("clears timeout on unmount without errors", async () => {
    vi.useFakeTimers()

    const wrapper = mount(ShareButton)
    await wrapper.find("button").trigger("click")
    await flushPromises()

    wrapper.unmount()
    vi.advanceTimersByTime(2000)
  })
})
