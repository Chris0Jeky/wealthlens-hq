import { describe, it, expect } from "vitest"
import { mount } from "@vue/test-utils"
import Tooltip from "@/components/Tooltip.vue"

describe("Tooltip", () => {
  it("does not show tooltip by default", () => {
    const wrapper = mount(Tooltip, {
      props: { text: "Info" },
      slots: { default: "<button>Hover me</button>" },
    })
    expect(wrapper.find('[role="tooltip"]').exists()).toBe(false)
  })

  it("shows tooltip on mouseenter", async () => {
    const wrapper = mount(Tooltip, {
      props: { text: "Tooltip text" },
      slots: { default: "<button>Hover</button>" },
    })
    await wrapper.find("span").trigger("mouseenter")
    const tooltip = wrapper.find('[role="tooltip"]')
    expect(tooltip.exists()).toBe(true)
    expect(tooltip.text()).toBe("Tooltip text")
  })

  it("hides tooltip on mouseleave", async () => {
    const wrapper = mount(Tooltip, {
      props: { text: "Info" },
      slots: { default: "<button>Hover</button>" },
    })
    await wrapper.find("span").trigger("mouseenter")
    expect(wrapper.find('[role="tooltip"]').exists()).toBe(true)
    await wrapper.find("span").trigger("mouseleave")
    expect(wrapper.find('[role="tooltip"]').exists()).toBe(false)
  })

  it("shows tooltip on focusin", async () => {
    const wrapper = mount(Tooltip, {
      props: { text: "Focus info" },
      slots: { default: "<button>Focus</button>" },
    })
    await wrapper.find("span").trigger("focusin")
    expect(wrapper.find('[role="tooltip"]').exists()).toBe(true)
  })

  it('uses role="tooltip"', async () => {
    const wrapper = mount(Tooltip, {
      props: { text: "Test" },
      slots: { default: "<span>X</span>" },
    })
    await wrapper.find("span").trigger("mouseenter")
    expect(wrapper.find('[role="tooltip"]').exists()).toBe(true)
  })

  it("positions above by default", async () => {
    const wrapper = mount(Tooltip, {
      props: { text: "Top" },
      slots: { default: "<span>X</span>" },
    })
    await wrapper.find("span").trigger("mouseenter")
    const tooltip = wrapper.find('[role="tooltip"]')
    expect(tooltip.classes()).toContain("bottom-full")
  })

  it("positions below when position is bottom", async () => {
    const wrapper = mount(Tooltip, {
      props: { text: "Bottom", position: "bottom" },
      slots: { default: "<span>X</span>" },
    })
    await wrapper.find("span").trigger("mouseenter")
    const tooltip = wrapper.find('[role="tooltip"]')
    expect(tooltip.classes()).toContain("top-full")
  })
})
