import { describe, it, expect } from "vitest";
import {
  calculateEmployeeTax,
  calculateBillionaireTax,
  formatPercentage,
  formatGBP,
  PERSONAL_ALLOWANCE,
  CGT_HIGHER_RATE,
} from "@/utils/taxCalculator";

describe("calculateEmployeeTax", () => {
  it("returns zero tax for zero salary", () => {
    const result = calculateEmployeeTax(0);
    expect(result.incomeTax).toBe(0);
    expect(result.nics).toBe(0);
    expect(result.effectiveRate).toBe(0);
  });

  it("returns zero tax for salary within personal allowance", () => {
    const result = calculateEmployeeTax(12_000);
    expect(result.incomeTax).toBe(0);
    expect(result.nics).toBe(0);
    expect(result.netPay).toBe(12_000);
  });

  it("returns zero income tax at exactly the PA boundary", () => {
    const result = calculateEmployeeTax(PERSONAL_ALLOWANCE);
    expect(result.incomeTax).toBe(0);
  });

  it("calculates basic rate tax correctly for £30,000 salary", () => {
    const result = calculateEmployeeTax(30_000);
    const expectedIT = (30_000 - 12_570) * 0.2;
    expect(result.incomeTax).toBeCloseTo(expectedIT, 0);
    expect(result.bands.length).toBe(2);
    expect(result.bands[1].name).toBe("Basic Rate");
  });

  it("calculates higher rate tax for £60,000 salary", () => {
    const result = calculateEmployeeTax(60_000);
    const basicIT = (50_270 - 12_570) * 0.2;
    const higherIT = (60_000 - 50_270) * 0.4;
    expect(result.incomeTax).toBeCloseTo(basicIT + higherIT, 0);
  });

  it("handles PA taper correctly at £110,000", () => {
    const result = calculateEmployeeTax(110_000);
    const effectivePA = Math.max(0, 12_570 - Math.floor((110_000 - 100_000) / 2));
    expect(effectivePA).toBe(7_570);

    const basicIT = (50_270 - effectivePA) * 0.2;
    const higherIT = (110_000 - 50_270) * 0.4;
    expect(result.incomeTax).toBeCloseTo(basicIT + higherIT, 0);
  });

  it("handles fully tapered PA at £125,140", () => {
    const result = calculateEmployeeTax(125_140);
    const effectivePA = Math.max(0, 12_570 - Math.floor((125_140 - 100_000) / 2));
    expect(effectivePA).toBe(0);

    const basicIT = (50_270 - 0) * 0.2;
    const higherIT = (125_140 - 50_270) * 0.4;
    expect(result.incomeTax).toBeCloseTo(basicIT + higherIT, 0);
  });

  it("calculates additional rate correctly at £200,000", () => {
    const result = calculateEmployeeTax(200_000);
    const basicIT = 50_270 * 0.2;
    const higherIT = (125_140 - 50_270) * 0.4;
    const additionalIT = (200_000 - 125_140) * 0.45;
    expect(result.incomeTax).toBeCloseTo(basicIT + higherIT + additionalIT, 0);
  });

  it("calculates NICs correctly", () => {
    const result = calculateEmployeeTax(60_000);
    const mainNIC = (50_270 - 12_570) * 0.08;
    const higherNIC = (60_000 - 50_270) * 0.02;
    expect(result.nics).toBeCloseTo(mainNIC + higherNIC, 0);
  });

  it("effective rate is totalTax / salary", () => {
    const result = calculateEmployeeTax(50_000);
    expect(result.effectiveRate).toBeCloseTo(result.totalTax / 50_000, 6);
  });

  it("netPay equals salary minus totalTax", () => {
    const result = calculateEmployeeTax(80_000);
    expect(result.netPay).toBeCloseTo(80_000 - result.totalTax, 2);
  });

  it("handles negative salary gracefully", () => {
    const result = calculateEmployeeTax(-1000);
    expect(result.incomeTax).toBe(0);
    expect(result.nics).toBe(0);
    expect(result.netPay).toBe(0);
  });
});

describe("calculateBillionaireTax", () => {
  it("returns zero for zero gains", () => {
    const result = calculateBillionaireTax(0);
    expect(result.cgtPaid).toBe(0);
    expect(result.effectiveRate).toBe(0);
  });

  it("applies higher CGT rate (24%) to realised gains", () => {
    const result = calculateBillionaireTax(10_000_000, 1.0);
    const expected = (10_000_000 - 3_000) * CGT_HIGHER_RATE;
    expect(result.cgtPaid).toBeCloseTo(expected, 0);
  });

  it("effective rate is much lower than realised rate due to unrealised gains", () => {
    const result = calculateBillionaireTax(100_000_000, 0.2);
    expect(result.effectiveRate).toBeLessThan(result.realisedRate);
    expect(result.effectiveRate).toBeCloseTo(result.realisedRate * 0.2, 2);
  });

  it("unrealised + realised = total gains", () => {
    const result = calculateBillionaireTax(50_000_000, 0.3);
    expect(result.unrealisedGains + result.realisedGains).toBe(50_000_000);
  });

  it("returns zero for negative gains", () => {
    const result = calculateBillionaireTax(-5_000_000);
    expect(result.cgtPaid).toBe(0);
    expect(result.effectiveRate).toBe(0);
  });
});

describe("formatPercentage", () => {
  it("formats 0.2345 as 23.4%", () => {
    expect(formatPercentage(0.2345)).toBe("23.4%");
  });

  it("formats 0 as 0.0%", () => {
    expect(formatPercentage(0)).toBe("0.0%");
  });

  it("formats 1 as 100.0%", () => {
    expect(formatPercentage(1)).toBe("100.0%");
  });
});

describe("formatGBP", () => {
  it("formats positive amounts with £ and commas", () => {
    expect(formatGBP(1234)).toBe("£1,234");
  });

  it("formats negative amounts with -£", () => {
    expect(formatGBP(-500)).toBe("-£500");
  });

  it("formats zero", () => {
    expect(formatGBP(0)).toBe("£0");
  });

  it("formats large amounts", () => {
    expect(formatGBP(1_000_000)).toBe("£1,000,000");
  });
});
