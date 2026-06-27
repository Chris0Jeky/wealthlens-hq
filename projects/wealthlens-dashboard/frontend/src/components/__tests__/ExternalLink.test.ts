import { describe, it, expect } from "vitest"
import { mount } from "@vue/test-utils"
import ExternalLink from "@/components/ExternalLink.vue"

describe("ExternalLink", () => {
  it("renders slot content", () => {
    const wrapper = mount(ExternalLink, {
      props: { href: "https://example.com" },
      slots: { default: "Example" },
    })
    expect(wrapper.text()).toContain("Example")
  })

  it("sets href for https URLs", () => {
    const wrapper = mount(ExternalLink, {
      props: { href: "https://example.com/page" },
      slots: { default: "Link" },
    })
    expect(wrapper.find("a").attributes("href")).toBe("https://example.com/page")
  })

  it("sets href for http URLs", () => {
    const wrapper = mount(ExternalLink, {
      props: { href: "http://example.com" },
      slots: { default: "Link" },
    })
    expect(wrapper.find("a").attributes("href")).toBe("http://example.com")
  })

  it("sanitises non-http schemes to #", () => {
    const wrapper = mount(ExternalLink, {
      props: { href: "javascript:alert(1)" },
      slots: { default: "Link" },
    })
    expect(wrapper.find("a").attributes("href")).toBe("#")
  })

  it("sanitises data URIs to #", () => {
    const wrapper = mount(ExternalLink, {
      props: { href: "data:text/html,<h1>hi</h1>" },
      slots: { default: "Link" },
    })
    expect(wrapper.find("a").attributes("href")).toBe("#")
  })

  it("opens in a new tab with noopener noreferrer", () => {
    const wrapper = mount(ExternalLink, {
      props: { href: "https://example.com" },
      slots: { default: "Link" },
    })
    const a = wrapper.find("a")
    expect(a.attributes("target")).toBe("_blank")
    expect(a.attributes("rel")).toBe("noopener noreferrer")
  })

  it("includes sr-only hint about new tab", () => {
    const wrapper = mount(ExternalLink, {
      props: { href: "https://example.com" },
      slots: { default: "Link" },
    })
    const srOnly = wrapper.find(".sr-only")
    expect(srOnly.exists()).toBe(true)
    expect(srOnly.text()).toContain("opens in new tab")
  })
})
