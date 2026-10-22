import { describe, expect, it } from "vitest"
import { escapeHtml, filterChartRowsByRange, parseChartRows, safeMinMax, toNumberOrNaN } from "../chart"
import type { DatasetRow } from "@/types/api"

describe("parseChartRows", () => {
  it("derives WID percentile keys without mutating raw rows or values", () => {
    const rows: DatasetRow[] = [
      { variable: "shweal_p90p100_992_j", value: 0.5 },
      { variable: "shweal_p99p100_992_j", value: 0.2 },
    ]
    const original = structuredClone(rows)
    expect(parseChartRows("wealth-shares", rows)).toEqual([
      { ...rows[0], percentile: "p90p100" },
      { ...rows[1], percentile: "p99p100" },
    ])
    expect(rows).toEqual(original)
  })

  it("preserves supplied percentiles, missing variables and unrelated datasets", () => {
    const rows: DatasetRow[] = [
      { variable: "shweal_p90p100_992_j", percentile: "p99p100" },
      { variable: null },
      { variable: "" },
      { value: 0 },
    ]
    expect(parseChartRows("wealth-shares", rows)).toEqual(rows)
    expect(parseChartRows("other", rows)).toBe(rows)
  })

  it("mirrors the exporter's fallback for an unrecognised variable", () => {
    expect(parseChartRows("wealth-shares", [{ variable: "unknown" }])).toEqual([
      { variable: "unknown", percentile: "unknown" },
    ])
  })
})

describe("filterChartRowsByRange", () => {
  const rows = [{ year: 2024 }, { year: "1999" }, { year: 2000 }, { year: null }]

  it("keeps an inclusive window anchored to the newest dataset year, regardless of order", () => {
    expect(filterChartRowsByRange(rows, "25y")).toEqual([rows[0], rows[2]])
    expect(filterChartRowsByRange(rows, "1y")).toEqual([rows[0]])
    expect(filterChartRowsByRange(rows, "200y")).toEqual(rows.slice(0, 3))
  })

  it("leaves All and unsupported ranges unchanged", () => {
    for (const range of ["All", "all", "", "bad", "0y", "-1y"]) {
      expect(filterChartRowsByRange(rows, range)).toBe(rows)
    }
  })

  it("uses UTC calendar years for date-axis rows", () => {
    const dates = [
      { date: "2019-12-31" }, { date: "2020-01-01" }, { date: "2024-01-01" },
      { date: "bad" }, { date: "" }, { date: null },
    ]
    expect(filterChartRowsByRange(dates, "5y")).toEqual(dates.slice(1, 3))
  })

  it("handles empty datasets and missing years without fabricating a year zero", () => {
    expect(filterChartRowsByRange([], "25y")).toEqual([])
    expect(filterChartRowsByRange([{ year: "" }, { year: null }, { year: "bad" }], "25y")).toEqual([])
  })
})

describe("toNumberOrNaN", () => {
  it("maps null / undefined / blank strings to NaN (not a fabricated 0)", () => {
    // The whole point: plain Number(null) === 0, Number('') === 0, Number('  ') === 0,
    // which would silently fabricate a real data point from a missing cell.
    expect(toNumberOrNaN(null)).toBeNaN()
    expect(toNumberOrNaN(undefined)).toBeNaN()
    expect(toNumberOrNaN("")).toBeNaN()
    expect(toNumberOrNaN("   ")).toBeNaN()
  })

  it("maps non-numeric strings to NaN", () => {
    expect(toNumberOrNaN("n/a")).toBeNaN()
    expect(toNumberOrNaN("abc")).toBeNaN()
  })

  it("maps non-number/non-string types to NaN (no Number() quirks)", () => {
    // Number([])===0, Number([5])===5, Number(true)===1, Number(Symbol()) throws —
    // all must safely become NaN instead of a fabricated value or a crash.
    expect(toNumberOrNaN(true)).toBeNaN()
    expect(toNumberOrNaN(false)).toBeNaN()
    expect(toNumberOrNaN([])).toBeNaN()
    expect(toNumberOrNaN([5])).toBeNaN()
    expect(toNumberOrNaN({})).toBeNaN()
    expect(() => toNumberOrNaN(Symbol("x"))).not.toThrow()
    expect(toNumberOrNaN(Symbol("x"))).toBeNaN()
  })

  it("rejects non-finite numbers (Infinity / overflow strings) as NaN", () => {
    expect(toNumberOrNaN(Infinity)).toBeNaN()
    expect(toNumberOrNaN(-Infinity)).toBeNaN()
    expect(toNumberOrNaN("Infinity")).toBeNaN()
    expect(toNumberOrNaN("1e309")).toBeNaN() // overflows to Infinity
  })

  it("preserves a genuine numeric 0 (so a real zero is NOT dropped)", () => {
    expect(toNumberOrNaN(0)).toBe(0)
    expect(toNumberOrNaN("0")).toBe(0)
  })

  it("parses real numbers and numeric strings", () => {
    expect(toNumberOrNaN(42)).toBe(42)
    expect(toNumberOrNaN("42.5")).toBe(42.5)
    expect(toNumberOrNaN(-3.7)).toBe(-3.7)
  })
})

describe("escapeHtml", () => {
  it("escapes ampersands", () => {
    expect(escapeHtml("a&b")).toBe("a&amp;b")
  })

  it("escapes angle brackets", () => {
    expect(escapeHtml("<script>")).toBe("&lt;script&gt;")
  })

  it("escapes double quotes", () => {
    expect(escapeHtml('a"b')).toBe("a&quot;b")
  })

  it("returns plain text unchanged", () => {
    expect(escapeHtml("hello world")).toBe("hello world")
  })

  it("handles empty string", () => {
    expect(escapeHtml("")).toBe("")
  })
})

describe("safeMinMax", () => {
  it("returns min and max from array", () => {
    expect(safeMinMax([3, 1, 4, 1, 5])).toEqual({ min: 1, max: 5 })
  })

  it("handles single element", () => {
    expect(safeMinMax([42])).toEqual({ min: 42, max: 42 })
  })

  it("returns zeros for empty array", () => {
    expect(safeMinMax([])).toEqual({ min: 0, max: 0 })
  })

  it("handles negative numbers", () => {
    expect(safeMinMax([-5, -1, -3])).toEqual({ min: -5, max: -1 })
  })
})
