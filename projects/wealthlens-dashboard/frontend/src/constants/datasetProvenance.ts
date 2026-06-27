/**
 * Canonical per-dataset provenance facts — the SINGLE SOURCE OF TRUTH for the
 * licence and update cadence shown on WealthLens's public transparency surfaces.
 *
 * Two pages render these facts: the Data Sources table (`DataSourcesView.vue`,
 * route `/data-sources`) and the Methodology source cards (`MethodologyView.vue`,
 * route `/methodology`). They previously held INDEPENDENT hardcoded copies and
 * drifted apart (e.g. one said wealth-shares updates "Periodic", the other
 * "Annual (irregular)"). Importing this map in both guarantees they cannot
 * disagree again — change a value here and both pages update together.
 *
 * Values are reconciled against the authoritative source catalogue
 * `research/data-sources/data-source-registry.md` and, for licences, the
 * Analyst registry `registries/sources.yml` + `docs/data-licences.md`. A
 * `datasetProvenance.test.ts` guard asserts the keyset stays in lockstep with
 * the 12 routed charts.
 *
 * Notes on specific values:
 * - `boe-rates` licence is "Open Government Licence v3.0" (NOT the registry's
 *   cautious "OGL-equivalent"): the Bank states its database content is
 *   "subject to the terms of the UK Open Government Licence" — only third-party
 *   exchange-rate series are excluded, which this chart does not use.
 * - `wealth-by-decile` is "Biennial (suspended)": the Wealth and Assets Survey
 *   lost accredited-official-statistics status (June 2025) and is suspended.
 * - `inheritance-tax` + `wage-stagnation` are served from static/hand-curated
 *   JSON (outside the CSV metadata pipeline). Since #463 they are appended to
 *   the generated all-metadata the Data Sources page renders, so their entries
 *   here are live (not merely pre-registered) and supply the licence/frequency
 *   the static sidecars omit.
 */

/** Provenance facts displayed for a single dataset. */
export interface DatasetProvenance {
  /** Licence the upstream source publishes the data under, as a display label. */
  licence: string
  /** How often the upstream source releases or refreshes the data. */
  updateFrequency: string
}

/** Keyed by dataset slug (matching the routed chart names in `constants/charts.ts`). */
export const DATASET_PROVENANCE: Record<string, DatasetProvenance> = {
  "wealth-shares": { licence: "CC-BY 4.0", updateFrequency: "Annual (irregular)" },
  "housing-affordability": { licence: "Open Government Licence v3.0", updateFrequency: "Annual" },
  "wealth-by-decile": {
    licence: "Open Government Licence v3.0",
    updateFrequency: "Biennial (suspended)",
  },
  "cgt-concentration": { licence: "Open Government Licence v3.0", updateFrequency: "Annual" },
  "productivity-pay": { licence: "Open Government Licence v3.0", updateFrequency: "Quarterly" },
  "gdhi-by-region": { licence: "Open Government Licence v3.0", updateFrequency: "Annual" },
  "tax-composition": { licence: "Open Government Licence v3.0", updateFrequency: "Monthly" },
  "boe-rates": { licence: "Open Government Licence v3.0", updateFrequency: "Monthly" },
  "child-poverty": { licence: "Open Government Licence v3.0", updateFrequency: "Annual" },
  "generational-wealth": { licence: "CC BY-NC-ND 4.0", updateFrequency: "Annual" },
  "wage-stagnation": { licence: "Open Government Licence v3.0", updateFrequency: "Annual" },
  "inheritance-tax": { licence: "Open Government Licence v3.0", updateFrequency: "Annual" },
}
