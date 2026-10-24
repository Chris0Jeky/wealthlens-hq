import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { readFileSync } from "node:fs"
import { flushPromises, mount } from "@vue/test-utils"
import { nextTick, ref } from "vue"
import { createMemoryHistory, createRouter } from "vue-router"
import ChartView from "@/views/ChartView.vue"
import { _resetForTesting, useTheme } from "@/composables/useTheme"

vi.mock("@/composables/useAnalytics", () => ({
  useAnalytics: () => ({ trackEvent: vi.fn() }),
}))

vi.mock("@/composables/useChartData", () => ({
  useChartData: (name: string) => ({
    // Synthetic rows only exercise rendering; no dataset or public figure changes.
    rows: ref(
      name === "wealth-shares"
        ? [
            { year: 2000, percentile: "p90p100", value: 0.5 },
            { year: 2000, percentile: "p99p100", value: 0.2 },
          ]
        : [{ year: 2000, productivity_index: 100, pay_index: 100, gap_pct: 0 }],
    ),
    loading: ref(false),
    error: ref(null),
  }),
}))

vi.mock("@/stores/data", () => ({
  useDataStore: () => ({ fetchMetadata: vi.fn().mockResolvedValue({ data_type: null }) }),
}))

vi.mock("vue-echarts", () => ({
  default: {
    name: "VChart",
    props: ["option", "autoresize"],
    template: '<div class="vchart-stub" />',
  },
}))

const tokens = readFileSync("src/assets/tokens.css", "utf8")

function rgb(color: string): string {
  const element = document.createElement("span")
  element.style.color = color
  return element.style.color
}

function contrast(foreground: string, background: string): number {
  const luminance = (color: string) =>
    rgb(color)
      .match(/\d+/g)!
      .map((channel) => {
        const s = Number(channel) / 255
        return s <= 0.04045 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4
      })
      .reduce((sum, channel, i) => sum + channel * [0.2126, 0.7152, 0.0722][i], 0)
  const values = [luminance(foreground), luminance(background)].sort((a, b) => b - a)
  return (values[0] + 0.05) / (values[1] + 0.05)
}

describe("ChartView toolbar series colours", () => {
  let style: HTMLStyleElement
  let wrapper: ReturnType<typeof mount> | undefined

  beforeEach(() => {
    localStorage.clear()
    _resetForTesting()
    vi.stubGlobal(
      "matchMedia",
      vi.fn(() => ({ matches: false })),
    )
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("Unexpected network request")))
    style = document.createElement("style")
    style.textContent = [
      tokens.match(/:root \{[\s\S]*?\n\}/)![0],
      tokens.match(/\[data-theme="dark"\] \{[\s\S]*?\n\}/)![0],
    ].join("\n")
    document.head.appendChild(style)
  })

  afterEach(() => {
    wrapper?.unmount()
    wrapper = undefined
    style.remove()
    _resetForTesting()
    localStorage.clear()
    vi.unstubAllGlobals()
  })

  it.each(["wealth-shares", "productivity-pay"])(
    "%s dots match plotted lines and meet 3:1 card contrast in light and dark themes",
    async (chartName) => {
      const router = createRouter({
        history: createMemoryHistory(),
        routes: [
          { path: "/charts/:name", component: ChartView },
          { path: "/", component: { template: "<div />" } },
        ],
      })
      await router.push(`/charts/${chartName}`)
      wrapper = mount(ChartView, {
        global: {
          plugins: [router],
          stubs: {
            StatStrip: true,
            ShareBar: true,
            SharePanel: true,
            RelatedCharts: true,
            DataFreshnessBadge: { props: ["dataset"], template: "<span />" },
            ExportButton: true,
          },
        },
      })
      await flushPromises()
      await vi.dynamicImportSettled()

      // Exercise reactive updates in both directions without remounting the page.
      for (const theme of ["light", "dark", "light"] as const) {
        if (useTheme().theme.value !== theme) useTheme().toggleTheme()
        await nextTick()
        const option = wrapper.findComponent({ name: "VChart" }).props("option")
        const dots = wrapper.findAll<HTMLSpanElement>(".chart-toolbar__dot")
        const card = getComputedStyle(document.documentElement).getPropertyValue("--wl-card").trim()
        expect(card).not.toBe("")
        expect(dots).toHaveLength(2)
        expect(option.series).toHaveLength(dots.length)
        dots.forEach((dot, i) => {
          const color = dot.element.style.backgroundColor
          expect(color).toBe(rgb(option.series[i].lineStyle.color))
          expect(contrast(color, card)).toBeGreaterThanOrEqual(3)
        })
      }
      expect(fetch).not.toHaveBeenCalled()
    },
  )
})
