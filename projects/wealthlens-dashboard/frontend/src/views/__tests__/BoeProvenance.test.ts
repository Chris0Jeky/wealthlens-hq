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
import { chartConfigs } from "@/config/chartArticles"
import { OG_METADATA } from "@/constants/ogMetadata"

// Consume the actual generated artifact. An honest mock alone would not catch
// the missing provenance in the committed BoE metadata that caused this issue.
const metadata = JSON.parse(readFileSync(resolve("public/data/boe-rates-metadata.json"), "utf-8"))

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

describe("BoE article and embed citations", () => {
  const config = chartConfigs["boe-rates"]
  const rows: { date: string; bank_rate: number; cpi_annual: number }[] = JSON.parse(
    readFileSync(resolve("public/data/boe-rates.json"), "utf-8"),
  ).data

  it("derives every card and the lede from the plotted monthly observations", () => {
    const month = (date: string) => date.slice(0, 7)
    const since2020 = rows.filter((row) => row.date >= "2020-01-01")
    const peak = Math.max(...since2020.map((row) => row.bank_rate))
    const peakRows = since2020.filter((row) => row.bank_rate === peak)
    const lowest = Math.min(...rows.map((row) => row.bank_rate))
    const lowRows = rows.filter((row) => row.bank_rate === lowest)
    const peakCpi = Math.max(...rows.map((row) => row.cpi_annual))
    const peakCpiRow = rows.find((row) => row.cpi_annual === peakCpi)!
    expect(config.stats.map((stat) => stat.value)).toEqual([
      String(peak),
      String(lowest),
      String(peakCpi),
      String(rows.at(-1)!.bank_rate),
    ])
    // Card and lede periods must be the contiguous months the data shows at those values.
    expect([month(peakRows[0].date), month(peakRows.at(-1)!.date)]).toEqual(["2023-09", "2024-07"])
    expect(config.stats[0].label).toBe("Peak Bank Rate (Sep 2023 to Jul 2024)")
    expect(config.stats[0].description).toContain("Monthly average")
    expect([month(lowRows[0].date), month(lowRows.at(-1)!.date)]).toEqual(["2020-04", "2021-11"])
    expect(config.stats[1].label).toBe("Low (Apr 2020 to Nov 2021)")
    expect(month(peakCpiRow.date)).toBe("2022-10")
    const year2000 = rows.filter((row) => row.date.startsWith("2000-"))
    expect(year2000.filter((row) => row.bank_rate === 6).length).toBeGreaterThanOrEqual(10)
    expect(config.lede).toContain(`${peak}% from September 2023`)
    expect(config.lede).toContain(`${lowest}% from April 2020 to November 2021`)
    expect(config.lede).toContain(`${peakCpi}% in October 2022`)
    expect(config.lede).toContain("6% through most of 2000")
  })

  it("names the actual series, monthly-average definition and both official URLs", () => {
    const copy = JSON.stringify({ ...config, related: [] })
    expect(copy).toContain("IUMABEDR")
    expect(copy).toContain("D7G7")
    expect(copy).toContain("MM23")
    expect(copy).not.toMatch(/IUDBEDR|D7BT|step function|2026-05-16|16 May 2026|\u2014/)
    expect(config.source.accessed).toBe(metadata.access_date)
    expect(config.source.links?.map((link) => link.url)).toEqual(
      metadata.sources.map((source: { url: string }) => source.url),
    )
    for (const source of metadata.sources) {
      const url = new URL(source.url)
      expect(config.methodology).toContain(url.hostname)
      expect(config.methodology).toContain(source.series)
    }
    expect(OG_METADATA["boe-rates"].subtitle).toContain("Monthly average")
    expect(OG_METADATA["boe-rates"].source).toContain("IUMABEDR")
    expect(OG_METADATA["boe-rates"].source).toContain("D7G7")
    expect(OG_METADATA["boe-rates"].sourceAccessDate).toBe(metadata.access_date)
  })

  it("renders both source links and the captured access date in the embed", async () => {
    fetchMetadata.mockResolvedValue(metadata)
    const wrapper = mount(EmbedChartView)
    await flushPromises()
    const footer = wrapper.get(".embed-source")
    expect(footer.findAll("a").map((link) => link.attributes("href"))).toEqual(
      metadata.sources.map((source: { url: string }) => source.url),
    )
    expect(footer.text()).toContain(metadata.access_date)
    expect(footer.text()).toContain("IUMABEDR")
    expect(footer.text()).toContain("D7G7")
    wrapper.unmount()
  })
})
