import { describe, it, expect } from "vitest"
import { mount } from "@vue/test-utils"
import WealthCalculator from "@/components/WealthCalculator.vue"

const SOURCE_URL =
  "https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/bulletins/totalwealthingreatbritain/april2018tomarch2020"

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

describe("WealthCalculator: WAS source citation", () => {
  it("cites the ONS source in the header before any calculation", () => {
    const wrapper = mountCalc()
    const header = wrapper.get("header.calc__header")
    const anchor = header.get("a")

    expect(anchor.attributes("href")).toBe(SOURCE_URL)
    expect(anchor.attributes("rel")).toBe("noopener noreferrer")
    expect(anchor.attributes("target")).toBe("_blank")

    const text = header.text()
    expect(text).toContain("Accessed 2026-05-16")
    expect(text).toContain("ONS Wealth and Assets Survey, Round 7, April 2018 to March 2020")

    const anchorEl = anchor.element
    expect(wrapper.get("#panel-single").element.contains(anchorEl)).toBe(false)
    expect(wrapper.get("#panel-compare").element.contains(anchorEl)).toBe(false)
  })

  it.each(["single", "compare"])(
    "shows exactly one source link before and after a %s calculation",
    async (mode) => {
      const wrapper = mountCalc()
      await wrapper.get(`#tab-${mode}`).trigger("click")

      const sourceSelector = `a[href="${SOURCE_URL}"]`
      expect(wrapper.findAll(sourceSelector)).toHaveLength(1)
      expect(wrapper.get(sourceSelector).isVisible()).toBe(true)

      if (mode === "single") {
        await wrapper.get("#wealth-input").setValue("100000")
        await wrapper.get("#panel-single .calc__btn").trigger("click")
        expect(wrapper.get('[aria-label="Your wealth position"]').isVisible()).toBe(true)
      } else {
        await wrapper.get("#compare-input-a").setValue("100000")
        await wrapper.get("#compare-input-b").setValue("500000")
        await wrapper.get(".calc__btn--compare").trigger("click")
        expect(wrapper.get('[aria-label="Comparison results"]').isVisible()).toBe(true)
      }

      expect(wrapper.findAll(sourceSelector)).toHaveLength(1)
      expect(wrapper.get(sourceSelector).isVisible()).toBe(true)
    },
  )
})
