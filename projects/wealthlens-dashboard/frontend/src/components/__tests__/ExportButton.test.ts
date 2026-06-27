import { describe, it, expect } from "vitest"
import { mount } from "@vue/test-utils"
import ExportButton from "@/components/ExportButton.vue"

describe("ExportButton", () => {
  it("renders the export trigger button", () => {
    const wrapper = mount(ExportButton)
    expect(wrapper.find("button").text()).toContain("Export")
  })

  it("menu is closed by default", () => {
    const wrapper = mount(ExportButton)
    expect(wrapper.find('[role="menu"]').exists()).toBe(false)
  })

  it("opens menu on button click", async () => {
    const wrapper = mount(ExportButton)
    await wrapper.find("button").trigger("click")
    expect(wrapper.find('[role="menu"]').exists()).toBe(true)
  })

  it("sets aria-expanded correctly", async () => {
    const wrapper = mount(ExportButton)
    const trigger = wrapper.find("button")
    expect(trigger.attributes("aria-expanded")).toBe("false")
    await trigger.trigger("click")
    expect(trigger.attributes("aria-expanded")).toBe("true")
  })

  it("has aria-haspopup on trigger", () => {
    const wrapper = mount(ExportButton)
    expect(wrapper.find("button").attributes("aria-haspopup")).toBe("true")
  })

  it("shows PNG and SVG options in menu", async () => {
    const wrapper = mount(ExportButton)
    await wrapper.find("button").trigger("click")
    const items = wrapper.findAll('[role="menuitem"]')
    expect(items.length).toBe(2)
    expect(items[0].text()).toBe("Download PNG")
    expect(items[1].text()).toBe("Download SVG")
  })

  it('emits export with "png" when PNG option is clicked', async () => {
    const wrapper = mount(ExportButton)
    await wrapper.find("button").trigger("click")
    const items = wrapper.findAll('[role="menuitem"]')
    await items[0].trigger("click")
    expect(wrapper.emitted("export")).toEqual([["png"]])
  })

  it('emits export with "svg" when SVG option is clicked', async () => {
    const wrapper = mount(ExportButton)
    await wrapper.find("button").trigger("click")
    const items = wrapper.findAll('[role="menuitem"]')
    await items[1].trigger("click")
    expect(wrapper.emitted("export")).toEqual([["svg"]])
  })

  it("closes menu after selection", async () => {
    const wrapper = mount(ExportButton)
    await wrapper.find("button").trigger("click")
    expect(wrapper.find('[role="menu"]').exists()).toBe(true)
    const items = wrapper.findAll('[role="menuitem"]')
    await items[0].trigger("click")
    expect(wrapper.find('[role="menu"]').exists()).toBe(false)
  })

  it("closes on Escape key", async () => {
    const wrapper = mount(ExportButton, {
      attachTo: document.body,
    })
    await wrapper.find("button").trigger("click")
    expect(wrapper.find('[role="menu"]').exists()).toBe(true)
    await wrapper.find(".export-btn").trigger("keydown", { key: "Escape" })
    expect(wrapper.find('[role="menu"]').exists()).toBe(false)
    wrapper.unmount()
  })

  it("toggles menu on repeated clicks", async () => {
    const wrapper = mount(ExportButton)
    const trigger = wrapper.find("button")
    await trigger.trigger("click")
    expect(wrapper.find('[role="menu"]').exists()).toBe(true)
    await trigger.trigger("click")
    expect(wrapper.find('[role="menu"]').exists()).toBe(false)
  })
})
