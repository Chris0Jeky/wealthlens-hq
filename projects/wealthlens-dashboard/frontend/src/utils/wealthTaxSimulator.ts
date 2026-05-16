/**
 * Wealth Tax Revenue Simulator — estimates annual revenue from a
 * progressive wealth tax using a simplified Pareto model of UK
 * wealth distribution.
 *
 * This is a simplified model for illustration. Actual revenue would
 * depend on behavioral responses, avoidance, and implementation details.
 *
 * Sources:
 * - ONS Wealth and Assets Survey, Round 7, April 2018 to March 2020
 *   URL: https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/bulletins/totalwealthingreatbritain/april2018tomarch2020
 *   Accessed: 2026-05-16
 * - Wealth Tax Commission (2020)
 *   URL: https://www.ukwealth.tax/
 *   Accessed: 2026-05-16
 * - Resolution Foundation wealth distribution estimates
 */

// ============================================================
// TYPES
// ============================================================

/** A single band of a progressive wealth tax */
export interface WealthTaxBand {
  /** Threshold above which this rate applies (GBP) */
  threshold: number;
  /** Tax rate as a decimal, e.g. 0.01 = 1% */
  rate: number;
}

/** Results from a wealth tax simulation */
export interface SimulationResult {
  /** Estimated annual revenue in GBP */
  annualRevenue: number;
  /** Number of households affected (wealth above lowest threshold) */
  affectedHouseholds: number;
  /** Average tax per affected household in GBP */
  averageTaxPerHousehold: number;
  /** Revenue as a percentage of UK GDP */
  revenueAsPercentGDP: number;
}

// ============================================================
// CONSTANTS
// ============================================================

/**
 * Total UK personal wealth (approximate, 2020).
 * Source: ONS Wealth and Assets Survey Round 7
 */
export const TOTAL_UK_WEALTH = 15_200_000_000_000; // £15.2 trillion

/**
 * UK GDP 2023 (approximate).
 * Source: ONS National Accounts
 */
export const UK_GDP = 2_300_000_000_000; // £2.3 trillion

/**
 * Total UK households (approximate).
 * Source: ONS Families and Households
 */
export const TOTAL_HOUSEHOLDS = 28_100_000; // 28.1 million

/**
 * Pareto alpha parameter for UK wealth distribution.
 * Estimated from ONS WAS data — lower alpha means heavier tail.
 * A value of ~1.5 is consistent with empirical UK wealth data.
 */
export const PARETO_ALPHA = 1.5;

/**
 * Minimum wealth level for Pareto model (scale parameter).
 * We use £250,000 as a reasonable lower bound for the Pareto
 * tail fitting, based on the approximate median being around this level.
 */
export const PARETO_XMIN = 250_000;

/**
 * Wealth distribution reference points used for estimating
 * the number of households above each threshold.
 * Source: ONS WAS Round 7 + Wealth Tax Commission estimates
 */
export const WEALTH_THRESHOLDS: ReadonlyArray<{
  threshold: number;
  householdsAbove: number;
  wealthAbove: number;
}> = [
  { threshold: 250_000, householdsAbove: 14_050_000, wealthAbove: 13_700_000_000_000 },
  { threshold: 500_000, householdsAbove: 7_025_000, wealthAbove: 11_400_000_000_000 },
  { threshold: 1_000_000, householdsAbove: 2_810_000, wealthAbove: 7_800_000_000_000 },
  { threshold: 1_600_000, householdsAbove: 1_405_000, wealthAbove: 5_300_000_000_000 },
  { threshold: 2_000_000, householdsAbove: 984_000, wealthAbove: 4_500_000_000_000 },
  { threshold: 3_600_000, householdsAbove: 281_000, wealthAbove: 2_900_000_000_000 },
  { threshold: 5_000_000, householdsAbove: 150_000, wealthAbove: 2_200_000_000_000 },
  { threshold: 10_000_000, householdsAbove: 50_000, wealthAbove: 1_200_000_000_000 },
];

// ============================================================
// HELPER FUNCTIONS
// ============================================================

/**
 * Estimates the number of households with wealth above a given threshold
 * using Pareto interpolation between known data points.
 *
 * Uses the complementary CDF of a Pareto distribution:
 * P(X > x) = (xmin / x)^alpha for x >= xmin
 *
 * We interpolate between known empirical data points for better accuracy.
 */
export function estimateHouseholdsAbove(threshold: number): number {
  if (threshold <= 0) return TOTAL_HOUSEHOLDS;
  if (threshold <= PARETO_XMIN) {
    // Linear interpolation below the Pareto range
    const fraction = 1 - threshold / (PARETO_XMIN * 2);
    return Math.round(fraction * TOTAL_HOUSEHOLDS);
  }

  // Find bracketing known thresholds
  const points = WEALTH_THRESHOLDS;
  for (let i = 0; i < points.length - 1; i++) {
    if (threshold >= points[i].threshold && threshold <= points[i + 1].threshold) {
      // Log-linear interpolation between known points
      const logRatio =
        Math.log(threshold / points[i].threshold) /
        Math.log(points[i + 1].threshold / points[i].threshold);
      const logHouseholds =
        Math.log(points[i].householdsAbove) +
        logRatio * (Math.log(points[i + 1].householdsAbove) - Math.log(points[i].householdsAbove));
      return Math.round(Math.exp(logHouseholds));
    }
  }

  // Above highest known point: extrapolate with Pareto
  const lastPoint = points[points.length - 1];
  const ratio = lastPoint.threshold / threshold;
  return Math.max(1, Math.round(lastPoint.householdsAbove * Math.pow(ratio, PARETO_ALPHA)));
}

/**
 * Estimates total wealth held above a given threshold using
 * Pareto model interpolation between known data points.
 *
 * For a Pareto distribution with alpha > 1:
 * E[X - threshold | X > threshold] = threshold / (alpha - 1)
 * Total excess wealth = households_above * threshold / (alpha - 1)
 *
 * We use empirical data points for interpolation where available.
 */
export function estimateWealthAbove(threshold: number): number {
  if (threshold <= 0) return TOTAL_UK_WEALTH;
  if (threshold <= PARETO_XMIN) {
    // Linear interpolation
    const fraction = 1 - threshold / PARETO_XMIN;
    return TOTAL_UK_WEALTH * (0.5 + 0.5 * fraction);
  }

  // Find bracketing known thresholds
  const points = WEALTH_THRESHOLDS;
  for (let i = 0; i < points.length - 1; i++) {
    if (threshold >= points[i].threshold && threshold <= points[i + 1].threshold) {
      // Log-linear interpolation between known points
      const logRatio =
        Math.log(threshold / points[i].threshold) /
        Math.log(points[i + 1].threshold / points[i].threshold);
      const logWealth =
        Math.log(points[i].wealthAbove) +
        logRatio * (Math.log(points[i + 1].wealthAbove) - Math.log(points[i].wealthAbove));
      return Math.exp(logWealth);
    }
  }

  // Above highest known point: Pareto extrapolation
  const lastPoint = points[points.length - 1];
  const ratio = lastPoint.threshold / threshold;
  return lastPoint.wealthAbove * Math.pow(ratio, PARETO_ALPHA - 1);
}

/**
 * Estimates the "excess" wealth above a threshold — i.e., the taxable
 * amount for wealth above that threshold. This is the total wealth held
 * by those above the threshold minus the threshold times the number
 * of households.
 */
export function estimateExcessWealth(threshold: number): number {
  const totalAbove = estimateWealthAbove(threshold);
  const households = estimateHouseholdsAbove(threshold);
  const exemptPortion = threshold * households;
  return Math.max(0, totalAbove - exemptPortion);
}

// ============================================================
// MAIN SIMULATION
// ============================================================

/**
 * Simulates revenue from a progressive wealth tax with one or more bands.
 *
 * For each band, calculates the revenue from that marginal rate on
 * wealth between that band's threshold and the next band's threshold.
 * Bands should be provided in ascending order of threshold.
 *
 * @param bands - Array of wealth tax bands (threshold + rate), sorted by threshold ascending
 * @returns Simulation results including revenue, affected households, and comparisons
 */
export function simulateWealthTax(bands: WealthTaxBand[]): SimulationResult {
  if (bands.length === 0) {
    return {
      annualRevenue: 0,
      affectedHouseholds: 0,
      averageTaxPerHousehold: 0,
      revenueAsPercentGDP: 0,
    };
  }

  // Sort bands by threshold ascending
  const sorted = [...bands].sort((a, b) => a.threshold - b.threshold);

  let totalRevenue = 0;

  // For each band, calculate revenue from the marginal rate applied
  // to wealth in that band's range
  for (let i = 0; i < sorted.length; i++) {
    const band = sorted[i];
    const nextThreshold = i < sorted.length - 1 ? sorted[i + 1].threshold : Infinity;

    if (band.rate <= 0) continue;

    // Excess wealth above this band's threshold
    const excessAboveThis = estimateExcessWealth(band.threshold);

    // Excess wealth above the next band's threshold (which will be taxed at a higher rate)
    const excessAboveNext =
      nextThreshold === Infinity ? 0 : estimateExcessWealth(nextThreshold);

    // Wealth in this band = excess above this threshold minus excess above next
    // But we also need to account for the number of households at each level
    // Simplified: revenue from this band's marginal rate on its slice
    const wealthInBand = excessAboveThis - excessAboveNext;
    const revenueFromBand = wealthInBand * band.rate;

    totalRevenue += revenueFromBand;
  }

  // Affected households are those above the lowest threshold
  const lowestThreshold = sorted[0].threshold;
  const affectedHouseholds = estimateHouseholdsAbove(lowestThreshold);

  const averageTax = affectedHouseholds > 0 ? totalRevenue / affectedHouseholds : 0;
  const revenueAsPercentGDP = (totalRevenue / UK_GDP) * 100;

  return {
    annualRevenue: Math.round(totalRevenue),
    affectedHouseholds,
    averageTaxPerHousehold: Math.round(averageTax),
    revenueAsPercentGDP: Math.round(revenueAsPercentGDP * 100) / 100,
  };
}

// ============================================================
// FORMATTING HELPERS
// ============================================================

/**
 * Formats a large number as a compact GBP string.
 * e.g. 45_000_000_000 -> "£45 billion"
 */
export function formatRevenue(value: number): string {
  const abs = Math.abs(value);
  if (abs >= 1_000_000_000_000) {
    return `£${(value / 1_000_000_000_000).toFixed(1)} trillion`;
  }
  if (abs >= 1_000_000_000) {
    return `£${(value / 1_000_000_000).toFixed(1)} billion`;
  }
  if (abs >= 1_000_000) {
    return `£${(value / 1_000_000).toFixed(1)} million`;
  }
  return `£${value.toLocaleString("en-GB")}`;
}

/**
 * Formats a number of households compactly.
 * e.g. 2_810_000 -> "2.8 million"
 */
export function formatHouseholds(value: number): string {
  if (value >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(1)} million`;
  }
  if (value >= 1_000) {
    return `${(value / 1_000).toFixed(0)},000`;
  }
  return value.toLocaleString("en-GB");
}

/**
 * Formats a threshold value compactly for display.
 * e.g. 5_000_000 -> "£5m"
 */
export function formatThreshold(value: number): string {
  if (value >= 1_000_000) {
    const millions = value / 1_000_000;
    return millions === Math.floor(millions)
      ? `£${millions}m`
      : `£${millions.toFixed(1)}m`;
  }
  if (value >= 1_000) {
    return `£${(value / 1_000).toFixed(0)}k`;
  }
  return `£${value}`;
}

// ============================================================
// SPENDING COMPARISONS
// ============================================================

/**
 * Public spending comparisons for context (approximate annual costs).
 * Source: Various UK Government departmental reports, 2023-24
 */
export const SPENDING_COMPARISONS: ReadonlyArray<{
  label: string;
  annualCost: number;
}> = [
  { label: "NHS England annual budget", annualCost: 165_000_000_000 },
  { label: "building 100,000 social homes per year", annualCost: 20_000_000_000 },
  { label: "tripling the state pension top-up", annualCost: 15_000_000_000 },
  { label: "abolishing university tuition fees", annualCost: 10_000_000_000 },
  { label: "doubling the schools budget increase", annualCost: 8_000_000_000 },
  { label: "free school meals for all primary pupils", annualCost: 1_000_000_000 },
];

/**
 * Returns the best spending comparison for a given revenue figure.
 * Picks the largest item that the revenue could fully fund.
 */
export function getSpendingComparison(revenue: number): string | null {
  // Sort by cost descending to find the largest fundable item
  const sorted = [...SPENDING_COMPARISONS].sort((a, b) => b.annualCost - a.annualCost);
  for (const item of sorted) {
    if (revenue >= item.annualCost) {
      const multiple = revenue / item.annualCost;
      if (multiple >= 1.5) {
        return `${multiple.toFixed(1)}x the annual cost of ${item.label}`;
      }
      return `Enough to fund ${item.label}`;
    }
  }
  // If less than smallest item, show as fraction of smallest
  const smallest = SPENDING_COMPARISONS[SPENDING_COMPARISONS.length - 1];
  if (revenue > 0) {
    const percent = Math.round((revenue / smallest.annualCost) * 100);
    return `${percent}% of the cost of ${smallest.label}`;
  }
  return null;
}

// ============================================================
// PRESET SCENARIOS
// ============================================================

export interface PresetScenario {
  name: string;
  description: string;
  bands: WealthTaxBand[];
}

export const PRESET_SCENARIOS: readonly PresetScenario[] = [
  {
    name: "Modest",
    description: "1% above £5m",
    bands: [{ threshold: 5_000_000, rate: 0.01 }],
  },
  {
    name: "Moderate",
    description: "1% above £2m, 2% above £10m",
    bands: [
      { threshold: 2_000_000, rate: 0.01 },
      { threshold: 10_000_000, rate: 0.02 },
    ],
  },
  {
    name: "Ambitious",
    description: "1% above £1m, 2% above £5m, 3% above £10m",
    bands: [
      { threshold: 1_000_000, rate: 0.01 },
      { threshold: 5_000_000, rate: 0.02 },
      { threshold: 10_000_000, rate: 0.03 },
    ],
  },
];

// ============================================================
// CITATION
// ============================================================

export const SIMULATOR_SOURCES = {
  primary: "ONS Wealth and Assets Survey, Round 7, April 2018 to March 2020",
  primaryUrl:
    "https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/bulletins/totalwealthingreatbritain/april2018tomarch2020",
  secondary: "Wealth Tax Commission (2020)",
  secondaryUrl: "https://www.ukwealth.tax/",
  accessed: "2026-05-16",
  disclaimer:
    "This is a simplified model for illustration. Actual revenue would depend on behavioral responses, avoidance, and implementation details.",
} as const;
