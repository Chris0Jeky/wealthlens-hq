/**
 * Cadence-aware freshness grammar (docs/product/freshness-grammar.md;
 * reality-check F3).
 *
 * The old fixed 7/30-day ladder branded fully-current annual statistics
 * red "Expired". Freshness here is graded against each SOURCE's declared
 * release cadence, from the single provenance source of truth
 * (constants/datasetProvenance.ts, itself reconciled with
 * registries/sources.yml). There is deliberately no red state — see the
 * grammar note.
 */
import { DATASET_PROVENANCE } from "@/constants/datasetProvenance"

export type CadenceState = "current" | "due" | "suspended" | "unknown"

export interface CadenceAssessment {
  state: CadenceState
  /** Short badge label ("Current", "Update due", "Source suspended", "Unknown"). */
  label: string
  /** One-line tooltip detail explaining what the state means for THIS series. */
  detail: string
}

/**
 * Official releases slip; an annual series published 13 months ago is not
 * late. Documented in the grammar note — keep the two in sync.
 */
export const CADENCE_GRACE = 1.25

/** Days per declared cadence label. */
const INTERVAL_DAYS: ReadonlyArray<[RegExp, number]> = [
  [/monthly/i, 31],
  [/quarterly/i, 92],
  [/annual/i, 366],
  [/biennial/i, 731],
]

/**
 * Release interval for a provenance updateFrequency label.
 * Returns "suspended" when the source has stopped publishing, or null for
 * a label we cannot map (a unit test pins all current labels, so null can
 * only happen for a future, unmapped one).
 */
export function cadenceIntervalDays(frequencyLabel: string): number | "suspended" | null {
  if (/suspended/i.test(frequencyLabel)) return "suspended"
  for (const [pattern, days] of INTERVAL_DAYS) {
    if (pattern.test(frequencyLabel)) return days
  }
  return null
}

/**
 * Grade a dataset's freshness against its source's cadence.
 *
 * @param slug dataset slug (keys DATASET_PROVENANCE)
 * @param lastUpdated curated last_updated date string (freshness.json), or null
 * @param now injection point for tests
 */
export function assessFreshness(
  slug: string,
  lastUpdated: string | null | undefined,
  now: Date = new Date(),
): CadenceAssessment {
  const frequency = DATASET_PROVENANCE[slug]?.updateFrequency
  const cadence = frequency ? cadenceIntervalDays(frequency) : null

  if (cadence === "suspended") {
    return {
      state: "suspended",
      label: "Source suspended",
      detail:
        "The source has paused publication — the last published round remains the best available official data.",
    }
  }

  const ts = lastUpdated ? Date.parse(lastUpdated) : NaN
  if (Number.isNaN(ts) || cadence === null) {
    return {
      state: "unknown",
      label: "Unknown",
      detail: "No update-cadence information for this dataset.",
    }
  }

  const ageDays = Math.max(0, (now.getTime() - ts) / 86_400_000)
  const seriesWord = frequency ? frequency.toLowerCase() : "this"

  if (ageDays <= cadence * CADENCE_GRACE) {
    return {
      state: "current",
      label: "Current",
      detail: `Current for ${aOrAn(seriesWord)} ${seriesWord} series — no newer release is expected yet.`,
    }
  }

  return {
    state: "due",
    label: "Update due",
    detail: `The ${seriesWord} source has likely published since our last ingest — our copy may lag; figures remain the newest we hold.`,
  }
}

function aOrAn(word: string): string {
  return /^[aeiou]/i.test(word) ? "an" : "a"
}
