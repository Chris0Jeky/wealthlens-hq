import { describe, it, expect } from "vitest"
import { mount, RouterLinkStub } from "@vue/test-utils"
import DatasetCard from "@/components/DatasetCard.vue"
import FreshnessIndicator from "@/components/FreshnessIndicator.vue"

describe("DatasetCard", () => {
  const defaultProps = {
    name: "wealth-shares",
    description: "Top 1% and 10% wealth shares (WID)",
  }

  const routerLinkStub = {
    template: '<a :href="to"><slot /></a>',
    props: ["to"],
  }

  function factory(
    props: { name: string; description: string; hasChart?: boolean } = defaultProps,
  ) {
    return mount(DatasetCard, {
      props,
      global: { stubs: { "router-link": routerLinkStub } },
    })
  }

  it("renders the name prop", () => {
    const wrapper = factory()
    expect(wrapper.text()).toContain(defaultProps.name)
  })

  it("renders the description prop", () => {
    const wrapper = factory()
    expect(wrapper.text()).toContain(defaultProps.description)
  })

  it("uses a semantic article element with aria-label", () => {
    const wrapper = mount(DatasetCard, { props: defaultProps })
    expect(wrapper.element.tagName).toBe("ARTICLE")
    expect(wrapper.attributes("aria-label")).toBe(`Dataset: ${defaultProps.name}`)
  })

  it("renders view-chart link with aria-label when chart is available", () => {
    const wrapper = mount(DatasetCard, {
      props: { ...defaultProps, hasChart: true },
      global: { stubs: { RouterLink: RouterLinkStub } },
    })
    const links = wrapper.findAllComponents(RouterLinkStub)
    const chartLink = links.find(
      (l) => l.attributes("aria-label") === `View ${defaultProps.name} chart`,
    )
    expect(chartLink).toBeDefined()
    expect(chartLink!.exists()).toBe(true)
  })

  it("uses an h3 for the dataset name", () => {
    const wrapper = factory()
    const heading = wrapper.find("h3")
    expect(heading.exists()).toBe(true)
    expect(heading.text()).toBe(defaultProps.name)
  })

  it("shows chart link when hasChart is true", () => {
    const wrapper = factory({ name: "wealth-shares", description: "D", hasChart: true })
    expect(wrapper.html()).toContain("/charts/wealth-shares")
  })

  it('shows "coming soon" for unsupported datasets', () => {
    const wrapper = factory({ name: "unknown-dataset", description: "Test" })
    expect(wrapper.text()).toContain("coming soon")
  })

  // Regression: Vue casts an absent Boolean prop to `false`, not `undefined`.
  // Before the `default: undefined` fix, the hasChart override always won and
  // every home-page card showed "Chart coming soon" instead of "View Chart".
  it("shows the chart link for a supported dataset when hasChart is NOT passed", () => {
    const wrapper = factory({ name: "wealth-shares", description: "D" })
    expect(wrapper.html()).toContain("/charts/wealth-shares")
    expect(wrapper.text()).toContain("View Chart")
    expect(wrapper.text()).not.toContain("coming soon")
  })

  it("respects an explicit hasChart=false override for a supported dataset", () => {
    const wrapper = factory({ name: "wealth-shares", description: "D", hasChart: false })
    expect(wrapper.text()).toContain("coming soon")
  })

  it("renders download CSV link", () => {
    const wrapper = factory()
    const downloadLink = wrapper.find("a[download]")
    expect(downloadLink.exists()).toBe(true)
    expect(downloadLink.attributes("href")).toBe("/api/data/wealth-shares/download")
  })

  it("download link has accessible label", () => {
    const wrapper = factory()
    const downloadLink = wrapper.find("a[download]")
    expect(downloadLink.attributes("aria-label")).toBe("Download wealth-shares as CSV")
  })

  it("respects hasChart prop override", () => {
    const wrapper = factory({ name: "unknown", description: "D", hasChart: true })
    expect(wrapper.text()).toContain("View Chart")
  })

  it("renders a details link to the dataset page", () => {
    const wrapper = factory()
    expect(wrapper.text()).toContain("Details")
    expect(wrapper.html()).toContain("/datasets/wealth-shares")
  })

  it("renders a FreshnessIndicator when a freshness entry is provided", () => {
    // Guards the seam the static-freshness fix depends on: a populated store entry
    // (from adaptStaticFreshness in static mode, or the live API) must reach the badge.
    const wrapper = mount(DatasetCard, {
      props: {
        ...defaultProps,
        freshness: { last_updated: "2026-06-14", age_hours: 30, status: "fresh" },
      },
      global: { stubs: { "router-link": routerLinkStub } },
    })
    expect(wrapper.findComponent(FreshnessIndicator).exists()).toBe(true)
    expect(wrapper.text()).toContain("Fresh")
  })

  it("omits the FreshnessIndicator when no freshness entry is provided", () => {
    const wrapper = factory()
    expect(wrapper.findComponent(FreshnessIndicator).exists()).toBe(false)
  })
})
