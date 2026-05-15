import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
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

  it("has a root div wrapper", () => {
    const wrapper = mount(DatasetCard, { props: defaultProps });
    expect(wrapper.element.tagName).toBe("DIV");
  });
});
