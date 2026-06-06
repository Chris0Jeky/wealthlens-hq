import { describe, it, expect } from "vitest";
import { existsSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { VALID_CHART_NAMES } from "@/constants/charts";

const here = dirname(fileURLToPath(import.meta.url));
const DATA_DIR = resolve(here, "../../../public/data");

// Resolve relative to THIS file (not process.cwd()) so the test passes regardless of
// which directory the runner is invoked from (repo root vs frontend).
function loadFreshness(): Record<string, unknown> {
  return JSON.parse(
    readFileSync(resolve(DATA_DIR, "freshness.json"), "utf-8"),
  ) as Record<string, unknown>;
}

/** Source string from a committed `{slug}-metadata.json`, or null if absent. */
function metadataSource(slug: string): string | null {
  const path = resolve(DATA_DIR, `${slug}-metadata.json`);
  if (!existsSync(path)) return null;
  // A metadata file that is empty or literally `null` parses to a non-object;
  // guard so `.source` cannot throw a TypeError (just treat it as no source).
  const meta = JSON.parse(readFileSync(path, "utf-8")) as unknown;
  if (typeof meta !== "object" || meta === null) return null;
  const source = (meta as { source?: unknown }).source;
  return typeof source === "string" ? source : null;
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

  // The badge tooltip renders freshness `source`, so it must not name the WRONG
  // organisation. Most entries are deliberately brief labels (e.g. "Bank of
  // England" vs the metadata's longer name), which is fine — but wealth-shares
  // had drifted to a different source entirely ("ONS Wealth and Assets Survey"
  // when its metadata + the WID pipeline cite the World Inequality Database).
  // Lock that one to its committed, authoritative metadata source so the drift
  // cannot recur. (wealth-shares is committed, so this runs in a fresh CI checkout.)
  //
  // Why this is NOT generalised to "every committed metadata slug": the only
  // OTHER committed metadata file is wage-stagnation, whose freshness label
  // ("ONS ASHE") is a deliberately brief form of its longer metadata source
  // ("ONS Annual Survey of Hours and Earnings (ASHE), Table 1") — the same
  // organisation, just abbreviated. An exact-equality loop would wrongly fail it.
  // The bug class worth locking is a wrong-ORGANISATION drift, which only
  // wealth-shares exhibited. This PR also corrects productivity-pay (ONS/EPI ->
  // ONS, since the US Economic Policy Institute supplies no UK datapoint — the
  // pipeline is pure ONS LZVD/AWE/CPIH). child-poverty's "DWP/HBAI" was left
  // as-is: it matches the user-facing ChildPovertyChart.vue and the after-housing-
  // costs measure, while the pipeline labels it CiLIF — an unresolved HBAI-vs-CiLIF
  // source conflict deferred to a human (see ORCHESTRATION). Neither has a
  // committed metadata file, so neither can be structurally locked here anyway.
  it("wealth-shares freshness source matches its authoritative metadata source", () => {
    const data = loadFreshness();
    const metaSource = metadataSource("wealth-shares");
    expect(metaSource, "wealth-shares-metadata.json should be committed").not.toBeNull();
    // Guard the entry shape before reading .source, so a missing/null/non-object
    // wealth-shares entry fails as a clear assertion, not an opaque TypeError.
    const entry = data["wealth-shares"];
    expect(entry, "freshness.json should have a wealth-shares entry").toBeTruthy();
    expect(typeof entry).toBe("object");
    expect((entry as { source?: unknown }).source).toBe(metaSource);
  });
});
