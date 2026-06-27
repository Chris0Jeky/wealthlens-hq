import { describe, it, expect } from "vitest"
import { mount } from "@vue/test-utils"
import NumberStat from "@/components/NumberStat.vue"

describe("NumberStat", () => {
  it("renders the value prominently", () => {
    const wrapper = mount(NumberStat, {
      props: { value: "23%", label: "Top 1% wealth share" },
    })
    expect(wrapper.text()).toContain("23%")
  })

  it("renders the label", () => {
    const wrapper = mount(NumberStat, {
      props: { value: "£1.2bn", label: "Average wealth" },
    })
    expect(wrapper.text()).toContain("Average wealth")
  })

  it("renders description when provided", () => {
    const wrapper = mount(NumberStat, {
      props: {
        value: "8.5x",
        label: "Affordability ratio",
        description: "Median house price to earnings",
      },
    })
    expect(wrapper.text()).toContain("Median house price to earnings")
  })

  it("omits description when not provided", () => {
    const wrapper = mount(NumberStat, {
      props: { value: "42", label: "Datasets" },
    })
    const paragraphs = wrapper.findAll("p")
    expect(paragraphs).toHaveLength(2)
  })

  it("includes sr-only combined text for screen readers", () => {
    const wrapper = mount(NumberStat, {
      props: { value: "70%", label: "Housing owned" },
    })
    const srOnly = wrapper.find(".sr-only")
    expect(srOnly.text()).toBe("Housing owned: 70%")
  })

  it("uses large font for the value", () => {
    const wrapper = mount(NumberStat, {
      props: { value: "5", label: "Regions" },
    })
    const value = wrapper.find(".text-3xl")
    expect(value.exists()).toBe(true)
    expect(value.text()).toBe("5")
  })
})
