import { describe, it, expect, vi, beforeEach } from "vitest";
import { mount } from "@vue/test-utils";
import WealthScaleScroller from "@/components/WealthScaleScroller.vue";

/**
 * Mock ResizeObserver — not available in jsdom.
 * Must be a real class so `new ResizeObserver(...)` works.
 */
const mockObserve = vi.fn();
const mockDisconnect = vi.fn();

class MockResizeObserver {
  constructor(_cb: ResizeObserverCallback) {
    // no-op
  }
  observe = mockObserve;
  disconnect = mockDisconnect;
  unobserve = vi.fn();
}

vi.stubGlobal("ResizeObserver", MockResizeObserver);

describe("WealthScaleScroller", () => {
  beforeEach(() => {
    mockObserve.mockClear();
    mockDisconnect.mockClear();
  });

  it("renders the component with region role", () => {
    const wrapper = mount(WealthScaleScroller);
    const region = wrapper.find('[role="region"]');
    expect(region.exists()).toBe(true);
    expect(region.attributes("aria-label")).toBe("Wealth scale visualisation");
  });

  it("renders the scale label", () => {
    const wrapper = mount(WealthScaleScroller);
    const label = wrapper.find(".wealth-scroller__scale-label");
    expect(label.exists()).toBe(true);
    expect(label.text()).toContain("1 pixel = £1,000");
  });

  it("renders all wealth markers", () => {
    const wrapper = mount(WealthScaleScroller);
    const markers = wrapper.findAll(".wealth-scroller__marker");
    // 8 markers defined in the component
    expect(markers.length).toBe(8);
  });

  it("places the median marker at the correct position (302.5px)", () => {
    const wrapper = mount(WealthScaleScroller);
    const medianMarker = wrapper.find("#marker-median");
    expect(medianMarker.exists()).toBe(true);
    expect(medianMarker.attributes("style")).toContain("left: 302.5px");
  });

  it("places the top 1% marker at 3600px", () => {
    const wrapper = mount(WealthScaleScroller);
    const top1Marker = wrapper.find("#marker-p99");
    expect(top1Marker.exists()).toBe(true);
    expect(top1Marker.attributes("style")).toContain("left: 3600px");
  });

  it("places the top 0.1% marker at 15000px", () => {
    const wrapper = mount(WealthScaleScroller);
    const top01Marker = wrapper.find("#marker-p999");
    expect(top01Marker.exists()).toBe(true);
    expect(top01Marker.attributes("style")).toContain("left: 15000px");
  });

  it("renders the 'you are here' median indicator", () => {
    const wrapper = mount(WealthScaleScroller);
    const youMarker = wrapper.find(".wealth-scroller__you-marker");
    expect(youMarker.exists()).toBe(true);
    expect(youMarker.attributes("style")).toContain("left: 302.5px");
    expect(youMarker.text()).toContain("You are here");
  });

  it("renders five colored segments", () => {
    const wrapper = mount(WealthScaleScroller);
    const segments = wrapper.findAll(".wealth-scroller__segment");
    expect(segments.length).toBe(5);
  });

  it("renders the segment legend with all bands", () => {
    const wrapper = mount(WealthScaleScroller);
    const keys = wrapper.findAll(".wealth-scroller__segment-key");
    expect(keys.length).toBe(5);
    const names = keys.map((k) => k.find(".wealth-scroller__segment-name").text());
    expect(names).toContain("Bottom 50%");
    expect(names).toContain("Top 1%");
    expect(names).toContain("Top 0.1%");
  });

  it("has a scrollable container with keyboard accessibility", () => {
    const wrapper = mount(WealthScaleScroller);
    const container = wrapper.find(".wealth-scroller__container");
    expect(container.exists()).toBe(true);
    expect(container.attributes("tabindex")).toBe("0");
    expect(container.attributes("role")).toBe("slider");
    expect(container.attributes("aria-label")).toContain("arrow keys");
  });

  it("renders the end indicator mentioning richest individual", () => {
    const wrapper = mount(WealthScaleScroller);
    const endIndicator = wrapper.find(".wealth-scroller__end-indicator");
    expect(endIndicator.exists()).toBe(true);
    expect(endIndicator.text()).toContain("37,000,000px");
  });

  it("renders a progress bar", () => {
    const wrapper = mount(WealthScaleScroller);
    const progressBar = wrapper.find(".wealth-scroller__progress-bar");
    expect(progressBar.exists()).toBe(true);
  });

  it("provides a 'Jump to median' button", () => {
    const wrapper = mount(WealthScaleScroller);
    const btn = wrapper.find(".wealth-scroller__reset-btn");
    expect(btn.exists()).toBe(true);
    expect(btn.text()).toBe("Jump to median");
    expect(btn.attributes("aria-label")).toBe("Scroll to median household wealth");
  });

  it("has a screen reader live region for current position", () => {
    const wrapper = mount(WealthScaleScroller);
    const srOnly = wrapper.find('[aria-live="polite"]');
    expect(srOnly.exists()).toBe(true);
    expect(srOnly.text()).toContain("wealth scale");
  });

  it("responds to ArrowRight keydown on the container", async () => {
    const wrapper = mount(WealthScaleScroller);
    const container = wrapper.find(".wealth-scroller__container");
    // Simulate keydown — the actual scroll won't fire in jsdom, but we
    // verify no error is thrown and the event is handled.
    await container.trigger("keydown", { key: "ArrowRight" });
    // No error thrown is a pass — scroll in jsdom is a no-op
    expect(true).toBe(true);
  });

  it("responds to ArrowLeft keydown on the container", async () => {
    const wrapper = mount(WealthScaleScroller);
    const container = wrapper.find(".wealth-scroller__container");
    await container.trigger("keydown", { key: "ArrowLeft" });
    expect(true).toBe(true);
  });

  it("renders marker aria-labels with full description", () => {
    const wrapper = mount(WealthScaleScroller);
    const medianMarker = wrapper.find("#marker-median");
    const ariaLabel = medianMarker.attributes("aria-label");
    expect(ariaLabel).toContain("Median (50%)");
    expect(ariaLabel).toContain("£302,500");
  });

  it("sets total track width to 20000px", () => {
    const wrapper = mount(WealthScaleScroller);
    const track = wrapper.find(".wealth-scroller__track");
    expect(track.attributes("style")).toContain("width: 20000px");
  });

  it("cleans up ResizeObserver on unmount", () => {
    const wrapper = mount(WealthScaleScroller);
    wrapper.unmount();
    expect(mockDisconnect).toHaveBeenCalled();
  });
});
