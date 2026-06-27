import { describe, it, expect } from "vitest"
import { mount } from "@vue/test-utils"
import { defineComponent, h } from "vue"
import RelatedCharts from "@/components/RelatedCharts.vue"

const RouterLinkStub = defineComponent({
  name: "RouterLink",
  props: { to: { type: String, required: true } },
  setup(props, { slots }) {
    return () => h("a", { href: props.to, class: "related__card" }, slots.default?.())
  },
})

const sampleCharts = [
  {
    domain: "Wealth",
    title: "Household wealth",
    finding: "Key finding <b>here</b>",
    to: "/charts/household-wealth",
  },
  {
    domain: "Housing",
    title: "Affordability ratio",
    finding: "Another finding",
    to: "/charts/housing",
    sparkType: "bar" as const,
  },
  { domain: "Tax", title: "CGT concentration", finding: "Third finding", to: "/charts/cgt" },
]

function mountRelated(charts = sampleCharts) {
  return mount(RelatedCharts, {
    props: { charts },
    global: {
      stubs: { RouterLink: RouterLinkStub },
    },
  })
}

describe("RelatedCharts", () => {
  it("renders cards with domain, title, and finding", () => {
    const wrapper = mountRelated()
    const cards = wrapper.findAll("a.related__card")
    expect(cards).toHaveLength(3)

    expect(cards[0].find(".related__domain").text()).toBe("Wealth")
    expect(cards[0].find(".related__title").text()).toBe("Household wealth")
    expect(cards[0].find(".related__finding").html()).toContain("Key finding <b>here</b>")
  })

  it("links cards to the correct route", () => {
    const wrapper = mountRelated()
    const cards = wrapper.findAll("a.related__card")
    expect(cards[0].attributes("href")).toBe("/charts/household-wealth")
    expect(cards[1].attributes("href")).toBe("/charts/housing")
    expect(cards[2].attributes("href")).toBe("/charts/cgt")
  })

  it("renders nothing in the grid when charts array is empty", () => {
    const wrapper = mountRelated([])
    const cards = wrapper.findAll("a.related__card")
    expect(cards).toHaveLength(0)
  })

  it("renders the section heading", () => {
    const wrapper = mountRelated()
    const heading = wrapper.find("#related-heading")
    expect(heading.exists()).toBe(true)
    expect(heading.text()).toContain("More from the wealth pillar")
  })

  it("has an accessible section with aria-labelledby", () => {
    const wrapper = mountRelated()
    const section = wrapper.find('section[aria-labelledby="related-heading"]')
    expect(section.exists()).toBe(true)
  })
})
