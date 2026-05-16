import { describe, it, expect } from "vitest";
import {
  getDecile,
  getPercentile,
  getContext,
  formatGBP,
  DECILE_BOUNDARIES,
  DECILE_DATA,
  COMPARISON_STATS,
} from "@/utils/wealthPosition";

describe("getDecile", () => {
  it("returns 1 for negative wealth", () => {
    expect(getDecile(-5000)).toBe(1);
  });

  it("returns 1 for zero wealth", () => {
    expect(getDecile(0)).toBe(1);
  });

  it("returns 1 for wealth at the upper boundary of decile 1", () => {
    expect(getDecile(15_400)).toBe(1);
  });

  it("returns 2 for wealth just above decile 1 boundary", () => {
    expect(getDecile(15_401)).toBe(2);
  });

  it("returns 5 for median UK wealth (£302,500)", () => {
    expect(getDecile(302_500)).toBe(5);
  });

  it("returns 6 for wealth just above median", () => {
    expect(getDecile(302_501)).toBe(6);
  });

  it("returns 9 for wealth at upper boundary of decile 9", () => {
    expect(getDecile(1_480_000)).toBe(9);
  });

  it("returns 10 for wealth above £1,480,000", () => {
    expect(getDecile(1_480_001)).toBe(10);
  });

  it("returns 10 for very large wealth", () => {
    expect(getDecile(100_000_000)).toBe(10);
  });

  it("correctly assigns each boundary to its decile", () => {
    DECILE_BOUNDARIES.forEach((boundary, i) => {
      expect(getDecile(boundary)).toBe(i + 1);
    });
  });

  it("correctly assigns values just above each boundary to the next decile", () => {
    DECILE_BOUNDARIES.forEach((boundary, i) => {
      expect(getDecile(boundary + 1)).toBe(i + 2);
    });
  });
});

describe("getPercentile", () => {
  it("returns 0 for very negative wealth", () => {
    expect(getPercentile(-50_000)).toBe(0);
  });

  it("returns a low percentile for zero wealth", () => {
    const p = getPercentile(0);
    expect(p).toBeGreaterThanOrEqual(0);
    expect(p).toBeLessThanOrEqual(10);
  });

  it("returns roughly 50 for median UK wealth", () => {
    const p = getPercentile(302_500);
    expect(p).toBeGreaterThanOrEqual(45);
    expect(p).toBeLessThanOrEqual(55);
  });

  it("returns a high percentile for wealth above £1.48M", () => {
    const p = getPercentile(2_000_000);
    expect(p).toBeGreaterThanOrEqual(90);
    expect(p).toBeLessThanOrEqual(99);
  });

  it("never returns above 99", () => {
    expect(getPercentile(999_999_999)).toBeLessThanOrEqual(99);
  });

  it("never returns below 0", () => {
    expect(getPercentile(-999_999)).toBeGreaterThanOrEqual(0);
  });

  it("increases monotonically with wealth", () => {
    const values = [-5000, 0, 5000, 50_000, 200_000, 500_000, 1_000_000, 2_000_000];
    for (let i = 1; i < values.length; i++) {
      expect(getPercentile(values[i])).toBeGreaterThanOrEqual(
        getPercentile(values[i - 1]),
      );
    }
  });
});

describe("getContext", () => {
  it("returns a string for every decile 1-10", () => {
    for (let d = 1; d <= 10; d++) {
      const msg = getContext(d);
      expect(typeof msg).toBe("string");
      expect(msg.length).toBeGreaterThan(0);
    }
  });

  it("mentions negative or zero wealth for decile 1", () => {
    const msg = getContext(1);
    expect(msg.toLowerCase()).toContain("bottom 10%");
  });

  it("mentions the median for decile 5", () => {
    const msg = getContext(5);
    expect(msg).toContain("302,500");
  });

  it("mentions the top 10% for decile 10", () => {
    const msg = getContext(10);
    expect(msg.toLowerCase()).toContain("wealthiest 10%");
  });

  it("returns a fallback for out-of-range deciles", () => {
    const msg = getContext(11);
    expect(typeof msg).toBe("string");
    expect(msg.length).toBeGreaterThan(0);
  });
});

describe("formatGBP", () => {
  it("formats positive numbers with pound sign", () => {
    expect(formatGBP(5000)).toBe("£5,000");
  });

  it("formats zero", () => {
    expect(formatGBP(0)).toBe("£0");
  });

  it("formats negative numbers with minus sign before pound", () => {
    expect(formatGBP(-900)).toBe("-£900");
  });

  it("formats large numbers with comma separators", () => {
    expect(formatGBP(1_480_000)).toBe("£1,480,000");
  });

  it("rounds to whole numbers", () => {
    expect(formatGBP(5000.75)).toBe("£5,001");
  });
});

describe("DECILE_DATA", () => {
  it("has exactly 10 entries", () => {
    expect(DECILE_DATA).toHaveLength(10);
  });

  it("has decile numbers 1 through 10", () => {
    DECILE_DATA.forEach((d, i) => {
      expect(d.decile).toBe(i + 1);
    });
  });

  it("decile 1 has null lower bound", () => {
    expect(DECILE_DATA[0].lowerBound).toBeNull();
  });

  it("decile 10 has null upper bound", () => {
    expect(DECILE_DATA[9].upperBound).toBeNull();
  });

  it("has continuous boundaries (upper of n = lower of n+1)", () => {
    for (let i = 0; i < DECILE_DATA.length - 1; i++) {
      expect(DECILE_DATA[i].upperBound).toBe(DECILE_DATA[i + 1].lowerBound);
    }
  });
});

describe("COMPARISON_STATS", () => {
  it("has the correct median UK wealth", () => {
    expect(COMPARISON_STATS.medianUK).toBe(302_500);
  });

  it("has the correct top 10% threshold", () => {
    expect(COMPARISON_STATS.top10Threshold).toBe(1_480_000);
  });

  it("cites ONS WAS", () => {
    expect(COMPARISON_STATS.source).toContain("ONS");
    expect(COMPARISON_STATS.source).toContain("Round 7");
  });
});
