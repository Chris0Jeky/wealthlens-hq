import { describe, it, expect, vi, beforeEach } from "vitest"
import { mount } from "@vue/test-utils"
import WealthScaleScroller from "@/components/WealthScaleScroller.vue"

/**
 * Mock ResizeObserver — not available in jsdom.
 * Must be a real class so `new ResizeObserver(...)` works.
 */
const mockObserve = vi.fn()
const mockDisconnect = vi.fn()

class MockResizeObserver {
  constructor() {
    // no-op
  }
  observe = mockObserve
  disconnect = mockDisconnect
  unobserve = vi.fn()
}

vi.stubGlobal("ResizeObserver", MockResizeObserver)

describe("WealthScaleScroller", () => {
  beforeEach(() => {
    mockObserve.mockClear()
    mockDisconnect.mockClear()
  })

  it("renders the component with region role", () => {
    const wrapper = mount(WealthScaleScroller)
    const region = wrapper.find('[role="region"]')
    expect(region.exists()).toBe(true)
    expect(region.attributes("aria-label")).toBe("Wealth scale visualisation")
  })

  it("renders the scale label", () => {
    const wrapper = mount(WealthScaleScroller)
    const label = wrapper.find(".wealth-scroller__scale-label")
    expect(label.exists()).toBe(true)
    expect(label.text()).toContain("1 pixel = £1,000")
  })

  it("renders all wealth markers", () => {
    const wrapper = mount(WealthScaleScroller)
    const markers = wrapper.findAll(".wealth-scroller__marker")
    // 8 markers defined in the component
    expect(markers.length).toBe(8)
  })

  it("places the median marker at the correct position (302.5px)", () => {
    const wrapper = mount(WealthScaleScroller)
    const medianMarker = wrapper.find("#marker-median")
    expect(medianMarker.exists()).toBe(true)
    expect(medianMarker.attributes("style")).toContain("left: 302.5px")
  })

  it("places the top 1% marker at 3600px", () => {
    const wrapper = mount(WealthScaleScroller)
    const top1Marker = wrapper.find("#marker-p99")
    expect(top1Marker.exists()).toBe(true)
    expect(top1Marker.attributes("style")).toContain("left: 3600px")
  })

  it("places the top 0.1% marker at 15000px", () => {
    const wrapper = mount(WealthScaleScroller)
    const top01Marker = wrapper.find("#marker-p999")
    expect(top01Marker.exists()).toBe(true)
    expect(top01Marker.attributes("style")).toContain("left: 15000px")
  })

  it("renders the 'you are here' median indicator", () => {
    const wrapper = mount(WealthScaleScroller)
    const youMarker = wrapper.find(".wealth-scroller__you-marker")
    expect(youMarker.exists()).toBe(true)
    expect(youMarker.attributes("style")).toContain("left: 302.5px")
    expect(youMarker.text()).toContain("You are here")
  })

  it("renders five colored segments", () => {
    const wrapper = mount(WealthScaleScroller)
    const segments = wrapper.findAll(".wealth-scroller__segment")
    expect(segments.length).toBe(5)
  })

  it("renders the segment legend with all bands", () => {
    const wrapper = mount(WealthScaleScroller)
    const keys = wrapper.findAll(".wealth-scroller__segment-key")
    expect(keys.length).toBe(5)
    const names = keys.map((k) => k.find(".wealth-scroller__segment-name").text())
    expect(names).toContain("Bottom 50%")
    expect(names).toContain("Top 1%")
    expect(names).toContain("Top 0.1%")
  })

  it("has a scrollable region with keyboard accessibility", () => {
    const wrapper = mount(WealthScaleScroller)
    const container = wrapper.find(".wealth-scroller__container")
    expect(container.exists()).toBe(true)
    expect(container.attributes("tabindex")).toBe("0")
    expect(container.attributes("role")).toBe("region")
    expect(container.attributes("aria-labelledby")).toBe("wealth-scale-scroll-heading")
    expect(container.attributes("aria-describedby")).toContain("wealth-scale-scroll-instructions")
    expect(container.attributes("aria-describedby")).toContain("wealth-scale-current-position")
  })

  it("does not expose the rich marker track as a slider", () => {
    const wrapper = mount(WealthScaleScroller)
    expect(wrapper.find('[role="slider"]').exists()).toBe(false)
    const container = wrapper.find(".wealth-scroller__container")
    expect(container.attributes("aria-valuenow")).toBeUndefined()
    expect(container.attributes("aria-valuemin")).toBeUndefined()
    expect(container.attributes("aria-valuemax")).toBeUndefined()
  })

  it("keeps marker labels and values exposed inside the scrollable region", () => {
    const wrapper = mount(WealthScaleScroller)
    const container = wrapper.find(".wealth-scroller__container")
    expect(container.text()).toContain("Median (50%)")
    expect(container.text()).toContain("£303k")
    expect(container.text()).toContain("Top 0.1%")
  })

  it("renders the end indicator mentioning richest individual", () => {
    const wrapper = mount(WealthScaleScroller)
    const endIndicator = wrapper.find(".wealth-scroller__end-indicator")
    expect(endIndicator.exists()).toBe(true)
    expect(endIndicator.text()).toContain("37,000,000px")
  })

  it("renders a progress bar", () => {
    const wrapper = mount(WealthScaleScroller)
    const progressBar = wrapper.find(".wealth-scroller__progress-bar")
    expect(progressBar.exists()).toBe(true)
  })

  it("provides a 'Jump to median' button", () => {
    const wrapper = mount(WealthScaleScroller)
    const btn = wrapper.find(".wealth-scroller__reset-btn")
    expect(btn.exists()).toBe(true)
    expect(btn.text()).toBe("Jump to median")
    expect(btn.attributes("aria-label")).toBe("Scroll to median household wealth")
  })

  it("has a screen reader live region for current position", () => {
    const wrapper = mount(WealthScaleScroller)
    const srOnly = wrapper.find('[aria-live="polite"]')
    expect(srOnly.exists()).toBe(true)
    expect(srOnly.text()).toContain("wealth scale")
  })

  // jsdom does no layout, so the actual scrollLeft mutation is unobservable.
  // Assert the meaningful, deterministic contract instead: the handler claims
  // each arrow/Home/End key by calling event.preventDefault() (so the page does
  // not also scroll), and leaves unrelated keys alone. Dispatch a real,
  // cancelable KeyboardEvent and read event.defaultPrevented.
  it.each(["ArrowRight", "ArrowLeft", "Home", "End"])(
    "calls preventDefault for the handled key %s",
    (key) => {
      const wrapper = mount(WealthScaleScroller)
      const el = wrapper.find(".wealth-scroller__container").element
      const event = new KeyboardEvent("keydown", {
        key,
        cancelable: true,
        bubbles: true,
      })
      el.dispatchEvent(event)
      expect(event.defaultPrevented, `${key} should be handled`).toBe(true)
    },
  )

  it("does NOT preventDefault for an unrelated key (e.g. Tab)", () => {
    const wrapper = mount(WealthScaleScroller)
    const el = wrapper.find(".wealth-scroller__container").element
    const event = new KeyboardEvent("keydown", {
      key: "Tab",
      cancelable: true,
      bubbles: true,
    })
    el.dispatchEvent(event)
    // Tab must remain available for keyboard navigation — the handler ignores it.
    expect(event.defaultPrevented).toBe(false)
  })

  it("renders marker aria-labels with full description", () => {
    const wrapper = mount(WealthScaleScroller)
    const medianMarker = wrapper.find("#marker-median")
    const ariaLabel = medianMarker.attributes("aria-label")
    expect(ariaLabel).toContain("Median (50%)")
    expect(ariaLabel).toContain("£302,500")
  })

  it("sets total track width to 20000px", () => {
    const wrapper = mount(WealthScaleScroller)
    const track = wrapper.find(".wealth-scroller__track")
    expect(track.attributes("style")).toContain("width: 20000px")
  })

  it("cleans up ResizeObserver on unmount", () => {
    const wrapper = mount(WealthScaleScroller)
    wrapper.unmount()
    expect(mockDisconnect).toHaveBeenCalled()
  })

  it("percentile markers stay consistent with the wealth calculator (no drift)", () => {
    // The scroller derives its percentile markers from utils/wealthPosition (the same
    // ONS WAS Round 7 figures the calculator uses), so the two surfaces cannot
    // contradict each other. Assert the corrected figures, not the old hardcoded ones
    // that were impossible against the decile boundaries. The precise figures live in
    // the marker aria-labels (annotations); the visible chips use rounded formatGBP.
    const html = mount(WealthScaleScroller).html()
    // Precise annotation figures (aria-labels):
    expect(html).toContain("£82,400") // P25 = decile-3 median (was £118,600, above the P30 boundary)
    expect(html).toContain("£829,950") // P75 = decile-8 median (was £611,200, below the P70 boundary)
    expect(html).toContain("£1.48m") // Top 10% threshold, matching the calculator (was £1.34m)
    // Rounded visible chips:
    expect(html).toContain("£82k")
    expect(html).toContain("£830k")
    // The contradicting old values must never reappear (annotation or chip).
    expect(html).not.toContain("£118,600")
    expect(html).not.toContain("£611,200")
    expect(html).not.toContain("£1.34m")
    expect(html).not.toContain("£119k") // old P25 chip
    expect(html).not.toContain("£611k") // old P75 chip
  })
})
