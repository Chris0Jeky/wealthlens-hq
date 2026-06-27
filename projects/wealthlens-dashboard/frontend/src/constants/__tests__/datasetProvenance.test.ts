import { describe, it, expect } from "vitest"
import { DATASET_PROVENANCE } from "@/constants/datasetProvenance"
import { VALID_CHART_NAMES } from "@/constants/charts"

/**
 * Guards the single source of truth for public provenance facts. DataSourcesView
 * and MethodologyView both read licence + update frequency from DATASET_PROVENANCE;
 * these assertions ensure every routed chart has an entry (so neither page ever
 * falls back to "Unknown"/em dash) and that no stray/typo slug creeps in.
 */
describe("DATASET_PROVENANCE", () => {
  it("covers exactly the routed charts (no missing or extra slugs)", () => {
    const provenanceSlugs = new Set(Object.keys(DATASET_PROVENANCE))
    expect(provenanceSlugs).toEqual(VALID_CHART_NAMES)
  })

  it("gives every dataset a non-empty licence and update frequency", () => {
    for (const [slug, info] of Object.entries(DATASET_PROVENANCE)) {
      expect(info.licence, `${slug} licence`).toBeTruthy()
      expect(info.updateFrequency, `${slug} updateFrequency`).toBeTruthy()
    }
  })
})
