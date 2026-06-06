import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { VALID_CHART_NAMES } from "@/constants/charts";

const here = dirname(fileURLToPath(import.meta.url));

// Resolve relative to THIS file (not process.cwd()) so the test passes regardless of
// which directory the runner is invoked from (repo root vs frontend).
function loadFreshness(): Record<string, unknown> {
  const path = resolve(here, "../../../public/data/freshness.json");
  return JSON.parse(readFileSync(path, "utf-8")) as Record<string, unknown>;
}

/**
 * Contract test for the committed static freshness.json.
 *
 * This is the artifact DataFreshnessBadge + useDataFreshness consume in static
 * (GitHub Pages) mode. It MUST use the flat per-slug schema parseDateOnly accepts —
 * `{ "<slug>": { last_updated: "YYYY-MM-DD", source: "..." } }` — and NOT the live
 * /api/data/freshness shape (`{ datasets: {...}, thresholds: {...} }`, ISO datetimes).
 *
 * An earlier generate_static_api.py emitted the live shape into this same path on
 * every deploy, which silently broke every freshness badge (the flat lookup
 * `data[slug]` missed the nested object, and parseDateOnly rejected the ISO dates).
 * The generator no longer writes this file; this test locks the schema so a future
 * regression (a generator re-add, or hand-edit drift) fails in CI rather than on the
 * live site.
 */
describe("committed public/data/freshness.json contract", () => {
  it("is a flat slug map of { last_updated: YYYY-MM-DD, source }", () => {
    const data = loadFreshness();

    // Not the live-API nested shape.
    expect(data.datasets).toBeUndefined();
    expect(data.thresholds).toBeUndefined();

    const entries = Object.entries(data);
    expect(entries.length).toBeGreaterThan(0);
    for (const [slug, entry] of entries) {
      expect(entry, `entry for ${slug}`).toMatchObject({
        last_updated: expect.stringMatching(/^\d{4}-\d{2}-\d{2}$/),
        source: expect.any(String),
      });
    }
  });

  it("has a freshness entry for every chart page (so no badge is missing)", () => {
    const data = loadFreshness();
    const missing = [...VALID_CHART_NAMES].filter((slug) => !(slug in data));
    expect(missing, `chart pages without a freshness entry: ${missing.join(", ")}`).toEqual(
      [],
    );
  });
});
