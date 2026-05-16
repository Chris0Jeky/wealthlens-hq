import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { mount, flushPromises } from "@vue/test-utils";

vi.mock("@/constants/urls", () => ({
  CHARTS_BASE_URL: "https://chris0jeky.github.io/wealthlens-hq/charts",
}));

import SharePanel from "@/components/SharePanel.vue";

describe("SharePanel", () => {
  let originalClipboard: unknown;
  let windowOpenSpy: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    vi.useFakeTimers();
    originalClipboard = navigator.clipboard;
    Object.defineProperty(navigator, "clipboard", {
      value: { writeText: vi.fn().mockResolvedValue(undefined) },
      writable: true,
      configurable: true,
    });
    windowOpenSpy = vi.spyOn(window, "open").mockImplementation(() => null);
  });

  afterEach(() => {
    Object.defineProperty(navigator, "clipboard", {
      value: originalClipboard,
      writable: true,
      configurable: true,
    });
    windowOpenSpy.mockRestore();
    vi.useRealTimers();
  });

  const defaultProps = {
    chartName: "wealth-shares",
    chartTitle: "Who owns wealth in the UK?",
  };

  it("renders a heading", () => {
    const wrapper = mount(SharePanel, { props: defaultProps });
    expect(wrapper.text()).toContain("Share this chart");
  });

  it("renders four share buttons (X, LinkedIn, Bluesky, Copy link)", () => {
    const wrapper = mount(SharePanel, { props: defaultProps });
    const buttons = wrapper.findAll("nav button");
    expect(buttons).toHaveLength(4);
  });

  it("has accessible aria-labels on all share buttons", () => {
    const wrapper = mount(SharePanel, { props: defaultProps });
    const buttons = wrapper.findAll("nav button");
    const labels = buttons.map((b) => b.attributes("aria-label"));
    expect(labels).toContain("Share on X (Twitter)");
    expect(labels).toContain("Share on LinkedIn");
    expect(labels).toContain("Share on Bluesky");
    expect(labels).toContain("Copy chart link");
  });

  it("opens Twitter share URL in new window on X button click", async () => {
    const wrapper = mount(SharePanel, { props: defaultProps });
    const xBtn = wrapper.find('button[aria-label="Share on X (Twitter)"]');
    await xBtn.trigger("click");

    expect(windowOpenSpy).toHaveBeenCalledWith(
      expect.stringContaining("https://twitter.com/intent/tweet"),
      "_blank",
      "noopener,noreferrer",
    );
    expect(windowOpenSpy).toHaveBeenCalledWith(
      expect.stringContaining("wealth-shares"),
      "_blank",
      "noopener,noreferrer",
    );
  });

  it("opens LinkedIn share URL on LinkedIn button click", async () => {
    const wrapper = mount(SharePanel, { props: defaultProps });
    const btn = wrapper.find('button[aria-label="Share on LinkedIn"]');
    await btn.trigger("click");

    expect(windowOpenSpy).toHaveBeenCalledWith(
      expect.stringContaining("linkedin.com/sharing/share-offsite"),
      "_blank",
      "noopener,noreferrer",
    );
  });

  it("opens Bluesky share URL on Bluesky button click", async () => {
    const wrapper = mount(SharePanel, { props: defaultProps });
    const btn = wrapper.find('button[aria-label="Share on Bluesky"]');
    await btn.trigger("click");

    expect(windowOpenSpy).toHaveBeenCalledWith(
      expect.stringContaining("bsky.app/intent/compose"),
      "_blank",
      "noopener,noreferrer",
    );
  });

  it("includes chart title in share URLs", async () => {
    const wrapper = mount(SharePanel, { props: defaultProps });
    const xBtn = wrapper.find('button[aria-label="Share on X (Twitter)"]');
    await xBtn.trigger("click");

    expect(windowOpenSpy).toHaveBeenCalledWith(
      expect.stringContaining(
        encodeURIComponent("Who owns wealth in the UK? — WealthLens UK"),
      ),
      "_blank",
      "noopener,noreferrer",
    );
  });

  it("copies chart URL to clipboard on Copy link click", async () => {
    const wrapper = mount(SharePanel, { props: defaultProps });
    const btn = wrapper.find('button[aria-label="Copy chart link"]');
    await btn.trigger("click");
    await flushPromises();

    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
      "https://chris0jeky.github.io/wealthlens-hq/charts/wealth-shares",
    );
  });

  it("shows 'Copied!' feedback after copy", async () => {
    const wrapper = mount(SharePanel, { props: defaultProps });
    const btn = wrapper.find('button[aria-label="Copy chart link"]');
    await btn.trigger("click");
    await flushPromises();

    expect(btn.text()).toContain("Copied!");
  });

  it("reverts copy button after 2 seconds", async () => {
    const wrapper = mount(SharePanel, { props: defaultProps });
    const btn = wrapper.find('button[aria-label="Copy chart link"]');
    await btn.trigger("click");
    await flushPromises();

    expect(btn.text()).toContain("Copied!");

    vi.advanceTimersByTime(2000);
    await flushPromises();

    // Re-query since aria-label changes
    const resetBtn = wrapper.find(
      'button[aria-label="Copy chart link"]',
    );
    expect(resetBtn.text()).toContain("Copy link");
  });

  it("updates aria-label on copy link button after copy", async () => {
    const wrapper = mount(SharePanel, { props: defaultProps });
    const btn = wrapper.find('button[aria-label="Copy chart link"]');
    await btn.trigger("click");
    await flushPromises();

    expect(btn.attributes("aria-label")).toBe(
      "Link copied to clipboard",
    );
  });

  it("announces copy via live region", async () => {
    const wrapper = mount(SharePanel, { props: defaultProps });
    const btn = wrapper.find('button[aria-label="Copy chart link"]');
    await btn.trigger("click");
    await flushPromises();

    const status = wrapper.find('[role="status"]');
    expect(status.text()).toContain("Chart link copied to clipboard");
  });

  it("renders the EmbedCode child component", () => {
    const wrapper = mount(SharePanel, { props: defaultProps });
    expect(wrapper.text()).toContain("Embed this chart");
  });

  it("passes chartName to EmbedCode", () => {
    const wrapper = mount(SharePanel, { props: defaultProps });
    const code = wrapper.find("code");
    expect(code.text()).toContain("wealth-shares");
  });

  it("has section landmark with aria-labelledby", () => {
    const wrapper = mount(SharePanel, { props: defaultProps });
    const section = wrapper.find("section");
    expect(section.attributes("aria-labelledby")).toBe(
      "share-panel-heading",
    );
  });

  it("has navigation landmark with aria-label", () => {
    const wrapper = mount(SharePanel, { props: defaultProps });
    const nav = wrapper.find("nav");
    expect(nav.attributes("aria-label")).toBe("Share options");
  });
});
