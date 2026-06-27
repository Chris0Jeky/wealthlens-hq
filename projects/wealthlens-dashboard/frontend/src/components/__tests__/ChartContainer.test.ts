import { describe, it, expect } from "vitest"
import { mount } from "@vue/test-utils"
import ChartContainer from "@/components/ChartContainer.vue"

describe("ChartContainer", () => {
  it("renders title", () => {
    const wrapper = mount(ChartContainer, {
      props: { title: "Wealth Shares" },
    })
    expect(wrapper.find("h2").text()).toBe("Wealth Shares")
  })

  it("renders subtitle when provided", () => {
    const wrapper = mount(ChartContainer, {
      props: { title: "Test", subtitle: "GB data since 1990" },
    })
    expect(wrapper.text()).toContain("GB data since 1990")
  })

  it("has section with aria-label matching title", () => {
    const wrapper = mount(ChartContainer, {
      props: { title: "Housing" },
    })
    expect(wrapper.find("section").attributes("aria-label")).toBe("Housing")
  })

  it("shows loading spinner when loading is true", () => {
    const wrapper = mount(ChartContainer, {
      props: { title: "Test", loading: true },
    })
    expect(wrapper.find('[role="status"]').exists()).toBe(true)
    expect(wrapper.find('[aria-busy="true"]').exists()).toBe(true)
  })

  it("shows error message when error is set", () => {
    const wrapper = mount(ChartContainer, {
      props: { title: "Test", error: "Failed to load data" },
    })
    expect(wrapper.find('[role="alert"]').text()).toBe("Failed to load data")
  })

  it("renders default slot content when not loading and no error", () => {
    const wrapper = mount(ChartContainer, {
      props: { title: "Test" },
      slots: { default: '<canvas id="chart"></canvas>' },
    })
    expect(wrapper.find("#chart").exists()).toBe(true)
  })

  it("does not render slot when loading", () => {
    const wrapper = mount(ChartContainer, {
      props: { title: "Test", loading: true },
      slots: { default: '<canvas id="chart"></canvas>' },
    })
    expect(wrapper.find("#chart").exists()).toBe(false)
  })

  it("does not render slot when error is present", () => {
    const wrapper = mount(ChartContainer, {
      props: { title: "Test", error: "bad" },
      slots: { default: '<canvas id="chart"></canvas>' },
    })
    expect(wrapper.find("#chart").exists()).toBe(false)
  })

  it("renders footer slot", () => {
    const wrapper = mount(ChartContainer, {
      props: { title: "Test" },
      slots: { footer: '<span class="citation">Source: ONS</span>' },
    })
    expect(wrapper.find(".citation").text()).toBe("Source: ONS")
  })

  it("hides footer when no footer slot content", () => {
    const wrapper = mount(ChartContainer, {
      props: { title: "Test" },
    })
    expect(wrapper.find("footer").exists()).toBe(false)
  })
})
