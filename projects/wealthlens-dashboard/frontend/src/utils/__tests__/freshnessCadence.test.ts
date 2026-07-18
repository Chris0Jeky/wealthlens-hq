import { describe, it, expect } from "vitest"
import { assessFreshness, cadenceIntervalDays, CADENCE_GRACE } from "../freshnessCadence"
import { DATASET_PROVENANCE } from "@/constants/datasetProvenance"
import { VALID_CHART_NAMES } from "@/constants/charts"

const NOW = new Date("2026-07-11T00:00:00Z")

function daysBefore(days: number): string {
  return new Date(NOW.getTime() - days * 86_400_000).toISOString()
}

describe("cadenceIntervalDays", () => {
  it("maps every current provenance label — a future unmapped label degrades to unknown, never red", () => {
    for (const slug of VALID_CHART_NAMES) {
      const label = DATASET_PROVENANCE[slug].updateFrequency
      expect(cadenceIntervalDays(label), `${slug}: "${label}"`).not.toBeNull()
    }
  })

  it("maps the four cadences and the suspended flag", () => {
    expect(cadenceIntervalDays("Monthly")).toBe(31)
    expect(cadenceIntervalDays("Quarterly")).toBe(92)
    expect(cadenceIntervalDays("Annual")).toBe(366)
    expect(cadenceIntervalDays("Annual (irregular)")).toBe(366)
    expect(cadenceIntervalDays("Biennial (suspended)")).toBe("suspended")
    expect(cadenceIntervalDays("Whenever")).toBeNull()
  })
})

describe("assessFreshness (docs/product/freshness-grammar.md)", () => {
  it("annual data months old is CURRENT — the F3 fix", () => {
    // wealth-shares: Annual (irregular). 100 days old was "Expired" under
    // the old 30-day ladder; it is fully current for an annual series.
    const a = assessFreshness("wealth-shares", daysBefore(100), NOW)
    expect(a.state).toBe("current")
    expect(a.label).toBe("Current")
  })

  it("annual data beyond the grace window is UPDATE DUE, not expired", () => {
    const a = assessFreshness("wealth-shares", daysBefore(500), NOW)
    expect(a.state).toBe("due")
    expect(a.label).toBe("Update due")
    expect(a.detail).toContain("our copy may lag")
  })

  it("monthly data is graded on the monthly rhythm", () => {
    expect(assessFreshness("boe-rates", daysBefore(20), NOW).state).toBe("current")
    expect(assessFreshness("boe-rates", daysBefore(60), NOW).state).toBe("due")
  })

  it("applies the documented grace factor at the boundary", () => {
    const graceEdge = 31 * CADENCE_GRACE
    expect(assessFreshness("boe-rates", daysBefore(graceEdge - 1), NOW).state).toBe("current")
    expect(assessFreshness("boe-rates", daysBefore(graceEdge + 1), NOW).state).toBe("due")
  })

  it("a suspended source is SUSPENDED regardless of age — the WAS case", () => {
    // wealth-by-decile: "Biennial (suspended)" — the survey stopped
    // publishing; age arithmetic is meaningless.
    const recent = assessFreshness("wealth-by-decile", daysBefore(10), NOW)
    const ancient = assessFreshness("wealth-by-decile", daysBefore(2000), NOW)
    expect(recent.state).toBe("suspended")
    expect(ancient.state).toBe("suspended")
    expect(ancient.label).toBe("Source suspended")
    expect(ancient.detail).toContain("best available official data")
  })

  it("missing or malformed dates are UNKNOWN", () => {
    expect(assessFreshness("wealth-shares", null, NOW).state).toBe("unknown")
    expect(assessFreshness("wealth-shares", "not-a-date", NOW).state).toBe("unknown")
  })

  it("an unknown slug is UNKNOWN (no provenance, no judgment)", () => {
    expect(assessFreshness("no-such-dataset", daysBefore(1), NOW).state).toBe("unknown")
  })

  it("never produces a red/expired state for any dataset at any age", () => {
    for (const slug of VALID_CHART_NAMES) {
      for (const age of [0, 40, 200, 800, 3000]) {
        const { state } = assessFreshness(slug, daysBefore(age), NOW)
        expect(["current", "due", "suspended", "unknown"]).toContain(state)
      }
    }
  })
})
