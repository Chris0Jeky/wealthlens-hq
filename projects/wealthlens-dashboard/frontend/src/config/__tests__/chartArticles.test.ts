import { describe, it, expect } from "vitest";
import { chartConfigs } from "../chartArticles";
import { COLOR_TOP_10, COLOR_TOP_1 } from "../chartColors";

/**
 * Guards the wealth-shares toolbar legend against re-drifting away from the
 * chart. WealthSharesChart.vue plots exactly two WID series — top 10%
 * (p90p100) and top 1% (p99p100) — both coloured from the SHARED constants in
 * config/chartColors.ts, which this test also imports. So the toolbar legend
 * must list those two series, in that order, using those exact shared colours,
 * and nothing else. (It previously listed four series with the wrong colours,
 * showing legend dots for lines that are never drawn.)
 *
 * Because the assertion binds to the same COLOR_TOP_10 / COLOR_TOP_1 the chart
 * uses (not copied literals), a future colour change on the chart side forces
 * the toolbar and this test to move together — a true cross-file guard.
 */
describe("chartArticles: wealth-shares toolbar legend", () => {
  const series = chartConfigs["wealth-shares"].toolbar?.series ?? [];

  it("lists exactly the two series the chart actually plots", () => {
    expect(series.map((s) => s.label)).toEqual(["Top 10%", "Top 1%"]);
  });

  it("uses the chart's shared series colours, not the broadsheet ink palette", () => {
    expect(series.map((s) => s.color)).toEqual([COLOR_TOP_10, COLOR_TOP_1]);
  });
});
