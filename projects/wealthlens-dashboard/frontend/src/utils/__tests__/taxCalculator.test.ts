import { describe, it, expect } from "vitest"
import {
  calculateIncomeTax,
  calculateNI,
  calculateEffectiveRate,
  formatPercent,
  getPersonalAllowance,
} from "@/utils/taxCalculator"

describe("getPersonalAllowance", () => {
  it("returns full allowance for salary under £100,000", () => {
    expect(getPersonalAllowance(50_000)).toBe(12_570)
  })

  it("returns full allowance at exactly £100,000", () => {
    expect(getPersonalAllowance(100_000)).toBe(12_570)
  })

  it("tapers allowance for salary over £100,000", () => {
    // £120,000: excess = £20,000, reduction = £10,000
    expect(getPersonalAllowance(120_000)).toBe(2_570)
  })

  it("returns zero allowance at £125,140", () => {
    expect(getPersonalAllowance(125_140)).toBe(0)
  })

  it("returns zero allowance above £125,140", () => {
    expect(getPersonalAllowance(200_000)).toBe(0)
  })
})

describe("calculateIncomeTax", () => {
  it("returns zero tax for zero salary", () => {
    const result = calculateIncomeTax(0)
    expect(result.totalTax).toBe(0)
    expect(result.effectiveRate).toBe(0)
    expect(result.bands).toHaveLength(0)
  })

  it("returns zero tax for negative salary", () => {
    const result = calculateIncomeTax(-5_000)
    expect(result.totalTax).toBe(0)
    expect(result.effectiveRate).toBe(0)
  })

  it("returns zero tax within personal allowance (£12,570)", () => {
    const result = calculateIncomeTax(12_570)
    expect(result.totalTax).toBe(0)
    expect(result.effectiveRate).toBe(0)
  })

  it("calculates basic rate correctly for £30,000", () => {
    const result = calculateIncomeTax(30_000)
    // Taxable: £30,000 - £12,570 = £17,430
    // Tax: £17,430 * 0.20 = £3,486
    expect(result.totalTax).toBe(3_486)
    expect(result.effectiveRate).toBeCloseTo(3_486 / 30_000, 6)
    expect(result.bands).toHaveLength(2)
  })

  it("calculates higher rate correctly for £80,000", () => {
    const result = calculateIncomeTax(80_000)
    // Basic: (£50,270 - £12,570) * 0.20 = £7,540
    // Higher: (£80,000 - £50,270) * 0.40 = £11,892
    // Total: £19,432
    expect(result.totalTax).toBe(7_540 + 11_892)
    expect(result.bands).toHaveLength(3)
  })

  it("calculates additional rate correctly for £200,000", () => {
    const result = calculateIncomeTax(200_000)
    // Personal allowance = 0 (fully tapered)
    // Basic: £37,700 * 0.20 = £7,540
    // Higher: (£125,140 - £37,700) * 0.40 = £34,976
    // Additional: (£200,000 - £125,140) * 0.45 = £33,687
    // Total: £76,203 (with potential rounding)
    expect(result.totalTax).toBeCloseTo(7_540 + 34_976 + 33_687, 0)
    expect(result.bands).toHaveLength(3)
  })

  it("applies personal allowance taper for £120,000", () => {
    const result = calculateIncomeTax(120_000)
    // PA = £12,570 - £10,000 = £2,570
    // Basic: £37,700 * 0.20 = £7,540
    // Higher: (£120,000 - £40,270) * 0.40 = £31,892
    // Total: £39,432
    expect(result.totalTax).toBeCloseTo(7_540 + 31_892, 0)
  })

  it("keeps the basic band width at £37,700 when personal allowance tapers", () => {
    const result = calculateIncomeTax(120_000)
    const basicBand = result.bands.find((band) => band.name === "Basic rate (20%)")

    expect(basicBand?.from).toBe(2_570)
    expect(basicBand?.to).toBe(40_270)
    expect((basicBand?.to ?? 0) - (basicBand?.from ?? 0)).toBe(37_700)
  })
})

describe("calculateNI", () => {
  it("returns zero NI for zero salary", () => {
    const result = calculateNI(0)
    expect(result.totalNI).toBe(0)
    expect(result.effectiveRate).toBe(0)
  })

  it("returns zero NI for negative salary", () => {
    const result = calculateNI(-1_000)
    expect(result.totalNI).toBe(0)
  })

  it("returns zero NI below primary threshold", () => {
    const result = calculateNI(12_570)
    expect(result.totalNI).toBe(0)
  })

  it("calculates main rate NI for £30,000", () => {
    const result = calculateNI(30_000)
    // (£30,000 - £12,570) * 0.08 = £1,394.40
    expect(result.totalNI).toBeCloseTo(1_394.4, 2)
  })

  it("calculates upper rate NI for £80,000", () => {
    const result = calculateNI(80_000)
    // Main: (£50,270 - £12,570) * 0.08 = £3,016
    // Upper: (£80,000 - £50,270) * 0.02 = £594.60
    // Total: £3,610.60
    expect(result.totalNI).toBeCloseTo(3_016 + 594.6, 2)
    expect(result.bands).toHaveLength(3)
  })
})

describe("calculateEffectiveRate", () => {
  it("returns zero rates for zero salary", () => {
    const result = calculateEffectiveRate(0)
    expect(result.combinedRate).toBe(0)
    expect(result.takeHomePay).toBe(0)
  })

  it("returns correct take-home pay for £50,000", () => {
    const result = calculateEffectiveRate(50_000)
    const expectedTakeHome = 50_000 - result.incomeTax.totalTax - result.nationalInsurance.totalNI
    expect(result.takeHomePay).toBeCloseTo(expectedTakeHome, 2)
  })

  it("combined rate is higher than CGT effective rate for £80,000", () => {
    const result = calculateEffectiveRate(80_000)
    expect(result.combinedRate).toBeGreaterThan(result.capitalGainsComparison.effectiveRate)
  })

  it("provides CGT comparison with basic and higher rates", () => {
    const result = calculateEffectiveRate(50_000)
    expect(result.capitalGainsComparison.basicRate).toBe(0.18)
    expect(result.capitalGainsComparison.higherRate).toBe(0.24)
    expect(result.capitalGainsComparison.effectiveRate).toBeGreaterThan(0)
  })
})

describe("formatPercent", () => {
  it("formats zero correctly", () => {
    expect(formatPercent(0)).toBe("0.0%")
  })

  it("formats a simple percentage", () => {
    expect(formatPercent(0.2)).toBe("20.0%")
  })

  it("formats a fractional percentage with one decimal", () => {
    expect(formatPercent(0.1162)).toBe("11.6%")
  })

  it("formats 100%", () => {
    expect(formatPercent(1)).toBe("100.0%")
  })
})
