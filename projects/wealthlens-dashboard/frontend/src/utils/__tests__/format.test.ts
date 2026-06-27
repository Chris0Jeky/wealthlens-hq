import { describe, it, expect } from "vitest"
import { formatCurrency, formatPercent, formatCompact } from "@/utils/format"

describe("formatCurrency", () => {
  it("formats billions", () => {
    expect(formatCurrency(1_500_000_000)).toBe("£2bn")
    expect(formatCurrency(1_500_000_000, 1)).toBe("£1.5bn")
  })

  it("formats millions", () => {
    expect(formatCurrency(2_500_000)).toBe("£3m")
    expect(formatCurrency(2_500_000, 1)).toBe("£2.5m")
  })

  it("formats thousands", () => {
    expect(formatCurrency(45_000)).toBe("£45k")
    expect(formatCurrency(45_500, 1)).toBe("£45.5k")
  })

  it("formats small values", () => {
    expect(formatCurrency(500)).toBe("£500")
    expect(formatCurrency(99.5, 2)).toBe("£99.50")
  })

  it("handles negative values", () => {
    expect(formatCurrency(-2_000_000, 1)).toBe("£-2.0m")
  })
})

describe("formatPercent", () => {
  it("formats with default 1 decimal", () => {
    expect(formatPercent(45.678)).toBe("45.7%")
  })

  it("formats with custom decimals", () => {
    expect(formatPercent(12.3456, 2)).toBe("12.35%")
  })

  it("formats zero", () => {
    expect(formatPercent(0)).toBe("0.0%")
  })
})

describe("formatCompact", () => {
  it("formats billions", () => {
    expect(formatCompact(3_200_000_000)).toBe("3.2B")
  })

  it("formats millions", () => {
    expect(formatCompact(7_800_000)).toBe("7.8M")
  })

  it("formats thousands", () => {
    expect(formatCompact(12_300)).toBe("12.3K")
  })

  it("returns raw number for small values", () => {
    expect(formatCompact(42)).toBe("42")
  })
})
