import { afterEach, beforeEach, describe, expect, it } from "vitest"
import { effectScope, nextTick } from "vue"
import { readFileSync } from "node:fs"
import { useChartTheme } from "@/composables/useChartTheme"
import { _resetForTesting, useTheme } from "@/composables/useTheme"

const tokens = readFileSync("src/assets/tokens.css", "utf8")

function channels(hex: string): number[] {
  const value = hex.slice(1)
  return (value.length === 3 ? [...value].map((c) => c + c) : value.match(/../g)!).map((c) =>
    parseInt(c, 16),
  )
}

function contrast(foreground: string, background: string, opacity = 1): number {
  const bg = channels(background)
  const fg = channels(foreground).map((c, i) => c * opacity + bg[i] * (1 - opacity))
  const luminance = (rgb: number[]) =>
    rgb
      .map((c) => {
        const s = c / 255
        return s <= 0.04045 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4
      })
      .reduce((sum, c, i) => sum + c * [0.2126, 0.7152, 0.0722][i], 0)
  const values = [luminance(fg), luminance(bg)].sort((a, b) => b - a)
  return (values[0] + 0.05) / (values[1] + 0.05)
}

describe("useChartTheme", () => {
  let style: HTMLStyleElement
  let scope: ReturnType<typeof effectScope>
  beforeEach(() => {
    _resetForTesting()
    localStorage.clear()
    style = document.createElement("style")
    // Use the production tokens rather than duplicating their values in fixtures.
    style.textContent = [
      tokens.match(/:root \{[\s\S]*?\n\}/)![0],
      tokens.match(/\[data-theme="dark"\] \{[\s\S]*?\n\}/)![0],
    ].join("\n")
    document.head.appendChild(style)
    scope = effectScope()
  })
  afterEach(() => {
    scope?.stop()
    style.remove()
    _resetForTesting()
    localStorage.clear()
  })

  it("reproduces the original dark-card text failure", () => {
    expect(contrast("#111827", "#242424")).toBeLessThan(4.5)
    expect(contrast("#374151", "#242424")).toBeLessThan(4.5)
  })

  it("resolves CSS tokens and keeps text and marks above AA contrast in both themes", async () => {
    const chart = scope.run(useChartTheme)!
    const light = { ...chart.colors.value }
    const palette = [
      "#1a56db",
      "#dc2626",
      "#b91c1c",
      "#047857",
      "#7c3aed",
      "#b45309",
      "#0e7490",
      "#be185d",
      "#4338ca",
      "#6b7280",
      "#374151",
    ]
    for (const theme of ["light", "dark"] as const) {
      if (theme === "dark") useTheme().toggleTheme()
      await nextTick()
      const { heading, text, muted, card } = chart.colors.value
      const css = getComputedStyle(document.documentElement)
      expect(heading).toBe(css.getPropertyValue("--wl-ink").trim())
      expect(text).toBe(css.getPropertyValue("--wl-ink-body").trim())
      expect(card).toBe(css.getPropertyValue("--wl-card").trim())
      for (const color of [heading, text, muted])
        expect(contrast(color, card)).toBeGreaterThanOrEqual(4.5)
      expect(chart.axisStyle.value.nameTextStyle.color).toBe(text)
      for (const color of palette) {
        expect(contrast(chart.markColor(color), card)).toBeGreaterThanOrEqual(3)
      }
      for (const color of ["#1a56db", "#047857", "#dc2626"]) {
        expect(contrast(chart.markColor(color), card, 0.75)).toBeGreaterThanOrEqual(3)
      }
      expect(contrast(chart.onMark.value, chart.markColor("#1a56db"))).toBeGreaterThanOrEqual(4.5)
    }
    expect(chart.colors.value).not.toEqual(light)
    useTheme().toggleTheme()
    await nextTick()
    expect(chart.colors.value).toEqual(light)
  })
})
