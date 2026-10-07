import { describe, it, expect } from "vitest"
import { mount } from "@vue/test-utils"
import WealthCalculator from "@/components/WealthCalculator.vue"
import { COMPARISON_STATS } from "@/utils/wealthPosition"

/**
 * The header shows WAS-derived copy before any calculation, so the ONS
 * source citation must be visible with no interaction.
 */

/** Mount helper with stubs for router-link if needed */
function mountCalc() {
  return mount(WealthCalculator, {
    global: {
      stubs: {
        "router-link": true,
      },
    },
  })
}

describe("WealthCalculator — header WAS source citation", () => {
  it("cites the ONS source in the header before any calculation", () => {
    const wrapper = mountCalc()
    const header = wrapper.get("header.calc__header")
    const anchor = header.get("a")

    expect(anchor.attributes("href")).toBe(COMPARISON_STATS.sourceUrl)
    expect(anchor.attributes("rel")).toBe("noopener")
    expect(anchor.attributes("target")).toBe("_blank")

    const text = header.text()
    expect(text).toContain(`Accessed ${COMPARISON_STATS.accessed}`)
    expect(text).toContain(COMPARISON_STATS.source)

    const anchorEl = anchor.element
    expect(wrapper.get("#panel-single").element.contains(anchorEl)).toBe(false)
    expect(wrapper.get("#panel-compare").element.contains(anchorEl)).toBe(false)
  })
})
