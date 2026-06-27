import { describe, it, expect } from "vitest"
import { mount } from "@vue/test-utils"
import RevenueBreakdown from "@/components/RevenueBreakdown.vue"
import type { Interval } from "@/types/simulator"

const iv = (low: number, central: number, high: number): Interval => ({
  low,
  central,
  high,
})

const NATIONS: Record<string, Interval> = {
  england: iv(12.5, 16.66, 24.06),
  scotland: iv(0.42, 0.56, 0.81),
  wales: iv(1.25, 1.66, 2.4),
}

// 10 deciles, revenue concentrated in the top two (indices 8 and 9).
const DECILES: Interval[] = Array.from({ length: 10 }, (_, i) =>
  i === 9 ? iv(10, 14, 20) : i === 8 ? iv(3, 5, 7) : iv(0, 0, 0),
)

describe("RevenueBreakdown", () => {
  it("renders the nation table sorted by central revenue (largest first)", () => {
    const wrapper = mount(RevenueBreakdown, { props: { byNation: NATIONS } })
    expect(wrapper.text()).toContain("By nation")
    const rowHeaders = wrapper.findAll('tbody th[scope="row"]').map((h) => h.text())
    expect(rowHeaders).toEqual(["England", "Wales", "Scotland"]) // 16.66 > 1.66 > 0.56
    expect(wrapper.text()).toContain("£16.66bn")
  })

  it("renders the decile table with least/most wealthy labels and central values", () => {
    const wrapper = mount(RevenueBreakdown, { props: { byDecile: DECILES } })
    expect(wrapper.text()).toContain("By wealth decile")
    expect(wrapper.text()).toContain("Decile 1 (least wealthy)")
    expect(wrapper.text()).toContain("Decile 10 (wealthiest)")
    expect(wrapper.text()).toContain("£14.00bn")
  })

  it("draws a decorative (aria-hidden) proportional bar; the top decile is widest", () => {
    const wrapper = mount(RevenueBreakdown, { props: { byDecile: DECILES } })
    const bars = wrapper.findAll('span[aria-hidden="true"]')
    expect(bars.length).toBe(10)
    // The largest central (decile 10 = 14) is the 100% bar; a zero decile is 0%.
    expect(bars[9].attributes("style")).toContain("width: 100%")
    expect(bars[0].attributes("style")).toContain("width: 0%")
  })

  it("respects currency/unit overrides", () => {
    const wrapper = mount(RevenueBreakdown, {
      props: { byNation: { uk: iv(1, 2, 3) }, currency: "$", unit: "m" },
    })
    expect(wrapper.text()).toContain("$2.00m")
  })

  it("renders only the nation section when no decile data", () => {
    const wrapper = mount(RevenueBreakdown, { props: { byNation: NATIONS } })
    expect(wrapper.text()).toContain("By nation")
    expect(wrapper.text()).not.toContain("By wealth decile")
  })

  it("renders nothing when both inputs are empty/absent", () => {
    const wrapper = mount(RevenueBreakdown, { props: { byDecile: [], byNation: {} } })
    expect(wrapper.find("section").exists()).toBe(false)
  })

  it("is robust to undefined props", () => {
    const wrapper = mount(RevenueBreakdown, { props: {} })
    expect(wrapper.find("section").exists()).toBe(false)
  })

  it("maps the engine northern_ireland key (underscore) to a friendly name", () => {
    const wrapper = mount(RevenueBreakdown, {
      props: { byNation: { northern_ireland: iv(0.1, 0.2, 0.3) } },
    })
    expect(wrapper.text()).toContain("Northern Ireland")
    expect(wrapper.text()).not.toContain("northern_ireland")
  })

  it("shows a compact range (currency + unit once)", () => {
    const wrapper = mount(RevenueBreakdown, {
      props: { byNation: { england: iv(12.5, 16.66, 24.06) } },
    })
    expect(wrapper.text()).toContain("£12.50–24.06bn")
  })

  it("omits the least/most-wealthy qualifiers for a partial (non-10) decile set", () => {
    const wrapper = mount(RevenueBreakdown, {
      props: { byDecile: [iv(0, 1, 2), iv(0, 3, 4)] },
    })
    expect(wrapper.text()).not.toContain("wealthiest")
    expect(wrapper.text()).not.toContain("least wealthy")
    expect(wrapper.text()).toContain("Decile 1")
    expect(wrapper.text()).toContain("Decile 2")
  })

  it("renders an em dash for a non-finite value rather than NaN", () => {
    const wrapper = mount(RevenueBreakdown, {
      props: { byNation: { england: iv(NaN, NaN, NaN) } },
    })
    expect(wrapper.text()).toContain("—")
    expect(wrapper.text()).not.toContain("NaN")
  })

  it("does not throw on null nation entries (malformed payload)", () => {
    const byNation = {
      england: iv(1, 2, 3),
      scotland: null,
    } as unknown as Record<string, Interval>
    const wrapper = mount(RevenueBreakdown, { props: { byNation } })
    expect(wrapper.text()).toContain("England")
    expect(wrapper.findAll('tbody th[scope="row"]')).toHaveLength(1)
  })

  it("drops null decile elements and clamps a negative bar to 0%", () => {
    const byDecile = [
      null,
      iv(-5, -5, -5), // negative central -> bar clamped to 0%, value shown
      iv(0, 4, 8),
    ] as unknown as Interval[]
    const wrapper = mount(RevenueBreakdown, { props: { byDecile } })
    const bars = wrapper.findAll('span[aria-hidden="true"]')
    expect(bars).toHaveLength(2) // the null element is dropped
    expect(bars.every((b) => !(b.attributes("style") ?? "").includes("width: -"))).toBe(true)
  })
})
