import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import { mount } from "@vue/test-utils"

vi.mock("@/constants/urls", () => ({
  CHARTS_BASE_URL: "https://chris0jeky.github.io/wealthlens-hq/charts",
  SITE_BASE_URL: "https://chris0jeky.github.io/wealthlens-hq",
}))

import ShareBar from "@/components/ShareBar.vue"

function mountBar() {
  return mount(ShareBar, {
    props: {
      chartName: "wealth-shares",
      chartTitle: "Who owns wealth in the UK?",
      chartId: "WL-W-001",
    },
  })
}

describe("ShareBar (F7 — every control is real)", () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.restoreAllMocks()
    vi.unstubAllGlobals()
  })

  it("copies the chart link to the clipboard with feedback", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined)
    vi.stubGlobal("navigator", { clipboard: { writeText } })

    const wrapper = mountBar()
    await wrapper.find('button[aria-label="Copy link to chart"]').trigger("click")
    await vi.waitFor(() => expect(wrapper.text()).toContain("Copied!"))

    expect(writeText).toHaveBeenCalledWith(
      "https://chris0jeky.github.io/wealthlens-hq/charts/wealth-shares",
    )
  })

  it("copies the embed snippet (iframe + resize script) via the Embed button", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined)
    vi.stubGlobal("navigator", { clipboard: { writeText } })

    const wrapper = mountBar()
    await wrapper.find('button[aria-label="Copy embed code"]').trigger("click")
    await vi.waitFor(() => expect(writeText).toHaveBeenCalled())

    const snippet = writeText.mock.calls[0][0] as string
    expect(snippet).toContain("/embed/wealth-shares")
    expect(snippet).toContain("<iframe")
    expect(snippet).toContain("wealthlens-embed")
  })

  it("shows an error state when the clipboard is unavailable", async () => {
    vi.stubGlobal("navigator", {})
    const wrapper = mountBar()
    await wrapper.find('button[aria-label="Copy link to chart"]').trigger("click")
    expect(wrapper.text()).toContain("Copy failed")
  })

  it("emits export events for PNG and SVG", async () => {
    const wrapper = mountBar()
    await wrapper.find('button[aria-label="Download PNG"]').trigger("click")
    await wrapper.find('button[aria-label="Download SVG"]').trigger("click")
    expect(wrapper.emitted("export")).toEqual([["png"], ["svg"]])
  })

  it("links CSV at the static data mirror", () => {
    const wrapper = mountBar()
    const csv = wrapper.find("a[download]")
    expect(csv.attributes("href")).toBe("/data/wealth-shares.csv")
  })

  it("hides the CSV link for the NC-ND dataset (ACTION-REQUIRED #10)", () => {
    const wrapper = mount(ShareBar, {
      props: { chartName: "generational-wealth", chartTitle: "The wealth ladder" },
    })
    expect(wrapper.find("a[download]").exists()).toBe(false)
  })

  it("opens share intents for Bluesky, LinkedIn, and X", async () => {
    const openSpy = vi.spyOn(window, "open").mockReturnValue({} as Window)
    const wrapper = mountBar()

    await wrapper.find('button[aria-label="Share on Bluesky"]').trigger("click")
    await wrapper.find('button[aria-label="Share on LinkedIn"]').trigger("click")
    await wrapper.find('button[aria-label="Share on X"]').trigger("click")

    const urls = openSpy.mock.calls.map((c) => c[0] as string)
    expect(urls[0]).toContain("bsky.app/intent/compose")
    expect(urls[1]).toContain("linkedin.com/sharing/share-offsite")
    expect(urls[2]).toContain("twitter.com/intent/tweet")
    for (const call of openSpy.mock.calls) {
      expect(call[2]).toBe("noopener,noreferrer")
    }
  })

  it("announces copy results in a live region", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined)
    vi.stubGlobal("navigator", { clipboard: { writeText } })

    const wrapper = mountBar()
    await wrapper.find('button[aria-label="Copy link to chart"]').trigger("click")
    await vi.waitFor(() =>
      expect(wrapper.find('[role="status"]').text()).toContain("Chart link copied"),
    )
  })
})
