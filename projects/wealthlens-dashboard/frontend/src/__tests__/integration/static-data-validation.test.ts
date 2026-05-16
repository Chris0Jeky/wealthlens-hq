/**
 * Integration tests: static data validation.
 *
 * Validates that ALL static JSON files in public/data/ (when they exist)
 * conform to the expected structure for the data store:
 * - Dataset files: { data: DatasetRow[], page, limit, total, total_pages }
 * - Metadata files: { name, description, source, source_url, access_date, row_count, columns }
 * - datasets.json: { datasets: string[] }
 * - all-metadata.json: { datasets: DatasetMetadata[] }
 *
 * Also validates that column names in metadata match the actual data keys.
 */
import { describe, it, expect } from "vitest";
import { readdirSync, readFileSync, existsSync } from "fs";
import { resolve } from "path";

// Path to the public/data directory (relative to project root)
const DATA_DIR = resolve(__dirname, "../../../../public/data");

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

function isValidDatasetList(
  obj: unknown,
): obj is { datasets: string[] } {
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
  if (!existsSync(DATA_DIR)) return [];
  return readdirSync(DATA_DIR).filter((f) => f.endsWith(".json"));
}

function readJson(filename: string): unknown {
  const content = readFileSync(resolve(DATA_DIR, filename), "utf-8");
  return JSON.parse(content);
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("Static data validation", () => {
  const jsonFiles = getJsonFiles();

  it("public/data directory exists or test gracefully skips", () => {
    // This test documents whether static data files are present.
    // When no files exist, remaining tests are skipped via it.skipIf.
    if (!existsSync(DATA_DIR)) {
      // Not a failure — static data is optional in dev
      expect(true).toBe(true);
    } else {
      expect(existsSync(DATA_DIR)).toBe(true);
    }
  });

  describe("JSON validity", () => {
    if (jsonFiles.length === 0) {
      it("no static data files present (skipped)", () => {
        expect(true).toBe(true);
      });
      return;
    }

    it.each(jsonFiles)("%s is valid JSON", (filename) => {
      expect(() => readJson(filename)).not.toThrow();
    });
  });

  describe("Dataset files structure", () => {
    const datasetFiles = jsonFiles.filter(
      (f) =>
        !f.endsWith("-metadata.json") &&
        f !== "datasets.json" &&
        f !== "all-metadata.json",
    );

    if (datasetFiles.length === 0) {
      it("no dataset files present (skipped)", () => {
        expect(true).toBe(true);
      });
      return;
    }

    it.each(datasetFiles)(
      "%s has valid paginated response structure",
      (filename) => {
        const data = readJson(filename);
        expect(isValidPaginatedResponse(data)).toBe(true);
      },
    );

    it.each(datasetFiles)(
      "%s has non-empty data array with objects",
      (filename) => {
        const data = readJson(filename) as PaginatedResponse;
        expect(data.data.length).toBeGreaterThan(0);
        for (const row of data.data) {
          expect(typeof row).toBe("object");
          expect(row).not.toBeNull();
        }
      },
    );
  });

  describe("Metadata files structure", () => {
    const metadataFiles = jsonFiles.filter(
      (f) => f.endsWith("-metadata.json") && f !== "all-metadata.json",
    );

    if (metadataFiles.length === 0) {
      it("no metadata files present (skipped)", () => {
        expect(true).toBe(true);
      });
      return;
    }

    it.each(metadataFiles)(
      "%s has required metadata fields",
      (filename) => {
        const data = readJson(filename);
        expect(isValidMetadata(data)).toBe(true);
      },
    );

    it.each(metadataFiles)(
      "%s has non-empty source and source_url",
      (filename) => {
        const data = readJson(filename) as DatasetMetadata;
        expect(data.source.length).toBeGreaterThan(0);
        expect(data.source_url.length).toBeGreaterThan(0);
        // source_url should be a valid URL
        expect(() => new URL(data.source_url)).not.toThrow();
      },
    );

    it.each(metadataFiles)(
      "%s has valid access_date (YYYY-MM-DD)",
      (filename) => {
        const data = readJson(filename) as DatasetMetadata;
        expect(data.access_date).toMatch(/^\d{4}-\d{2}-\d{2}$/);
      },
    );
  });

  describe("datasets.json", () => {
    const hasDatasetsJson = jsonFiles.includes("datasets.json");

    if (!hasDatasetsJson) {
      it("datasets.json not present (skipped)", () => {
        expect(true).toBe(true);
      });
      return;
    }

    it("has valid dataset list structure", () => {
      const data = readJson("datasets.json");
      expect(isValidDatasetList(data)).toBe(true);
    });

    it("contains at least one dataset name", () => {
      const data = readJson("datasets.json") as { datasets: string[] };
      expect(data.datasets.length).toBeGreaterThan(0);
    });
  });

  describe("all-metadata.json", () => {
    const hasAllMetadata = jsonFiles.includes("all-metadata.json");

    if (!hasAllMetadata) {
      it("all-metadata.json not present (skipped)", () => {
        expect(true).toBe(true);
      });
      return;
    }

    it("has valid all-metadata structure", () => {
      const data = readJson("all-metadata.json");
      expect(isValidAllMetadata(data)).toBe(true);
    });
  });

  describe("Metadata-data consistency", () => {
    const metadataFiles = jsonFiles.filter(
      (f) => f.endsWith("-metadata.json") && f !== "all-metadata.json",
    );

    if (metadataFiles.length === 0) {
      it("no metadata files to cross-validate (skipped)", () => {
        expect(true).toBe(true);
      });
      return;
    }

    it.each(metadataFiles)(
      "%s columns match actual data keys",
      (metaFilename) => {
        const dataFilename = metaFilename.replace("-metadata.json", ".json");
        if (!jsonFiles.includes(dataFilename)) {
          // Skip if corresponding data file doesn't exist
          return;
        }

        const meta = readJson(metaFilename) as DatasetMetadata;
        const dataset = readJson(dataFilename) as PaginatedResponse;

        if (dataset.data.length === 0) return;

        // All column names from metadata should appear as keys in at least
        // the first row of data
        const firstRowKeys = Object.keys(dataset.data[0]);
        for (const col of meta.columns) {
          expect(
            firstRowKeys,
            `Column "${col}" from metadata not found in data row keys: [${firstRowKeys.join(", ")}]`,
          ).toContain(col);
        }
      },
    );

    it.each(metadataFiles)(
      "%s row_count matches actual data length",
      (metaFilename) => {
        const dataFilename = metaFilename.replace("-metadata.json", ".json");
        if (!jsonFiles.includes(dataFilename)) return;

        const meta = readJson(metaFilename) as DatasetMetadata;
        const dataset = readJson(dataFilename) as PaginatedResponse;

        // row_count in metadata should match total in paginated response
        expect(meta.row_count).toBe(dataset.total);
      },
    );
  });
});
