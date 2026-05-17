import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import TaxCalculator from "@/components/TaxCalculator.vue";

describe("TaxCalculator", () => {
  it("renders the page title", () => {
    const wrapper = mount(TaxCalculator);
    expect(wrapper.find("h1").text()).toContain("tax rate");
  });

  it("renders the salary input with label", () => {
    const wrapper = mount(TaxCalculator);
    const label = wrapper.find('label[for="salary-input"]');
    expect(label.exists()).toBe(true);
    expect(label.text()).toContain("annual gross salary");
    const input = wrapper.find("#salary-input");
    expect(input.exists()).toBe(true);
  });

  it("states the income tax jurisdiction scope", () => {
    const wrapper = mount(TaxCalculator);
    expect(wrapper.text()).toContain("England, Wales, and Northern Ireland");
    expect(wrapper.text()).toContain("Scottish Income Tax uses");
  });

  it("disables calculate button when input is empty", () => {
    const wrapper = mount(TaxCalculator);
    const btn = wrapper.find("button.calc__btn");
    expect((btn.element as HTMLButtonElement).disabled).toBe(true);
  });

  it("enables calculate button when valid number is entered", async () => {
    const wrapper = mount(TaxCalculator);
    const input = wrapper.find("#salary-input");
    await input.setValue("50000");
    const btn = wrapper.find("button.calc__btn");
    expect(btn.attributes("disabled")).toBeUndefined();
  });

  it("shows results after clicking calculate", async () => {
    const wrapper = mount(TaxCalculator);
    const input = wrapper.find("#salary-input");
    await input.setValue("50000");
    const btn = wrapper.find("button.calc__btn");
    await btn.trigger("click");
    expect(wrapper.find(".calc__results").exists()).toBe(true);
  });

  it("shows breakdown table with tax bands", async () => {
    const wrapper = mount(TaxCalculator);
    const input = wrapper.find("#salary-input");
    await input.setValue("80000");
    await wrapper.find("button.calc__btn").trigger("click");
    const rows = wrapper.findAll(".calc__table tbody tr");
    expect(rows.length).toBeGreaterThan(0);
  });

  it("shows capital gains comparison", async () => {
    const wrapper = mount(TaxCalculator);
    await wrapper.find("#salary-input").setValue("80000");
    await wrapper.find("button.calc__btn").trigger("click");
    expect(wrapper.find(".calc__comparison").exists()).toBe(true);
    expect(wrapper.find(".calc__comparison-text").text()).toContain("capital gains");
    expect(wrapper.find(".calc__comparison-note").text()).toContain("2026-27");
  });

  it("applies preset value when preset button is clicked", async () => {
    const wrapper = mount(TaxCalculator);
    const presets = wrapper.findAll(".calc__presets .wl-btn--ghost");
    await presets[0].trigger("click");
    const input = wrapper.find("#salary-input");
    expect((input.element as HTMLInputElement).value).toBe("25,000");
  });

  it("shows error message for invalid input", async () => {
    const wrapper = mount(TaxCalculator);
    await wrapper.find("#salary-input").setValue("abc");
    expect(wrapper.find(".calc__error").exists()).toBe(true);
  });

  it("hides results initially", () => {
    const wrapper = mount(TaxCalculator);
    expect(wrapper.find(".calc__results").exists()).toBe(false);
  });

  it("resets when 'Try another salary' is clicked", async () => {
    const wrapper = mount(TaxCalculator);
    await wrapper.find("#salary-input").setValue("50000");
    await wrapper.find("button.calc__btn").trigger("click");
    expect(wrapper.find(".calc__results").exists()).toBe(true);
    await wrapper.find(".calc__reset").trigger("click");
    expect(wrapper.find(".calc__results").exists()).toBe(false);
  });

  it("handles input with £ and commas", async () => {
    const wrapper = mount(TaxCalculator);
    await wrapper.find("#salary-input").setValue("£80,000");
    await wrapper.find("button.calc__btn").trigger("click");
    expect(wrapper.find(".calc__results").exists()).toBe(true);
  });

  it("has proper aria attributes for accessibility", () => {
    const wrapper = mount(TaxCalculator);
    const input = wrapper.find("#salary-input");
    expect(input.attributes("aria-describedby")).toBe("salary-input-help");
    expect(input.attributes("inputmode")).toBe("numeric");
  });
});
