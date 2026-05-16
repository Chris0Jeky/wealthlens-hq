import { describe, it, expect } from "vitest";
import { mount, RouterLinkStub } from "@vue/test-utils";
import DatasetCard from "@/components/DatasetCard.vue";

describe("DatasetCard", () => {
  const defaultProps = {
    name: "wealth-distribution",
    description: "UK household wealth by decile, 2020-2022",
  };

  it("renders the name prop", () => {
    const wrapper = mount(DatasetCard, { props: defaultProps });
    expect(wrapper.text()).toContain(defaultProps.name);
  });

  it("renders the description prop", () => {
    const wrapper = mount(DatasetCard, { props: defaultProps });
    expect(wrapper.text()).toContain(defaultProps.description);
  });

  it("uses an h3 for the dataset name", () => {
    const wrapper = mount(DatasetCard, { props: defaultProps });
    const heading = wrapper.find("h3");
    expect(heading.exists()).toBe(true);
    expect(heading.text()).toBe(defaultProps.name);
  });

  it("uses a paragraph for the description", () => {
    const wrapper = mount(DatasetCard, { props: defaultProps });
    const paragraph = wrapper.find("p");
    expect(paragraph.exists()).toBe(true);
    expect(paragraph.text()).toBe(defaultProps.description);
  });

  it("uses a semantic article element with aria-label", () => {
    const wrapper = mount(DatasetCard, { props: defaultProps });
    expect(wrapper.element.tagName).toBe("ARTICLE");
    expect(wrapper.attributes("aria-label")).toBe(
      `Dataset: ${defaultProps.name}`,
    );
  });

  it("renders view-chart link with aria-label when chart is available", () => {
    const wrapper = mount(DatasetCard, {
      props: { ...defaultProps, hasChart: true },
      global: { stubs: { RouterLink: RouterLinkStub } },
    });
    const link = wrapper.findComponent(RouterLinkStub);
    expect(link.exists()).toBe(true);
    expect(link.attributes("aria-label")).toBe(
      `View ${defaultProps.name} chart`,
    );
  });
});
