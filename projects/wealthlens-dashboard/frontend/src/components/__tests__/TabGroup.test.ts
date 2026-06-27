import { describe, it, expect } from "vitest"
import { mount } from "@vue/test-utils"
import TabGroup from "@/components/TabGroup.vue"

const tabs = [
  { id: "chart", label: "Chart" },
  { id: "table", label: "Table" },
  { id: "metadata", label: "Metadata" },
]

describe("TabGroup", () => {
  it("renders all tab buttons", () => {
    const wrapper = mount(TabGroup, { props: { tabs, activeId: "chart" } })
    const buttons = wrapper.findAll('[role="tab"]')
    expect(buttons).toHaveLength(3)
    expect(buttons[0].text()).toBe("Chart")
    expect(buttons[1].text()).toBe("Table")
  })

  it("marks active tab with aria-selected", () => {
    const wrapper = mount(TabGroup, { props: { tabs, activeId: "table" } })
    const active = wrapper.find('[aria-selected="true"]')
    expect(active.text()).toBe("Table")
  })

  it('uses role="tablist"', () => {
    const wrapper = mount(TabGroup, { props: { tabs, activeId: "chart" } })
    expect(wrapper.find('[role="tablist"]').exists()).toBe(true)
  })

  it("renders tabpanels with correct aria-labelledby", () => {
    const wrapper = mount(TabGroup, { props: { tabs, activeId: "chart" } })
    const panel = wrapper.find("#panel-chart")
    expect(panel.exists()).toBe(true)
    expect(panel.attributes("aria-labelledby")).toBe("tab-chart")
  })

  it("hides non-active panels", () => {
    const wrapper = mount(TabGroup, { props: { tabs, activeId: "chart" } })
    const tablePanel = wrapper.find("#panel-table")
    expect(tablePanel.attributes("hidden")).toBeDefined()
  })

  it("emits update:activeId on tab click", async () => {
    const wrapper = mount(TabGroup, { props: { tabs, activeId: "chart" } })
    const tableTab = wrapper.findAll('[role="tab"]')[1]
    await tableTab.trigger("click")
    expect(wrapper.emitted("update:activeId")).toEqual([["table"]])
  })

  it("sets tabindex=0 on active and -1 on inactive tabs", () => {
    const wrapper = mount(TabGroup, { props: { tabs, activeId: "table" } })
    const buttons = wrapper.findAll('[role="tab"]')
    expect(buttons[0].attributes("tabindex")).toBe("-1")
    expect(buttons[1].attributes("tabindex")).toBe("0")
    expect(buttons[2].attributes("tabindex")).toBe("-1")
  })

  it("links tab to panel via aria-controls", () => {
    const wrapper = mount(TabGroup, { props: { tabs, activeId: "chart" } })
    const tab = wrapper.find("#tab-chart")
    expect(tab.attributes("aria-controls")).toBe("panel-chart")
  })
})
