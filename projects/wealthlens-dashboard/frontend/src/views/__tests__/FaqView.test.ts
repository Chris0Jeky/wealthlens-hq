import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import FaqView from "../FaqView.vue";

describe("FaqView", () => {
  it("renders FAQ heading", () => {
    const wrapper = mount(FaqView);
    expect(wrapper.find("h1").text()).toContain("FAQ & Glossary");
  });

  it("renders all FAQ questions as accordion buttons", () => {
    const wrapper = mount(FaqView);
    const buttons = wrapper.findAll("button[type='button']");
    expect(buttons.length).toBeGreaterThanOrEqual(8);
  });

  it("toggles FAQ answer visibility on click", async () => {
    const wrapper = mount(FaqView);
    const firstButton = wrapper.find("button[type='button']");

    expect(firstButton.attributes("aria-expanded")).toBe("false");

    await firstButton.trigger("click");
    expect(firstButton.attributes("aria-expanded")).toBe("true");

    await firstButton.trigger("click");
    expect(firstButton.attributes("aria-expanded")).toBe("false");
  });

  it("renders glossary terms in a definition list", () => {
    const wrapper = mount(FaqView);
    const terms = wrapper.findAll("dt");
    expect(terms.length).toBeGreaterThanOrEqual(10);
    expect(terms[0].text()).toBe("Decile");
  });

  it("uses proper heading hierarchy for accessibility", () => {
    const wrapper = mount(FaqView);
    expect(wrapper.find("h1").exists()).toBe(true);
    expect(wrapper.findAll("h2").length).toBe(2);
    expect(wrapper.findAll("h3").length).toBeGreaterThanOrEqual(8);
  });

  it("has accessible accordion structure with aria-controls and aria-expanded", () => {
    const wrapper = mount(FaqView);
    const buttons = wrapper.findAll("button[type='button']");
    buttons.forEach((btn) => {
      expect(btn.attributes("aria-expanded")).toBeDefined();
      expect(btn.attributes("aria-controls")).toBeDefined();
    });
  });
});
