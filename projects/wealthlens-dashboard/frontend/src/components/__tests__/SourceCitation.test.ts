import { describe, it, expect } from "vitest"
import { mount } from "@vue/test-utils"
import SourceCitation from "@/components/SourceCitation.vue"

const defaultProps = {
  source: "ONS",
  sourceUrl: "https://www.ons.gov.uk/data",
  accessDate: "2026-05-14",
}

describe("SourceCitation", () => {
  it("renders source name as link text", () => {
    const wrapper = mount(SourceCitation, { props: defaultProps })
    const link = wrapper.find("a")
    expect(link.text()).toContain("ONS")
  })

  it("links to the source URL", () => {
    const wrapper = mount(SourceCitation, { props: defaultProps })
    const link = wrapper.find("a")
    expect(link.attributes("href")).toBe("https://www.ons.gov.uk/data")
  })

  it("opens link in new tab with noopener", () => {
    const wrapper = mount(SourceCitation, { props: defaultProps })
    const link = wrapper.find("a")
    expect(link.attributes("target")).toBe("_blank")
    expect(link.attributes("rel")).toBe("noopener noreferrer")
  })

  it("displays access date", () => {
    const wrapper = mount(SourceCitation, { props: defaultProps })
    expect(wrapper.text()).toContain("Accessed 2026-05-14")
  })

  it("includes sr-only new tab hint", () => {
    const wrapper = mount(SourceCitation, { props: defaultProps })
    const srOnly = wrapper.find(".sr-only")
    expect(srOnly.exists()).toBe(true)
    expect(srOnly.text()).toContain("opens in new tab")
  })

  it("renders as a footer element", () => {
    const wrapper = mount(SourceCitation, { props: defaultProps })
    expect(wrapper.find("footer").exists()).toBe(true)
  })
})
