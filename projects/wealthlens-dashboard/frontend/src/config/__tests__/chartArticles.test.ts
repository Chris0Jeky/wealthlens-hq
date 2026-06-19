import { readFileSync } from "node:fs";
import { resolve } from "node:path";
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

/**
 * Data-integrity guard for the wealth-shares stat cards + narrative.
 *
 * The page once carried headline numbers ("Top 1% alone: 28%", "Postwar low
 * 1980: 50%", lede "we're now at 1910 levels") that the WID series the chart
 * actually plots does NOT support (top 1% 2024 ≈ 21%, the all-time low was ≈ 52%
 * in 1990, and 1910 was ≈ 94%). This test recomputes the card figures straight
 * from public/data/wealth-shares.json — the same file the chart loads — so the
 * cards and the plotted data are forced to move together, and the discredited
 * claims cannot creep back. (Per the data-integrity guardrail: every figure
 * must match its source.)
 */
describe("chartArticles: wealth-shares stat cards match the WID series", () => {
  type Row = { year: number; value: number; percentile: string };
  // vitest runs with the frontend package dir as cwd, where the chart's data
  // file lives under public/ — the same file WealthSharesChart.vue fetches.
  const raw = readFileSync(
    resolve(process.cwd(), "public/data/wealth-shares.json"),
    "utf8",
  );
  const rows: Row[] = JSON.parse(raw).data;
  const byPct = (p: string) =>
    rows.filter((r) => r.percentile === p).sort((a, b) => a.year - b.year);
  const top10 = byPct("p90p100");
  const top1 = byPct("p99p100");
  const latestYear = top10[top10.length - 1].year;
  const top10Latest = top10[top10.length - 1].value;
  const top1Latest = top1[top1.length - 1].value;
  // All-time low of the top-10% share (the "postwar low" / least-concentrated).
  // The strict `<` keeps the FIRST occurrence on a tie: 1990 and 1991 are both
  // 51.6%, so the card's "(1990)" label is the earlier of the tied minima.
  const low = top10.reduce((m, r) => (r.value < m.value ? r : m), top10[0]);

  const cfg = chartConfigs["wealth-shares"];
  const cardByLabelPrefix = (prefix: string) =>
    (cfg.stats ?? []).find((s) => s.label.startsWith(prefix));

  it("reflects the latest plotted year (2024) and its top-10% share", () => {
    expect(latestYear).toBe(2024);
    const headline = (cfg.stats ?? []).find((s) => s.headline);
    expect(headline?.value).toBe(String(Math.round(top10Latest * 100)));
    expect(headline?.description).toContain(String(latestYear));
  });

  it("top-1% card equals the WID p99p100 latest value", () => {
    expect(cardByLabelPrefix("Top 1%")?.value).toBe(
      String(Math.round(top1Latest * 100)),
    );
  });

  it("bottom-90% card equals 100 minus the top-10% share", () => {
    expect(cardByLabelPrefix("Bottom 90%")?.value).toBe(
      String(Math.round((1 - top10Latest) * 100)),
    );
  });

  it("postwar-low card matches the series minimum and its year", () => {
    const card = cardByLabelPrefix("Postwar low");
    expect(card?.value).toBe(String(Math.round(low.value * 100)));
    expect(card?.label).toContain(String(low.year));
  });

  it("meta 'Data points' equals the plotted row count", () => {
    const dataPoints = cfg.meta.find((m) => m.label === "Data points");
    expect(dataPoints?.value).toBe(String(rows.length));
  });

  it("no longer carries the discredited '1910 levels' lede claim", () => {
    // The per-card recompute assertions above already pin the values to the
    // series (so the old 28% / 50% cards cannot return). This guards the one
    // claim with no card to anchor it: the false "now at 1910 levels" lede
    // (top 10% was ~94% in 1910, not ~57%).
    expect(cfg.lede).not.toContain("1910 levels");
  });
});
