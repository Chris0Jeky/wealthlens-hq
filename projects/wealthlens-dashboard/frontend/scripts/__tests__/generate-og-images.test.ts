/**
 * Tests for OG image generation script.
 *
 * Verifies:
 * 1. Metadata completeness (all VALID_CHART_NAMES have OG metadata)
 * 2. Generated images exist and are valid PNGs (check magic bytes)
 * 3. Generated images are within size limits
 */

import { describe, it, expect } from "vitest";
import { existsSync, readFileSync } from "fs";
import { resolve, join } from "path";
import { VALID_CHART_NAMES } from "../../src/constants/charts";
import {
  OG_METADATA,
  getChartsMissingOgMetadata,
} from "../../src/constants/ogMetadata";

const OUTPUT_DIR = resolve(__dirname, "../../public/og");

// PNG magic bytes: 137 80 78 71 13 10 26 10
const PNG_MAGIC_BYTES = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);

/** Max allowed file size: 150KB (generous limit; target is ~100KB) */
const MAX_FILE_SIZE_BYTES = 150 * 1024;

describe("OG Metadata", () => {
  it("every VALID_CHART_NAME has OG metadata", () => {
    const missing = getChartsMissingOgMetadata();
    expect(missing).toEqual([]);
  });

  it("all metadata entries have required fields", () => {
    for (const [slug, entry] of Object.entries(OG_METADATA)) {
      expect(entry.title, `${slug} missing title`).toBeTruthy();
      expect(entry.subtitle, `${slug} missing subtitle`).toBeTruthy();
      expect(entry.source, `${slug} missing source`).toBeTruthy();
      expect(
        entry.sourceAccessDate,
        `${slug} missing sourceAccessDate`
      ).toMatch(/^\d{4}-\d{2}-\d{2}$/);
    }
  });

  it("metadata keys match VALID_CHART_NAMES exactly", () => {
    const metadataKeys = new Set(Object.keys(OG_METADATA));
    const chartNames = new Set(VALID_CHART_NAMES);
    // Every metadata key should be a valid chart name
    for (const key of metadataKeys) {
      expect(chartNames.has(key), `"${key}" in OG_METADATA but not in VALID_CHART_NAMES`).toBe(
        true
      );
    }
  });
});

describe("OG Generated Images", () => {
  // These tests verify the output after the generate script has run.
  // They will be skipped if images don't exist (e.g., in CI before generation).

  const chartNames = Array.from(VALID_CHART_NAMES);

  describe.runIf(existsSync(OUTPUT_DIR))("image files", () => {
    it.each(chartNames)("generates %s.png as valid PNG", (chartName) => {
      const filePath = join(OUTPUT_DIR, `${chartName}.png`);
      expect(existsSync(filePath), `${chartName}.png does not exist`).toBe(true);

      const fileBuffer = readFileSync(filePath);
      // Check PNG magic bytes
      const header = fileBuffer.subarray(0, 8);
      expect(header.equals(PNG_MAGIC_BYTES), `${chartName}.png has invalid PNG header`).toBe(
        true
      );
    });

    it("generates og-default.png as valid PNG", () => {
      const filePath = join(OUTPUT_DIR, "og-default.png");
      expect(existsSync(filePath), "og-default.png does not exist").toBe(true);

      const fileBuffer = readFileSync(filePath);
      const header = fileBuffer.subarray(0, 8);
      expect(header.equals(PNG_MAGIC_BYTES), "og-default.png has invalid PNG header").toBe(
        true
      );
    });

    it.each(chartNames)("%s.png is under size limit", (chartName) => {
      const filePath = join(OUTPUT_DIR, `${chartName}.png`);
      if (!existsSync(filePath)) return;

      const fileBuffer = readFileSync(filePath);
      expect(
        fileBuffer.length,
        `${chartName}.png exceeds ${MAX_FILE_SIZE_BYTES / 1024}KB limit`
      ).toBeLessThan(MAX_FILE_SIZE_BYTES);
    });

    it("og-default.png is under size limit", () => {
      const filePath = join(OUTPUT_DIR, "og-default.png");
      if (!existsSync(filePath)) return;

      const fileBuffer = readFileSync(filePath);
      expect(
        fileBuffer.length,
        `og-default.png exceeds ${MAX_FILE_SIZE_BYTES / 1024}KB limit`
      ).toBeLessThan(MAX_FILE_SIZE_BYTES);
    });

    it("generates correct number of images", () => {
      let count = 0;
      for (const chartName of chartNames) {
        if (existsSync(join(OUTPUT_DIR, `${chartName}.png`))) count++;
      }
      if (existsSync(join(OUTPUT_DIR, "og-default.png"))) count++;
      // Should have one per chart + default
      expect(count).toBe(chartNames.length + 1);
    });
  });
});
