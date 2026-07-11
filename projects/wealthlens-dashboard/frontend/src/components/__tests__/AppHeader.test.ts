import { describe, it, expect } from "vitest"
import { mount } from "@vue/test-utils"
import { defineComponent, h } from "vue"
import AppHeader from "@/components/AppHeader.vue"
import i18n from "@/i18n"

const RouterLinkStub = defineComponent({
  name: "RouterLink",
  props: { to: { type: String, required: true } },
  setup(props, { slots }) {
    return () => h("a", { href: props.to }, slots.default?.())
  },
})

function mountHeader() {
  return mount(AppHeader, {
    global: {
      plugins: [i18n],
      stubs: { RouterLink: RouterLinkStub },
    },
  })
}

describe("AppHeader", () => {
  it('renders the brand text "WealthLens" and "UK"', () => {
    const wrapper = mountHeader()
    expect(wrapper.text()).toContain("WealthLens")
    expect(wrapper.text()).toContain("UK")
  })

  it("shows the build-time data vintage, not the visitor's clock (F4)", () => {
    const wrapper = mountHeader()
    // __WL_DATA_VINTAGE__ is defined in vitest.config.ts from the real
    // freshness.json, so the band carries a data claim, not new Date().
    expect(wrapper.find(".vintage").text()).toMatch(/^Data as of \d{1,2} [A-Z][a-z]{2} \d{4}$/)
    expect(wrapper.text()).not.toContain("Live · Updated")
  })

  it("renders desktop navigation links", () => {
    const wrapper = mountHeader()
    const navLinks = wrapper.findAll(".nav-link")
    const texts = navLinks.map((l) => l.text())
    expect(texts).toContain("Front page")
    expect(texts).toContain("The data")
    expect(texts).toContain("Simulator")
    expect(texts).toContain("Methodology")
    expect(texts).toContain("About")
    expect(texts).toContain("Contribute")
  })

  it("has a hamburger button with correct aria attributes", () => {
    const wrapper = mountHeader()
    const btn = wrapper.find('button[aria-label="Toggle navigation menu"]')
    expect(btn.exists()).toBe(true)
    expect(btn.attributes("aria-expanded")).toBe("false")
    expect(btn.attributes("aria-controls")).toBe("mobile-menu")
  })

  it("toggles mobile menu open on hamburger click", async () => {
    const wrapper = mountHeader()
    const btn = wrapper.find('button[aria-label="Toggle navigation menu"]')

    expect(wrapper.find("#mobile-menu").exists()).toBe(false)

    await btn.trigger("click")

    expect(btn.attributes("aria-expanded")).toBe("true")
    expect(wrapper.find("#mobile-menu").exists()).toBe(true)
  })

  it("closes mobile menu on second hamburger click", async () => {
    const wrapper = mountHeader()
    const btn = wrapper.find('button[aria-label="Toggle navigation menu"]')

    await btn.trigger("click")
    expect(wrapper.find("#mobile-menu").exists()).toBe(true)

    await btn.trigger("click")
    expect(wrapper.find("#mobile-menu").exists()).toBe(false)
  })

  it("renders the brand link pointing to home", () => {
    const wrapper = mountHeader()
    const brandLink = wrapper.find('a[aria-label="WealthLens UK — home page"]')
    expect(brandLink.exists()).toBe(true)
    expect(brandLink.attributes("href")).toBe("/")
  })

  it("closes mobile menu on Escape key", async () => {
    const wrapper = mountHeader()
    const btn = wrapper.find('button[aria-label="Toggle navigation menu"]')
    await btn.trigger("click")
    expect(wrapper.find("#mobile-menu").exists()).toBe(true)

    const menu = wrapper.find("#mobile-menu")
    await menu.trigger("keydown", { key: "Escape" })
    expect(wrapper.find("#mobile-menu").exists()).toBe(false)
    expect(btn.attributes("aria-expanded")).toBe("false")
  })
})
