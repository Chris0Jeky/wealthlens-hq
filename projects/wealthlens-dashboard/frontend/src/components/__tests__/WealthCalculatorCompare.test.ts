import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import WealthCalculator from "@/components/WealthCalculator.vue";

/**
 * Tests for the WealthCalculator comparison mode feature.
 *
 * Verifies that:
 * - The mode toggle switches between single and compare UI
 * - Both inputs calculate independently in compare mode
 * - Comparison results show correct difference text
 * - Presets populate both fields correctly
 * - Accessibility attributes are present (tablist, tab, aria-selected)
 */

/** Mount helper with stubs for router-link if needed */
function mountCalc() {
  return mount(WealthCalculator, {
    global: {
      stubs: {
        "router-link": true,
      },
    },
  });
}

describe("WealthCalculator — mode toggle", () => {
  it("renders in single mode by default", () => {
    const wrapper = mountCalc();
    const singlePanel = wrapper.find("#panel-single");
    const comparePanel = wrapper.find("#panel-compare");
    expect(singlePanel.attributes("hidden")).toBeUndefined();
    expect(comparePanel.attributes("hidden")).toBeDefined();
  });

  it("has a tablist with two tabs", () => {
    const wrapper = mountCalc();
    const tablist = wrapper.find('[role="tablist"]');
    expect(tablist.exists()).toBe(true);
    const tabs = tablist.findAll('[role="tab"]');
    expect(tabs).toHaveLength(2);
  });

  it("marks single tab as selected by default", () => {
    const wrapper = mountCalc();
    const singleTab = wrapper.find("#tab-single");
    const compareTab = wrapper.find("#tab-compare");
    expect(singleTab.attributes("aria-selected")).toBe("true");
    expect(compareTab.attributes("aria-selected")).toBe("false");
  });

  it("switches to compare mode when compare tab is clicked", async () => {
    const wrapper = mountCalc();
    const compareTab = wrapper.find("#tab-compare");
    await compareTab.trigger("click");

    const singlePanel = wrapper.find("#panel-single");
    const comparePanel = wrapper.find("#panel-compare");
    expect(singlePanel.attributes("hidden")).toBeDefined();
    expect(comparePanel.attributes("hidden")).toBeUndefined();

    // Tab aria-selected updates
    expect(wrapper.find("#tab-single").attributes("aria-selected")).toBe("false");
    expect(wrapper.find("#tab-compare").attributes("aria-selected")).toBe("true");
  });

  it("switches back to single mode when single tab is clicked", async () => {
    const wrapper = mountCalc();

    // Go to compare
    await wrapper.find("#tab-compare").trigger("click");
    expect(wrapper.find("#panel-compare").attributes("hidden")).toBeUndefined();

    // Go back to single
    await wrapper.find("#tab-single").trigger("click");
    expect(wrapper.find("#panel-single").attributes("hidden")).toBeUndefined();
    expect(wrapper.find("#panel-compare").attributes("hidden")).toBeDefined();
  });
});

describe("WealthCalculator — compare mode inputs", () => {
  it("renders two input fields in compare mode", async () => {
    const wrapper = mountCalc();
    await wrapper.find("#tab-compare").trigger("click");

    const inputA = wrapper.find("#compare-input-a");
    const inputB = wrapper.find("#compare-input-b");
    expect(inputA.exists()).toBe(true);
    expect(inputB.exists()).toBe(true);
  });

  it("both inputs have associated labels", async () => {
    const wrapper = mountCalc();
    await wrapper.find("#tab-compare").trigger("click");

    const labelA = wrapper.find('label[for="compare-input-a"]');
    const labelB = wrapper.find('label[for="compare-input-b"]');
    expect(labelA.exists()).toBe(true);
    expect(labelB.exists()).toBe(true);
    expect(labelA.text()).toContain("Amount A");
    expect(labelB.text()).toContain("Amount B");
  });

  it("both inputs have aria-describedby", async () => {
    const wrapper = mountCalc();
    await wrapper.find("#tab-compare").trigger("click");

    const inputA = wrapper.find("#compare-input-a");
    const inputB = wrapper.find("#compare-input-b");
    expect(inputA.attributes("aria-describedby")).toBe("compare-input-a-help");
    expect(inputB.attributes("aria-describedby")).toBe("compare-input-b-help");
  });

  it("compare button is disabled when inputs are invalid", async () => {
    const wrapper = mountCalc();
    await wrapper.find("#tab-compare").trigger("click");

    // Set invalid (non-numeric) values
    await wrapper.find("#compare-input-a").setValue("abc");
    await wrapper.find("#compare-input-b").setValue("xyz");

    const btn = wrapper.find(".calc__btn--compare");
    expect(btn.attributes("disabled")).toBeDefined();
  });

  it("compare button stays disabled when inputs are blank", async () => {
    const wrapper = mountCalc();
    await wrapper.find("#tab-compare").trigger("click");

    await wrapper.find("#compare-input-a").setValue("");
    await wrapper.find("#compare-input-b").setValue("");

    const btn = wrapper.find(".calc__btn--compare");
    expect(btn.attributes("disabled")).toBeDefined();
  });

  it("compare button enables when both inputs have valid values", async () => {
    const wrapper = mountCalc();
    await wrapper.find("#tab-compare").trigger("click");

    await wrapper.find("#compare-input-a").setValue("100,000");
    await wrapper.find("#compare-input-b").setValue("500,000");

    const btn = wrapper.find(".calc__btn--compare");
    expect(btn.attributes("disabled")).toBeUndefined();
  });
});

describe("WealthCalculator — compare mode results", () => {
  async function setupComparison(
    wrapper: ReturnType<typeof mountCalc>,
    valueA: string,
    valueB: string,
  ) {
    await wrapper.find("#tab-compare").trigger("click");
    await wrapper.find("#compare-input-a").setValue(valueA);
    await wrapper.find("#compare-input-b").setValue(valueB);
    await wrapper.find(".calc__btn--compare").trigger("click");
  }

  it("shows results after clicking compare with valid inputs", async () => {
    const wrapper = mountCalc();
    await setupComparison(wrapper, "100000", "500000");

    const results = wrapper.find('[aria-label="Comparison results"]');
    expect(results.exists()).toBe(true);
  });

  it("shows correct comparison summary for different deciles", async () => {
    const wrapper = mountCalc();
    // 100,000 = decile 3, 500,000 = decile 7
    await setupComparison(wrapper, "100000", "500000");

    const summary = wrapper.find(".calc__compare-summary");
    expect(summary.exists()).toBe(true);
    expect(summary.text()).toContain("Amount B is 4 deciles higher than Amount A");
  });

  it("shows same-decile message when both are in same decile", async () => {
    const wrapper = mountCalc();
    // Both in decile 5: 200,000 and 250,000
    await setupComparison(wrapper, "200000", "250000");

    const summary = wrapper.find(".calc__compare-summary");
    expect(summary.text()).toContain("same decile");
  });

  it("shows correct difference when A is higher than B", async () => {
    const wrapper = mountCalc();
    // 1,500,000 = decile 10, 100,000 = decile 3
    await setupComparison(wrapper, "1500000", "100000");

    const summary = wrapper.find(".calc__compare-summary");
    expect(summary.text()).toContain("Amount A is 7 deciles higher than Amount B");
  });

  it("displays both amounts in the stat grid", async () => {
    const wrapper = mountCalc();
    await setupComparison(wrapper, "100000", "500000");

    const statValues = wrapper.findAll(".calc__stat-value");
    const texts = statValues.map((s) => s.text());
    // Should contain formatted versions of both amounts
    expect(texts.some((t) => t.includes("100,000"))).toBe(true);
    expect(texts.some((t) => t.includes("500,000"))).toBe(true);
  });

  it("displays wealth difference", async () => {
    const wrapper = mountCalc();
    await setupComparison(wrapper, "100000", "500000");

    const statLabels = wrapper.findAll(".calc__stat-label");
    const diffLabel = statLabels.find((l) => l.text().includes("Wealth difference"));
    expect(diffLabel).toBeDefined();
  });

  it("shows dual markers on the decile bar", async () => {
    const wrapper = mountCalc();
    // Decile 3 and decile 7 — different deciles
    await setupComparison(wrapper, "100000", "500000");

    const markerA = wrapper.find(".calc__bar-marker--a");
    const markerB = wrapper.find(".calc__bar-marker--b");
    expect(markerA.exists()).toBe(true);
    expect(markerB.exists()).toBe(true);
  });

  it("shows combined marker when both values are in same decile", async () => {
    const wrapper = mountCalc();
    await setupComparison(wrapper, "200000", "250000");

    const markerBoth = wrapper.find(".calc__bar-marker--both");
    expect(markerBoth.exists()).toBe(true);
  });

  it("has aria-live polite on results section", async () => {
    const wrapper = mountCalc();
    await setupComparison(wrapper, "100000", "500000");

    const results = wrapper.find('[aria-live="polite"]');
    expect(results.exists()).toBe(true);
  });

  it("includes source citation in compare results", async () => {
    const wrapper = mountCalc();
    await setupComparison(wrapper, "100000", "500000");

    const source = wrapper.find(".calc__source");
    expect(source.exists()).toBe(true);
    expect(source.text()).toContain("ONS");
  });
});

describe("WealthCalculator — compare presets", () => {
  it("renders comparison preset buttons", async () => {
    const wrapper = mountCalc();
    await wrapper.find("#tab-compare").trigger("click");

    const presets = wrapper.find('[aria-label="Comparison presets"]');
    expect(presets.exists()).toBe(true);

    const buttons = presets.findAll("button");
    expect(buttons.length).toBeGreaterThanOrEqual(3);
  });

  it("Median vs Top 10% preset populates both fields", async () => {
    const wrapper = mountCalc();
    await wrapper.find("#tab-compare").trigger("click");

    const presetBtn = wrapper
      .findAll('[aria-label="Comparison presets"] button')
      .find((b) => b.text().includes("Median vs Top 10%"));
    expect(presetBtn).toBeDefined();
    await presetBtn!.trigger("click");

    const inputA = wrapper.find("#compare-input-a");
    const inputB = wrapper.find("#compare-input-b");
    expect((inputA.element as HTMLInputElement).value).toContain("302,500");
    expect((inputB.element as HTMLInputElement).value).toContain("1,480,000");
  });

  it("Renter vs Homeowner preset populates both fields", async () => {
    const wrapper = mountCalc();
    await wrapper.find("#tab-compare").trigger("click");

    const presetBtn = wrapper
      .findAll('[aria-label="Comparison presets"] button')
      .find((b) => b.text().includes("Renter vs Homeowner"));
    expect(presetBtn).toBeDefined();
    await presetBtn!.trigger("click");

    const inputA = wrapper.find("#compare-input-a");
    const inputB = wrapper.find("#compare-input-b");
    expect((inputA.element as HTMLInputElement).value).toContain("5,000");
    expect((inputB.element as HTMLInputElement).value).toContain("302,500");
  });

  it("With vs Without Pension preset populates both fields", async () => {
    const wrapper = mountCalc();
    await wrapper.find("#tab-compare").trigger("click");

    const presetBtn = wrapper
      .findAll('[aria-label="Comparison presets"] button')
      .find((b) => b.text().includes("With vs Without Pension"));
    expect(presetBtn).toBeDefined();
    await presetBtn!.trigger("click");

    const inputA = wrapper.find("#compare-input-a");
    const inputB = wrapper.find("#compare-input-b");
    expect((inputA.element as HTMLInputElement).value).toContain("302,500");
    expect((inputB.element as HTMLInputElement).value).toContain("175,000");
  });
});

describe("WealthCalculator — single mode still works", () => {
  it("single mode calculate still works after switching modes", async () => {
    const wrapper = mountCalc();

    // Switch to compare and back
    await wrapper.find("#tab-compare").trigger("click");
    await wrapper.find("#tab-single").trigger("click");

    // Use single mode
    await wrapper.find("#wealth-input").setValue("302500");
    await wrapper.find(".calc__btn:not(.calc__btn--compare)").trigger("click");

    const results = wrapper.find('[aria-label="Your wealth position"]');
    expect(results.exists()).toBe(true);
  });
});
