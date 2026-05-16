import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";
import ChartSkeleton from "../ChartSkeleton.vue";

describe("ChartSkeleton", () => {
  it("renders with animate-pulse class", () => {
    const wrapper = mount(ChartSkeleton);
    expect(wrapper.find(".animate-pulse").exists()).toBe(true);
  });

  it("has accessible role and label", () => {
    const wrapper = mount(ChartSkeleton);
    const el = wrapper.find('[role="status"]');
    expect(el.exists()).toBe(true);
    expect(el.attributes("aria-label")).toBe("Loading chart");
  });

  it("has sr-only loading text", () => {
    const wrapper = mount(ChartSkeleton);
    expect(wrapper.find(".sr-only").text()).toBe("Loading chart data");
  });
});
