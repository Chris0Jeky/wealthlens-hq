import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import FaqView from "../FaqView.vue";

describe("FaqView", () => {
  it("renders FAQ heading", () => {
    const wrapper = mount(FaqView);
    expect(wrapper.find("h1").text()).toContain("FAQ & Glossary");
  });

  it("renders all FAQ questions as buttons", () => {
    const wrapper = mount(FaqView);
    const buttons = wrapper.findAll("button");
    expect(buttons.length).toBeGreaterThanOrEqual(8);
  });

  it("toggles FAQ answer visibility on click", async () => {
    const wrapper = mount(FaqView);
    const firstButton = wrapper.find("button");
    const answerId = firstButton.attributes("aria-controls");

    expect(firstButton.attributes("aria-expanded")).toBe("false");

    await firstButton.trigger("click");
    expect(firstButton.attributes("aria-expanded")).toBe("true");

    await firstButton.trigger("click");
    expect(firstButton.attributes("aria-expanded")).toBe("false");
  });

  it("renders glossary terms", () => {
    const wrapper = mount(FaqView);
    const terms = wrapper.findAll("dt");
    expect(terms.length).toBeGreaterThanOrEqual(10);
    expect(terms[0].text()).toBe("Decile");
  });

  it("has accessible FAQ structure with aria-controls", () => {
    const wrapper = mount(FaqView);
    const buttons = wrapper.findAll("button");
    buttons.forEach((btn) => {
      expect(btn.attributes("aria-expanded")).toBeDefined();
      expect(btn.attributes("aria-controls")).toMatch(/^faq-answer-\d+$/);
    });
  });
});
