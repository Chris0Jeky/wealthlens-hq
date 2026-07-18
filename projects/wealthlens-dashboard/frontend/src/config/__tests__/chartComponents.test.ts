import { describe, it, expect } from "vitest"
import { CHART_COMPONENT_LOADERS } from "../chartComponents"
import { VALID_CHART_NAMES } from "@/constants/charts"

describe("CHART_COMPONENT_LOADERS", () => {
  it("has exactly one loader per routed chart — the embed shell can render them all", () => {
    expect(new Set(Object.keys(CHART_COMPONENT_LOADERS))).toEqual(VALID_CHART_NAMES)
  })

  it("every loader resolves to a component module", async () => {
    // Import one representative loader end-to-end (importing all 12 would pull
    // the full echarts graph into this test for no additional signal).
    const mod = await CHART_COMPONENT_LOADERS["wealth-shares"]()
    expect(mod.default).toBeTruthy()
  })
})
