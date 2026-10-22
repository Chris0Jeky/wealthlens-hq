import { readFileSync } from "node:fs"
import { resolve } from "node:path"
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import { mount, flushPromises } from "@vue/test-utils"

vi.mock("vue-router", () => ({
  useRoute: () => ({ params: { name: "boe-rates" }, meta: { embed: true } }),
}))

vi.mock("@/config/chartComponents", () => ({
  CHART_COMPONENT_LOADERS: {
    "boe-rates": async () => ({ default: { render: () => null } }),
  },
}))

const { fetchMetadata } = vi.hoisted(() => ({ fetchMetadata: vi.fn() }))
vi.mock("@/stores/data", () => ({ useDataStore: () => ({ fetchMetadata }) }))

import EmbedChartView from "../EmbedChartView.vue"

// Consume the actual generated artifact. An honest mock alone would not catch
// the missing provenance in the committed BoE metadata that caused this issue.
const metadata = JSON.parse(
  readFileSync(
    resolve("public/data/boe-rates-metadata.json"),
    "utf-8",
  ),
)

describe("published BoE provenance", () => {
  beforeEach(() => {
    fetchMetadata.mockReset()
  })

  afterEach(() => {
    document.head.querySelectorAll("[data-wl-meta]").forEach((el) => el.remove())
  })

  it("preserves the disclaimer decision in the actual published metadata", async () => {
    fetchMetadata.mockResolvedValue(metadata)
    const wrapper = mount(EmbedChartView)
    await flushPromises()

    expect(fetchMetadata).toHaveBeenCalledWith("boe-rates")
    expect(["illustrative_fallback", "live_ons"]).toContain(metadata.data_type)
    if (metadata.data_type === "illustrative_fallback") {
      const caveat = wrapper.get('[role="note"]')
      expect(caveat.text()).toContain("Illustrative composite")
      expect(caveat.text()).toContain("not published statistics")
    } else {
      expect(wrapper.find('[role="note"]').exists()).toBe(false)
    }
    wrapper.unmount()
  })

  it("does not label a verified official response as illustrative", async () => {
    fetchMetadata.mockResolvedValue({ ...metadata, data_type: "live_ons" })
    const wrapper = mount(EmbedChartView)
    await flushPromises()

    expect(wrapper.find('[role="note"]').exists()).toBe(false)
    wrapper.unmount()
  })
})
