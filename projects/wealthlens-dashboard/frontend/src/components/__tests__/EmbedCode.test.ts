import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import { mount, flushPromises } from "@vue/test-utils"

vi.mock("@/constants/urls", () => ({
  CHARTS_BASE_URL: "https://chris0jeky.github.io/wealthlens-hq/charts",
}))

import EmbedCode from "@/components/EmbedCode.vue"

describe("EmbedCode", () => {
  let originalClipboard: unknown

  beforeEach(() => {
    vi.useFakeTimers()
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
    vi.useRealTimers()
  })

  it("renders a heading", () => {
    const wrapper = mount(EmbedCode, {
      props: { chartName: "wealth-shares" },
    })
    expect(wrapper.text()).toContain("Embed this chart")
  })

  it("shows an iframe snippet with correct chart URL", () => {
    const wrapper = mount(EmbedCode, {
      props: { chartName: "wealth-shares" },
    })
    const code = wrapper.find("code")
    expect(code.text()).toContain("https://chris0jeky.github.io/wealthlens-hq/charts/wealth-shares")
    expect(code.text()).toContain("<iframe")
    expect(code.text()).toContain('frameborder="0"')
  })

  it("defaults to 100% width", () => {
    const wrapper = mount(EmbedCode, {
      props: { chartName: "test-chart" },
    })
    const code = wrapper.find("code")
    expect(code.text()).toContain('width="100%"')
  })

  it("changes iframe width when a radio option is selected", async () => {
    const wrapper = mount(EmbedCode, {
      props: { chartName: "test-chart" },
    })
    const radios = wrapper.findAll('input[type="radio"]')
    // Select 600px (first option)
    await radios[0].setValue(true)
    const code = wrapper.find("code")
    expect(code.text()).toContain('width="600"')
  })

  it("renders 800px option correctly", async () => {
    const wrapper = mount(EmbedCode, {
      props: { chartName: "test-chart" },
    })
    const radios = wrapper.findAll('input[type="radio"]')
    // Select 800px (second option)
    await radios[1].setValue(true)
    const code = wrapper.find("code")
    expect(code.text()).toContain('width="800"')
  })

  it("has three width options", () => {
    const wrapper = mount(EmbedCode, {
      props: { chartName: "test-chart" },
    })
    const radios = wrapper.findAll('input[type="radio"]')
    expect(radios).toHaveLength(3)
  })

  it("renders a copy button", () => {
    const wrapper = mount(EmbedCode, {
      props: { chartName: "test-chart" },
    })
    const btn = wrapper.find("button")
    expect(btn.exists()).toBe(true)
    expect(btn.text()).toContain("Copy code")
  })

  it("copies embed snippet to clipboard on click", async () => {
    const wrapper = mount(EmbedCode, {
      props: { chartName: "wealth-shares" },
    })
    await wrapper.find("button").trigger("click")
    await flushPromises()

    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(expect.stringContaining("<iframe"))
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
      expect.stringContaining("wealth-shares"),
    )
  })

  it("shows 'Copied!' feedback after successful copy", async () => {
    const wrapper = mount(EmbedCode, {
      props: { chartName: "test-chart" },
    })
    await wrapper.find("button").trigger("click")
    await flushPromises()

    expect(wrapper.find("button").text()).toContain("Copied!")
  })

  it("reverts to 'Copy code' after 2 seconds", async () => {
    const wrapper = mount(EmbedCode, {
      props: { chartName: "test-chart" },
    })
    await wrapper.find("button").trigger("click")
    await flushPromises()

    expect(wrapper.find("button").text()).toContain("Copied!")

    vi.advanceTimersByTime(2000)
    await flushPromises()

    expect(wrapper.find("button").text()).toContain("Copy code")
  })

  it("updates aria-label on copy", async () => {
    const wrapper = mount(EmbedCode, {
      props: { chartName: "test-chart" },
    })
    expect(wrapper.find("button").attributes("aria-label")).toBe("Copy embed code")

    await wrapper.find("button").trigger("click")
    await flushPromises()

    expect(wrapper.find("button").attributes("aria-label")).toBe("Embed code copied")
  })

  it("announces copy via live region", async () => {
    const wrapper = mount(EmbedCode, {
      props: { chartName: "test-chart" },
    })
    await wrapper.find("button").trigger("click")
    await flushPromises()

    const status = wrapper.find('[role="status"]')
    expect(status.text()).toContain("Embed code copied to clipboard")
  })

  it("includes height=500 in the embed snippet", () => {
    const wrapper = mount(EmbedCode, {
      props: { chartName: "test-chart" },
    })
    const code = wrapper.find("code")
    expect(code.text()).toContain('height="500"')
  })

  it("includes a title attribute in the iframe for accessibility", () => {
    const wrapper = mount(EmbedCode, {
      props: { chartName: "test-chart" },
    })
    const code = wrapper.find("code")
    expect(code.text()).toContain('title="WealthLens UK chart"')
  })
})
