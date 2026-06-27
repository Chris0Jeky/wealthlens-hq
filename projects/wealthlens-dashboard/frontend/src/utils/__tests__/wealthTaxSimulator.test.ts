import { describe, it, expect } from "vitest"
import {
  simulateWealthTax,
  estimateTaxpayersAbove,
  estimateWealthAbove,
  estimateExcessWealth,
  formatRevenue,
  formatTaxpayers,
  formatThreshold,
  getSpendingComparison,
  PRESET_SCENARIOS,
  SIMULATOR_SOURCES,
  SPENDING_COMPARISONS,
  TOTAL_HOUSEHOLDS,
  UK_GDP,
  WEALTH_THRESHOLDS,
} from "@/utils/wealthTaxSimulator"

describe("simulateWealthTax", () => {
  it("returns zero revenue for empty bands", () => {
    const result = simulateWealthTax([])
    expect(result.annualRevenue).toBe(0)
    expect(result.affectedTaxpayers).toBe(0)
    expect(result.averageTaxPerTaxpayer).toBe(0)
    expect(result.revenueAsPercentGDP).toBe(0)
  })

  it("returns zero revenue for zero rate", () => {
    const result = simulateWealthTax([{ threshold: 5_000_000, rate: 0 }])
    expect(result.annualRevenue).toBe(0)
  })

  it("returns positive revenue for a single band at £5m threshold", () => {
    const result = simulateWealthTax([{ threshold: 5_000_000, rate: 0.01 }])
    expect(result.annualRevenue).toBeGreaterThan(0)
    expect(result.affectedTaxpayers).toBeGreaterThan(0)
    expect(result.averageTaxPerTaxpayer).toBeGreaterThan(0)
    expect(result.revenueAsPercentGDP).toBeGreaterThan(0)
  })

  it("higher threshold reduces affected households", () => {
    const low = simulateWealthTax([{ threshold: 1_000_000, rate: 0.01 }])
    const high = simulateWealthTax([{ threshold: 10_000_000, rate: 0.01 }])
    expect(high.affectedTaxpayers).toBeLessThan(low.affectedTaxpayers)
  })

  it("higher rate increases revenue proportionally", () => {
    const low = simulateWealthTax([{ threshold: 5_000_000, rate: 0.01 }])
    const high = simulateWealthTax([{ threshold: 5_000_000, rate: 0.02 }])
    // Should be approximately double (within rounding tolerance)
    expect(high.annualRevenue).toBeGreaterThan(low.annualRevenue * 1.8)
    expect(high.annualRevenue).toBeLessThan(low.annualRevenue * 2.2)
  })

  it("multiple bands stack correctly (more revenue than single lower band)", () => {
    const single = simulateWealthTax([{ threshold: 1_000_000, rate: 0.01 }])
    const multi = simulateWealthTax([
      { threshold: 1_000_000, rate: 0.01 },
      { threshold: 5_000_000, rate: 0.02 },
    ])
    expect(multi.annualRevenue).toBeGreaterThan(single.annualRevenue)
  })

  it("revenueAsPercentGDP is consistent with annualRevenue", () => {
    const result = simulateWealthTax([{ threshold: 2_000_000, rate: 0.01 }])
    const expectedPct = (result.annualRevenue / UK_GDP) * 100
    expect(result.revenueAsPercentGDP).toBeCloseTo(expectedPct, 1)
  })

  it("averageTaxPerTaxpayer equals revenue / affected households", () => {
    const result = simulateWealthTax([{ threshold: 1_000_000, rate: 0.01 }])
    const expected = result.annualRevenue / result.affectedTaxpayers
    expect(result.averageTaxPerTaxpayer).toBeCloseTo(expected, -2) // within rounding
  })

  it("handles unsorted bands correctly", () => {
    const sorted = simulateWealthTax([
      { threshold: 1_000_000, rate: 0.01 },
      { threshold: 5_000_000, rate: 0.02 },
    ])
    const unsorted = simulateWealthTax([
      { threshold: 5_000_000, rate: 0.02 },
      { threshold: 1_000_000, rate: 0.01 },
    ])
    expect(unsorted.annualRevenue).toBe(sorted.annualRevenue)
  })

  it("preset scenarios all produce reasonable revenue", () => {
    for (const preset of PRESET_SCENARIOS) {
      const result = simulateWealthTax(preset.bands)
      // Revenue should be between £1 billion and £500 billion for any preset
      expect(result.annualRevenue).toBeGreaterThan(1_000_000_000)
      expect(result.annualRevenue).toBeLessThan(500_000_000_000)
    }
  })

  it("100% rate on zero threshold returns very large revenue", () => {
    const result = simulateWealthTax([{ threshold: 0, rate: 1.0 }])
    expect(result.annualRevenue).toBeGreaterThan(1_000_000_000_000)
  })
})

describe("estimateTaxpayersAbove", () => {
  it("returns total households for zero threshold", () => {
    expect(estimateTaxpayersAbove(0)).toBe(TOTAL_HOUSEHOLDS)
  })

  it("returns fewer households for higher thresholds", () => {
    const low = estimateTaxpayersAbove(1_000_000)
    const high = estimateTaxpayersAbove(5_000_000)
    expect(high).toBeLessThan(low)
  })

  it("returns a positive number for very high thresholds", () => {
    const result = estimateTaxpayersAbove(50_000_000)
    expect(result).toBeGreaterThan(0)
  })

  it("returns at least 1 for extreme thresholds", () => {
    const result = estimateTaxpayersAbove(1_000_000_000)
    expect(result).toBeGreaterThanOrEqual(1)
  })

  it("returns approximately correct values for known data points", () => {
    // £1m should be around 2.8 million households
    const at1m = estimateTaxpayersAbove(1_000_000)
    expect(at1m).toBeGreaterThan(2_000_000)
    expect(at1m).toBeLessThan(4_000_000)
  })

  it("uses empirical low-threshold anchors instead of the fallback", () => {
    expect(estimateTaxpayersAbove(250_000)).toBe(15_537_000)
    expect(estimateTaxpayersAbove(500_000)).toBe(8_246_000)
    expect(estimateTaxpayersAbove(1_000_000)).toBe(3_004_000)
  })
})

describe("estimateWealthAbove", () => {
  it("uses the empirical first threshold anchor at GBP250k", () => {
    expect(estimateWealthAbove(250_000)).toBe(12_217_000_000_000)
  })
})

describe("estimateExcessWealth", () => {
  it("returns zero for very high threshold", () => {
    // Threshold so high nobody is above it meaningfully
    const result = estimateExcessWealth(100_000_000_000_000)
    expect(result).toBe(0)
  })

  it("returns positive for reasonable thresholds", () => {
    expect(estimateExcessWealth(1_000_000)).toBeGreaterThan(0)
    expect(estimateExcessWealth(5_000_000)).toBeGreaterThan(0)
  })

  it("lower threshold produces more excess wealth", () => {
    const low = estimateExcessWealth(1_000_000)
    const high = estimateExcessWealth(10_000_000)
    expect(low).toBeGreaterThan(high)
  })
})

describe("formatRevenue", () => {
  it("formats billions correctly", () => {
    expect(formatRevenue(45_000_000_000)).toBe("£45.0 billion")
  })

  it("formats trillions correctly", () => {
    expect(formatRevenue(1_500_000_000_000)).toBe("£1.5 trillion")
  })

  it("formats millions correctly", () => {
    expect(formatRevenue(5_000_000)).toBe("£5.0 million")
  })

  it("formats small numbers with locale", () => {
    const result = formatRevenue(500_000)
    expect(result).toContain("£")
    expect(result).toContain("500")
  })
})

describe("formatTaxpayers", () => {
  it("formats millions correctly", () => {
    expect(formatTaxpayers(2_800_000)).toBe("2.8 million")
  })

  it("formats thousands correctly", () => {
    expect(formatTaxpayers(150_000)).toBe("150,000")
  })

  it("formats small numbers", () => {
    expect(formatTaxpayers(500)).toBe("500")
  })
})

describe("formatThreshold", () => {
  it("formats millions as £Xm", () => {
    expect(formatThreshold(5_000_000)).toBe("£5m")
  })

  it("formats fractional millions", () => {
    expect(formatThreshold(1_500_000)).toBe("£1.5m")
  })

  it("formats thousands as £Xk", () => {
    expect(formatThreshold(500_000)).toBe("£500k")
  })
})

describe("getSpendingComparison", () => {
  it("returns null for zero revenue", () => {
    expect(getSpendingComparison(0)).toBeNull()
  })

  it("returns a string for significant revenue", () => {
    const result = getSpendingComparison(20_000_000_000)
    expect(typeof result).toBe("string")
    expect(result!.length).toBeGreaterThan(0)
  })

  it("mentions a relevant spending item", () => {
    const result = getSpendingComparison(10_000_000_000)
    expect(result).not.toBeNull()
  })
})

describe("source metadata", () => {
  it("keeps estimate anchors backed by source URLs and access dates", () => {
    expect(WEALTH_THRESHOLDS.length).toBeGreaterThan(0)
    for (const source of SIMULATOR_SOURCES.references) {
      expect(source.url).toMatch(/^https:\/\//)
      expect(source.accessDate).toMatch(/^\d{4}-\d{2}-\d{2}$/)
    }
    for (const comparison of SPENDING_COMPARISONS) {
      expect(comparison.sourceUrl).toMatch(/^https:\/\//)
      expect(comparison.accessDate).toMatch(/^\d{4}-\d{2}-\d{2}$/)
    }
  })
})
