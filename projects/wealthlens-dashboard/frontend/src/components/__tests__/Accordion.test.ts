import { describe, it, expect } from "vitest"
import { mount } from "@vue/test-utils"
import Accordion from "@/components/Accordion.vue"

describe("Accordion", () => {
  it("renders title in button", () => {
    const wrapper = mount(Accordion, {
      props: { title: "Details" },
      slots: { default: "Content here" },
    })
    expect(wrapper.find("button").text()).toContain("Details")
  })

  it("panel is hidden by default", () => {
    const wrapper = mount(Accordion, {
      props: { title: "Info" },
      slots: { default: "Hidden" },
    })
    const panel = wrapper.find('[role="region"]')
    expect(panel.isVisible()).toBe(false)
  })

  it("shows panel on click", async () => {
    const wrapper = mount(Accordion, {
      props: { title: "FAQ" },
      slots: { default: "Answer" },
    })
    await wrapper.find("button").trigger("click")
    expect(wrapper.find('[role="region"]').isVisible()).toBe(true)
  })

  it("hides panel on second click", async () => {
    const wrapper = mount(Accordion, {
      props: { title: "FAQ" },
      slots: { default: "Answer" },
    })
    await wrapper.find("button").trigger("click")
    await wrapper.find("button").trigger("click")
    expect(wrapper.find('[role="region"]').isVisible()).toBe(false)
  })

  it("sets aria-expanded correctly", async () => {
    const wrapper = mount(Accordion, {
      props: { title: "Q" },
      slots: { default: "A" },
    })
    expect(wrapper.find("button").attributes("aria-expanded")).toBe("false")
    await wrapper.find("button").trigger("click")
    expect(wrapper.find("button").attributes("aria-expanded")).toBe("true")
  })

  it("links button to panel via aria-controls", () => {
    const wrapper = mount(Accordion, {
      props: { title: "Q" },
      slots: { default: "A" },
    })
    const panelId = wrapper.find('[role="region"]').attributes("id")
    expect(wrapper.find("button").attributes("aria-controls")).toBe(panelId)
  })

  it("panel has aria-labelledby pointing to heading", () => {
    const wrapper = mount(Accordion, {
      props: { title: "Q" },
      slots: { default: "A" },
    })
    const headingId = wrapper.find("button").attributes("id")
    expect(wrapper.find('[role="region"]').attributes("aria-labelledby")).toBe(headingId)
  })

  it("renders slot content", async () => {
    const wrapper = mount(Accordion, {
      props: { title: "Q" },
      slots: { default: '<p class="answer">The answer</p>' },
    })
    await wrapper.find("button").trigger("click")
    expect(wrapper.find(".answer").text()).toBe("The answer")
  })
})
