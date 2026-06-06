/**
 * Integration tests: static data validation.
 *
 * Validates the static JSON the SPA ships in `public/data/`. These files are
 * served verbatim by the GitHub Pages deploy, so a malformed or drifted file
 * reaches users directly — this test is the guard.
 *
 * Why this exists / what it caught: the test previously pointed `DATA_DIR` one
 * directory too high (`../../../../public/data` -> the wealthlens-dashboard
 * root, which has no `public/`), so `existsSync(DATA_DIR)` was false and every
 * assertion silently skipped — it validated nothing. The path is now correct
 * AND the directory's presence is asserted (not skipped), so a future mis-path
 * regression fails loudly. Activating it surfaced a real bug: the generator
 * shipped `cgt-concentration.json` with literal `NaN` tokens (invalid JSON).
 *
 * Two environments to support:
 *  - A fresh CI checkout: `public/data/*` is gitignored except a small committed
 *    whitelist (wealth-shares[+meta], inheritance-tax, wage-stagnation[+meta],
 *    freshness). The other datasets, `datasets.json` and `all-metadata.json` are
 *    build artifacts produced by `scripts/generate_static_api.py` at deploy and
 *    are ABSENT in CI.
 *  - Local/deploy after running the generator: all datasets are present.
 *
 * So the committed-file checks (wealth-shares contract, freshness shape) always
 * run, the JSON-validity sweep covers whatever is present, and the full
 * per-dataset contract is asserted only when the generator output is present.
 */
import { describe, it, expect } from "vitest";
import { readdirSync, readFileSync, existsSync } from "fs";
import { resolve } from "path";

// Path to the SPA's static data directory.
// __dirname = frontend/src/__tests__/integration  ->  ../../../ = frontend.
const DATA_DIR = resolve(__dirname, "../../../public/data");

// ---------------------------------------------------------------------------
// Schema validators
// ---------------------------------------------------------------------------

interface DatasetRow {
  [key: string]: string | number | null;
}

interface PaginatedResponse {
  data: DatasetRow[];
  page: number;
  limit: number;
  total: number;
  total_pages: number;
}

interface DatasetMetadata {
  name: string;
  description: string;
  source: string;
  source_url: string;
  access_date: string;
  row_count: number;
  columns: string[];
}

function isValidPaginatedResponse(obj: unknown): obj is PaginatedResponse {
  if (typeof obj !== "object" || obj === null) return false;
  const o = obj as Record<string, unknown>;
  return (
    Array.isArray(o.data) &&
    typeof o.page === "number" &&
    typeof o.limit === "number" &&
    typeof o.total === "number" &&
    typeof o.total_pages === "number"
  );
}

function isValidMetadata(obj: unknown): obj is DatasetMetadata {
  if (typeof obj !== "object" || obj === null) return false;
  const o = obj as Record<string, unknown>;
  return (
    typeof o.name === "string" &&
    typeof o.description === "string" &&
    typeof o.source === "string" &&
    typeof o.source_url === "string" &&
    typeof o.access_date === "string" &&
    typeof o.row_count === "number" &&
    Array.isArray(o.columns) &&
    o.columns.every((c: unknown) => typeof c === "string")
  );
}

function isValidDatasetList(obj: unknown): obj is { datasets: string[] } {
  if (typeof obj !== "object" || obj === null) return false;
  const o = obj as Record<string, unknown>;
  return (
    Array.isArray(o.datasets) &&
    o.datasets.every((d: unknown) => typeof d === "string")
  );
}

function isValidAllMetadata(
  obj: unknown,
): obj is { datasets: DatasetMetadata[] } {
  if (typeof obj !== "object" || obj === null) return false;
  const o = obj as Record<string, unknown>;
  return (
    Array.isArray(o.datasets) &&
    o.datasets.every((d: unknown) => isValidMetadata(d))
  );
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function getJsonFiles(): string[] {
  return readdirSync(DATA_DIR).filter((f) => f.endsWith(".json"));
}

function present(filename: string): boolean {
  return existsSync(resolve(DATA_DIR, filename));
}

function readJson(filename: string): unknown {
  const content = readFileSync(resolve(DATA_DIR, filename), "utf-8");
  return JSON.parse(content);
}

/** The authoritative list of store-backed dataset slugs (from datasets.json). */
function getDatasetSlugs(): string[] {
  if (!present("datasets.json")) return [];
  const parsed = readJson("datasets.json");
  return isValidDatasetList(parsed) ? parsed.datasets : [];
}

/** Validate one dataset slug's data + metadata + their consistency. */
function validateDataset(slug: string): void {
  const dataFile = `${slug}.json`;
  const metaFile = `${slug}-metadata.json`;
  expect(present(dataFile), `missing ${dataFile}`).toBe(true);
  expect(present(metaFile), `missing ${metaFile}`).toBe(true);

  const data = readJson(dataFile);
  expect(isValidPaginatedResponse(data)).toBe(true);
  const paginated = data as PaginatedResponse;
  expect(paginated.data.length).toBeGreaterThan(0);
  for (const row of paginated.data) {
    expect(typeof row).toBe("object");
    expect(row).not.toBeNull();
  }

  const meta = readJson(metaFile);
  expect(isValidMetadata(meta)).toBe(true);
  const metadata = meta as DatasetMetadata;
  expect(metadata.source.length).toBeGreaterThan(0);
  expect(metadata.source_url.length).toBeGreaterThan(0);
  expect(() => new URL(metadata.source_url)).not.toThrow();
  expect(metadata.access_date).toMatch(/^\d{4}-\d{2}-\d{2}$/);

  // Metadata columns must appear in the data rows.
  const firstRowKeys = Object.keys(paginated.data[0]);
  for (const col of metadata.columns) {
    expect(
      firstRowKeys,
      `Column "${col}" from ${metaFile} not in data row keys: [${firstRowKeys.join(", ")}]`,
    ).toContain(col);
  }
  // row_count must match the paginated total.
  expect(metadata.row_count).toBe(paginated.total);
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("Static data validation", () => {
  // The data directory is committed (gitignore whitelists wealth-shares,
  // inheritance-tax, wage-stagnation and freshness) and shipped verbatim, so it
  // MUST exist. Asserting (not skipping) keeps a future path regression from
  // silently disabling every check below — the original failure mode.
  it("public/data directory exists and contains JSON", () => {
    expect(existsSync(DATA_DIR), `expected static data at ${DATA_DIR}`).toBe(
      true,
    );
    expect(getJsonFiles().length).toBeGreaterThan(0);
  });

  const jsonFiles = getJsonFiles();

  describe("JSON validity (all present files parse)", () => {
    it.each(jsonFiles)("%s is valid JSON", (filename) => {
      // Catches invalid-JSON literals like NaN/Infinity that Python's json.dump
      // emits by default — these are unparseable by the browser's fetch().json().
      expect(() => readJson(filename)).not.toThrow();
    });
  });

  // wealth-shares is committed (gitignore whitelist), so this contract check
  // always runs, including in a fresh CI checkout.
  describe("wealth-shares (committed dataset)", () => {
    it("data + metadata are valid and consistent", () => {
      validateDataset("wealth-shares");
    });
  });

  describe("freshness.json (badge data)", () => {
    it("each entry has a valid, non-future last_updated and a source", () => {
      expect(present("freshness.json")).toBe(true);
      const fresh = readJson("freshness.json") as Record<string, unknown>;
      expect(typeof fresh).toBe("object");
      expect(fresh).not.toBeNull();
      const entries = Object.entries(fresh);
      expect(entries.length).toBeGreaterThan(0);
      // Compare against today's UTC date as a YYYY-MM-DD string. String order
      // matches chronological order for that format, so this is timezone-safe.
      const todayUtc = new Date().toISOString().slice(0, 10);
      for (const [slug, value] of entries) {
        expect(typeof value, `freshness["${slug}"] should be an object`).toBe(
          "object",
        );
        const entry = value as Record<string, unknown>;
        expect(entry.last_updated, `freshness["${slug}"].last_updated`).toMatch(
          /^\d{4}-\d{2}-\d{2}$/,
        );
        // A future last_updated would render a perpetually "fresh" badge.
        expect(
          (entry.last_updated as string) <= todayUtc,
          `freshness["${slug}"].last_updated ${entry.last_updated} is in the future (today ${todayUtc})`,
        ).toBe(true);
        expect(typeof entry.source, `freshness["${slug}"].source`).toBe(
          "string",
        );
        expect((entry.source as string).length).toBeGreaterThan(0);
      }
    });
  });

  // Full per-dataset contract — only present after the generator has run
  // (local dev / the deploy build). Absent in a fresh CI checkout, where the
  // committed-file checks above are the active guard.
  describe("Generated dataset contract (when datasets.json is present)", () => {
    const slugs = getDatasetSlugs();

    if (slugs.length === 0) {
      it("datasets.json not generated in this checkout — full contract skipped", () => {
        // Assert the REASON we skip, so this is not a silent no-op: the build
        // artifact is genuinely absent (it is gitignored and regenerated at
        // deploy). If it ever IS present, the it.each blocks below run instead.
        expect(present("datasets.json")).toBe(false);
      });
      return;
    }

    it.each(slugs)("%s data + metadata are valid and consistent", (slug) => {
      validateDataset(slug);
    });

    it("all-metadata.json covers exactly the datasets.json slugs", () => {
      expect(present("all-metadata.json")).toBe(true);
      const all = readJson("all-metadata.json");
      expect(isValidAllMetadata(all)).toBe(true);
      const covered = (all as { datasets: DatasetMetadata[] }).datasets
        .map((d) => d.name)
        .sort();
      expect(covered).toEqual([...slugs].sort());
    });

    it("every dataset slug has a freshness.json entry", () => {
      const fresh = readJson("freshness.json") as Record<string, unknown>;
      for (const slug of slugs) {
        expect(
          Object.prototype.hasOwnProperty.call(fresh, slug),
          `freshness.json is missing an entry for dataset "${slug}"`,
        ).toBe(true);
      }
    });
  });
});
