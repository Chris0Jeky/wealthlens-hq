import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import WealthTaxSimulator from "@/components/WealthTaxSimulator.vue";

/**
 * Stub router-link to avoid needing a full router in tests.
 * The component itself does not use router-link, but its parent view does.
 */
const globalStubs = {
  "router-link": { template: "<a><slot /></a>" },
};

describe("WealthTaxSimulator", () => {
  it("renders with initial state showing results", () => {
    const wrapper = mount(WealthTaxSimulator, {
      global: { stubs: globalStubs },
    });
    // Title is present
    expect(wrapper.find("h1").text()).toContain("Wealth Tax");
    expect(wrapper.find("h1").text()).toContain("Revenue Simulator");
  });

  it("displays the three preset buttons", () => {
    const wrapper = mount(WealthTaxSimulator, {
      global: { stubs: globalStubs },
    });
    const presetButtons = wrapper.findAll("[aria-label='Preset scenario buttons'] button");
    expect(presetButtons.length).toBe(3);
    expect(presetButtons[0].text()).toContain("Modest");
    expect(presetButtons[1].text()).toContain("Moderate");
    expect(presetButtons[2].text()).toContain("Ambitious");
  });

  it("displays simulation results on initial render", () => {
    const wrapper = mount(WealthTaxSimulator, {
      global: { stubs: globalStubs },
    });
    // Results section should be visible (always computed reactively)
    const results = wrapper.find("[aria-label='Simulation results']");
    expect(results.exists()).toBe(true);
    // Revenue headline should contain a pound sign
    const revenue = wrapper.find(".sim__revenue");
    expect(revenue.exists()).toBe(true);
    expect(revenue.text()).toContain("£");
  });

  it("preset buttons populate sliders and update results", async () => {
    const wrapper = mount(WealthTaxSimulator, {
      global: { stubs: globalStubs },
    });

    // Click "Ambitious" preset (3 bands)
    const presetButtons = wrapper.findAll("[aria-label='Preset scenario buttons'] button");
    await presetButtons[2].trigger("click");

    // Should now have 3 bands
    const bands = wrapper.findAll(".sim__band");
    expect(bands.length).toBe(3);

    // The "Ambitious" button should be marked as active/pressed
    expect(presetButtons[2].attributes("aria-pressed")).toBe("true");
  });

  it("add band button creates a new band", async () => {
    const wrapper = mount(WealthTaxSimulator, {
      global: { stubs: globalStubs },
    });

    // Initially 1 band
    let bands = wrapper.findAll(".sim__band");
    expect(bands.length).toBe(1);

    // Click add band
    const addBtn = wrapper.find(".sim__add-band");
    expect(addBtn.exists()).toBe(true);
    await addBtn.trigger("click");

    // Now 2 bands
    bands = wrapper.findAll(".sim__band");
    expect(bands.length).toBe(2);
  });

  it("remove band button removes a band", async () => {
    const wrapper = mount(WealthTaxSimulator, {
      global: { stubs: globalStubs },
    });

    // Add a band first
    const addBtn = wrapper.find(".sim__add-band");
    await addBtn.trigger("click");
    expect(wrapper.findAll(".sim__band").length).toBe(2);

    // Remove the second band
    const removeBtn = wrapper.find("[aria-label='Remove band 2']");
    expect(removeBtn.exists()).toBe(true);
    await removeBtn.trigger("click");

    expect(wrapper.findAll(".sim__band").length).toBe(1);
  });

  it("cannot add more than 3 bands", async () => {
    const wrapper = mount(WealthTaxSimulator, {
      global: { stubs: globalStubs },
    });

    // Add to max
    let addBtn = wrapper.find(".sim__add-band");
    await addBtn.trigger("click"); // 2 bands
    addBtn = wrapper.find(".sim__add-band");
    await addBtn.trigger("click"); // 3 bands

    // Add band button should no longer exist
    addBtn = wrapper.find(".sim__add-band");
    expect(addBtn.exists()).toBe(false);
  });

  it("has accessible slider labels", () => {
    const wrapper = mount(WealthTaxSimulator, {
      global: { stubs: globalStubs },
    });
    // Threshold slider has a label
    const thresholdLabel = wrapper.find("label[for='threshold-0']");
    expect(thresholdLabel.exists()).toBe(true);
    expect(thresholdLabel.text()).toContain("Threshold");

    // Rate slider has a label
    const rateLabel = wrapper.find("label[for='rate-0']");
    expect(rateLabel.exists()).toBe(true);
    expect(rateLabel.text()).toContain("Rate");
  });

  it("sliders have aria-valuetext attributes", () => {
    const wrapper = mount(WealthTaxSimulator, {
      global: { stubs: globalStubs },
    });
    const thresholdSlider = wrapper.find("#threshold-0");
    expect(thresholdSlider.attributes("aria-valuetext")).toBeTruthy();

    const rateSlider = wrapper.find("#rate-0");
    expect(rateSlider.attributes("aria-valuetext")).toBeTruthy();
  });

  it("results update reactively when slider changes", async () => {
    const wrapper = mount(WealthTaxSimulator, {
      global: { stubs: globalStubs },
    });

    // Get initial revenue text
    const initialRevenue = wrapper.find(".sim__revenue").text();

    // Click "Ambitious" which adds more bands at higher rates
    const presetButtons = wrapper.findAll("[aria-label='Preset scenario buttons'] button");
    await presetButtons[2].trigger("click");

    // Revenue should be different (higher)
    const newRevenue = wrapper.find(".sim__revenue").text();
    expect(newRevenue).not.toBe(initialRevenue);
  });

  it("displays the disclaimer text", () => {
    const wrapper = mount(WealthTaxSimulator, {
      global: { stubs: globalStubs },
    });
    const disclaimer = wrapper.find(".sim__disclaimer-text");
    expect(disclaimer.exists()).toBe(true);
    expect(disclaimer.text()).toContain("simplified model");
  });

  it("displays source citations with links", () => {
    const wrapper = mount(WealthTaxSimulator, {
      global: { stubs: globalStubs },
    });
    const links = wrapper.findAll(".sim__source-detail a");
    expect(links.length).toBeGreaterThanOrEqual(2);
    // First link should point to ONS
    expect(links[0].attributes("href")).toContain("ons.gov.uk");
    // Second link should point to wealth tax commission
    expect(links[1].attributes("href")).toContain("ukwealth.tax");
  });

  it("has aria-live on results section for screen reader updates", () => {
    const wrapper = mount(WealthTaxSimulator, {
      global: { stubs: globalStubs },
    });
    const results = wrapper.find("[aria-live='polite']");
    expect(results.exists()).toBe(true);
  });
});
