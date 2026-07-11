import { describe, it, expect } from "vitest"
import { HOME_PILLARS } from "../homePillars"
import { VALID_CHART_NAMES } from "@/constants/charts"
import { chartConfigs, simpleChartTitles } from "@/config/chartArticles"

describe("HOME_PILLARS", () => {
  const allSlugs = HOME_PILLARS.flatMap((p) => [...p.charts])

  it("covers VALID_CHART_NAMES exactly — a new chart cannot ship without a front-page home", () => {
    expect(new Set(allSlugs)).toEqual(VALID_CHART_NAMES)
    expect(allSlugs.length).toBe(VALID_CHART_NAMES.size)
  })

  it("lists every chart exactly once", () => {
    expect(new Set(allSlugs).size).toBe(allSlugs.length)
  })

  it("every slug has a display title in the article config", () => {
    for (const slug of allSlugs) {
      const hasTitle = slug in chartConfigs || slug in simpleChartTitles
      expect(hasTitle, `${slug} needs a headline in chartArticles.ts`).toBe(true)
    }
  })
})
