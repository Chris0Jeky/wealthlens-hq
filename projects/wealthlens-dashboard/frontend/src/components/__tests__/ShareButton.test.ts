import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { mount } from "@vue/test-utils";
import ShareButton from "@/components/ShareButton.vue";

describe("ShareButton", () => {
  beforeEach(() => {
    // Mock the Clipboard API
    Object.assign(navigator, {
      clipboard: {
        writeText: vi.fn().mockResolvedValue(undefined),
      },
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.useRealTimers();
  });

  it('renders "Copy link" text by default', () => {
    const wrapper = mount(ShareButton);
    expect(wrapper.text()).toContain("Copy link");
  });

  it("has correct aria-label", () => {
    const wrapper = mount(ShareButton);
    const button = wrapper.find("button");
    expect(button.attributes("aria-label")).toBe(
      "Copy chart URL to clipboard",
    );
  });

  it("calls navigator.clipboard.writeText on click", async () => {
    const wrapper = mount(ShareButton);
    await wrapper.find("button").trigger("click");

    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
      window.location.href,
    );
  });

  it('shows "Copied!" after click and reverts after timeout', async () => {
    vi.useFakeTimers();

    const wrapper = mount(ShareButton);
    await wrapper.find("button").trigger("click");

    // Wait for the async clipboard call to resolve
    await vi.runAllTicksAsync();

    expect(wrapper.text()).toContain("Copied!");

    // Advance time by 2 seconds
    vi.advanceTimersByTime(2000);
    await vi.runAllTicksAsync();

    expect(wrapper.text()).toContain("Copy link");
  });
});
