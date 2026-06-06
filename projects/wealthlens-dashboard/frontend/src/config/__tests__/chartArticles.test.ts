import { describe, it, expect } from "vitest";
import { chartConfigs } from "../chartArticles";

/**
 * Guards the wealth-shares toolbar legend against re-drifting away from the
 * chart. WealthSharesChart.vue plots exactly two WID series — top 10%
 * (p90p100, COLOR_TOP_10 #1a56db) and top 1% (p99p100, COLOR_TOP_1 #dc2626) —
 * so the broadsheet toolbar legend above it must list those two, in those
 * colours, and nothing else. (It previously listed four series with the wrong
 * colours, showing legend dots for lines that are never drawn.)
 */
describe("chartArticles: wealth-shares toolbar legend", () => {
  const series = chartConfigs["wealth-shares"].toolbar?.series ?? [];

  it("lists exactly the two series the chart actually plots", () => {
    expect(series.map((s) => s.label)).toEqual(["Top 10%", "Top 1%"]);
  });

  it("uses the chart's series colours, not the broadsheet ink palette", () => {
    expect(series.map((s) => s.color)).toEqual(["#1a56db", "#dc2626"]);
  });
});
