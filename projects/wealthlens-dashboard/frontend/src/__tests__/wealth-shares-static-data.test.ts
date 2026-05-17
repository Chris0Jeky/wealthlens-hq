/**
 * Validates the committed wealth-shares static JSON fallback files.
 *
 * These files live in public/data/ and are served as-is by the Vue dev
 * server or GitHub Pages when VITE_STATIC_DATA=true.  The test ensures
 * they are valid JSON with the structure expected by the data store and
 * the WealthSharesChart component.
 *
 * Data source: World Inequality Database (wid.world)
 * Real CSV: projects/wealthlens-dashboard/data/processed/wid_wealth_shares_gb.csv
 * Columns in CSV: variable, country, year, value
 * The generation script derives a 'percentile' field from the variable name.
 */
import { describe, it, expect } from "vitest";
import { readFileSync } from "fs";
import { resolve } from "path";

const PUBLIC_DATA = resolve(__dirname, "../../public/data");

describe("wealth-shares.json static data", () => {
  const raw = readFileSync(resolve(PUBLIC_DATA, "wealth-shares.json"), "utf-8");
  const json = JSON.parse(raw);

  it("is valid JSON with PaginatedResponse structure", () => {
    expect(json).toHaveProperty("data");
    expect(json).toHaveProperty("page");
    expect(json).toHaveProperty("limit");
    expect(json).toHaveProperty("total");
    expect(json).toHaveProperty("total_pages");
  });

  it("has page set to 1 and total_pages set to 1", () => {
    expect(json.page).toBe(1);
    expect(json.total_pages).toBe(1);
  });

  it("total matches data array length", () => {
    expect(json.total).toBe(json.data.length);
    expect(json.limit).toBe(json.data.length);
  });

  it("contains exactly 250 rows (125 per series from real WID data)", () => {
    expect(Array.isArray(json.data)).toBe(true);
    expect(json.data.length).toBe(250);
  });

  it("each row has required fields: variable, percentile, country, year, value", () => {
    for (const row of json.data) {
      expect(row).toHaveProperty("variable");
      expect(row).toHaveProperty("percentile");
      expect(row).toHaveProperty("country");
      expect(row).toHaveProperty("year");
      expect(row).toHaveProperty("value");
    }
  });

  it("variable names are real WID identifiers", () => {
    const variables = new Set(json.data.map((r: { variable: string }) => r.variable));
    expect(variables.size).toBe(2);
    expect(variables.has("shweal_p99p100_992_j")).toBe(true);
    expect(variables.has("shweal_p90p100_992_j")).toBe(true);
  });

  it("percentile values are derived correctly from variable names", () => {
    const percentiles = new Set(json.data.map((r: { percentile: string }) => r.percentile));
    expect(percentiles.size).toBe(2);
    expect(percentiles.has("p99p100")).toBe(true);
    expect(percentiles.has("p90p100")).toBe(true);
  });

  it("year range matches real WID data (1820-2024, with gaps)", () => {
    const years = json.data.map((r: { year: number }) => r.year);
    const minYear = Math.min(...years);
    const maxYear = Math.max(...years);
    expect(minYear).toBe(1820);
    expect(maxYear).toBe(2024);
  });

  it("value is a number between 0 and 1 (wealth share proportion)", () => {
    for (const row of json.data) {
      expect(typeof row.value).toBe("number");
      expect(row.value).toBeGreaterThan(0);
      expect(row.value).toBeLessThanOrEqual(1);
    }
  });

  it("country is GB for all rows", () => {
    for (const row of json.data) {
      expect(row.country).toBe("GB");
    }
  });

  it("has 125 rows per series (matching real WID year coverage)", () => {
    const top1 = json.data.filter((r: { percentile: string }) => r.percentile === "p99p100");
    const top10 = json.data.filter((r: { percentile: string }) => r.percentile === "p90p100");
    expect(top1.length).toBe(125);
    expect(top10.length).toBe(125);
  });

  it("spot-checks match real WID values (not fabricated)", () => {
    // These are known values from wid.world for GB wealth shares
    const top1_1895 = json.data.find(
      (r: { percentile: string; year: number }) => r.percentile === "p99p100" && r.year === 1895,
    );
    // Real WID value is 0.7211, fabricated PR had 0.69
    expect(top1_1895).toBeDefined();
    expect(top1_1895.value).toBeCloseTo(0.7211, 3);

    const top10_1820 = json.data.find(
      (r: { percentile: string; year: number }) => r.percentile === "p90p100" && r.year === 1820,
    );
    // Real WID value is 0.9458
    expect(top10_1820).toBeDefined();
    expect(top10_1820.value).toBeCloseTo(0.9458, 3);

    const top1_2024 = json.data.find(
      (r: { percentile: string; year: number }) => r.percentile === "p99p100" && r.year === 2024,
    );
    // Real WID value is 0.213
    expect(top1_2024).toBeDefined();
    expect(top1_2024.value).toBeCloseTo(0.213, 3);
  });

  it("data has expected gaps (WW1: no 1915-1918, WW2: no 1942-1945)", () => {
    const years = new Set(json.data.map((r: { year: number }) => r.year));
    // WW1 gap
    expect(years.has(1915)).toBe(false);
    expect(years.has(1916)).toBe(false);
    expect(years.has(1917)).toBe(false);
    expect(years.has(1918)).toBe(false);
    // WW2 gap
    expect(years.has(1942)).toBe(false);
    expect(years.has(1943)).toBe(false);
    expect(years.has(1944)).toBe(false);
    expect(years.has(1945)).toBe(false);
  });
});

describe("wealth-shares-metadata.json static data", () => {
  const raw = readFileSync(resolve(PUBLIC_DATA, "wealth-shares-metadata.json"), "utf-8");
  const json = JSON.parse(raw);

  it("is valid JSON with DatasetMetadata structure", () => {
    expect(json).toHaveProperty("name");
    expect(json).toHaveProperty("description");
    expect(json).toHaveProperty("source");
    expect(json).toHaveProperty("source_url");
    expect(json).toHaveProperty("access_date");
    expect(json).toHaveProperty("row_count");
    expect(json).toHaveProperty("columns");
  });

  it("name is wealth-shares", () => {
    expect(json.name).toBe("wealth-shares");
  });

  it("source cites World Inequality Database", () => {
    expect(json.source).toBe("World Inequality Database");
  });

  it("source_url points to wid.world", () => {
    expect(json.source_url).toContain("wid.world");
  });

  it("access_date is a valid ISO date", () => {
    expect(json.access_date).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  });

  it("row_count matches the data file (250 rows)", () => {
    const dataRaw = readFileSync(resolve(PUBLIC_DATA, "wealth-shares.json"), "utf-8");
    const dataJson = JSON.parse(dataRaw);
    expect(json.row_count).toBe(dataJson.total);
    expect(json.row_count).toBe(250);
  });

  it("columns lists all fields including derived percentile", () => {
    expect(Array.isArray(json.columns)).toBe(true);
    expect(json.columns).toContain("variable");
    expect(json.columns).toContain("country");
    expect(json.columns).toContain("year");
    expect(json.columns).toContain("value");
    expect(json.columns).toContain("percentile");
  });
});
