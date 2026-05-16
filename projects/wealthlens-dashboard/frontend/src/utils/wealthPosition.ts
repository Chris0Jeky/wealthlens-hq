/**
 * Wealth position utilities — determines where a UK household sits
 * in the wealth distribution using ONS Wealth and Assets Survey
 * (WAS) Round 7, 2018-2020 decile boundaries.
 *
 * Source: ONS Wealth and Assets Survey, Round 7, April 2018 to March 2020
 * URL: https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/bulletins/totalwealthingreatbritain/april2018tomarch2020
 * Accessed: 2026-05-16
 *
 * All calculation is client-side. No personal data is stored or transmitted.
 */

/**
 * ONS WAS Round 7 decile boundaries for total household net wealth.
 * Each entry represents the upper boundary of the decile (inclusive).
 * The 10th decile has no upper boundary.
 */
export const DECILE_BOUNDARIES = [
  15_400,   // Decile 1: up to £15,400
  52_800,   // Decile 2: up to £52,800
  112_000,  // Decile 3: up to £112,000
  183_300,  // Decile 4: up to £183,300
  302_500,  // Decile 5: up to £302,500
  457_200,  // Decile 6: up to £457,200
  669_900,  // Decile 7: up to £669,900
  990_000,  // Decile 8: up to £990,000
  1_480_000, // Decile 9: up to £1,480,000
] as const;

/**
 * Decile metadata with display labels and median values.
 * Medians are approximate mid-points from ONS WAS Round 7 tables.
 */
export interface DecileInfo {
  /** Decile number 1-10 */
  decile: number;
  /** Lower boundary (inclusive), null for decile 1 */
  lowerBound: number | null;
  /** Upper boundary (inclusive), null for decile 10 */
  upperBound: number | null;
  /** Approximate median wealth for this decile */
  median: number;
  /** Display label for the range */
  rangeLabel: string;
}

export const DECILE_DATA: readonly DecileInfo[] = [
  { decile: 1,  lowerBound: null,      upperBound: 15_400,    median: -900,     rangeLabel: "up to £15,400" },
  { decile: 2,  lowerBound: 15_400,    upperBound: 52_800,    median: 34_100,   rangeLabel: "£15,400 – £52,800" },
  { decile: 3,  lowerBound: 52_800,    upperBound: 112_000,   median: 82_400,   rangeLabel: "£52,800 – £112,000" },
  { decile: 4,  lowerBound: 112_000,   upperBound: 183_300,   median: 147_650,  rangeLabel: "£112,000 – £183,300" },
  { decile: 5,  lowerBound: 183_300,   upperBound: 302_500,   median: 242_900,  rangeLabel: "£183,300 – £302,500" },
  { decile: 6,  lowerBound: 302_500,   upperBound: 457_200,   median: 379_850,  rangeLabel: "£302,500 – £457,200" },
  { decile: 7,  lowerBound: 457_200,   upperBound: 669_900,   median: 563_550,  rangeLabel: "£457,200 – £669,900" },
  { decile: 8,  lowerBound: 669_900,   upperBound: 990_000,   median: 829_950,  rangeLabel: "£669,900 – £990,000" },
  { decile: 9,  lowerBound: 990_000,   upperBound: 1_480_000, median: 1_235_000, rangeLabel: "£990,000 – £1,480,000" },
  { decile: 10, lowerBound: 1_480_000, upperBound: null,      median: 2_500_000, rangeLabel: "£1,480,000+" },
];

/** Key comparison statistics from ONS WAS Round 7. */
export const COMPARISON_STATS = {
  /** Median total household net wealth across all households */
  medianUK: 302_500,
  /** Approximate median for the bottom 50% of households */
  medianBottom50: 12_500,
  /** Threshold to enter the top 10% of households by wealth */
  top10Threshold: 1_480_000,
  /** Source citation text */
  source: "ONS Wealth and Assets Survey, Round 7, April 2018 to March 2020",
  /** Source URL */
  sourceUrl: "https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/bulletins/totalwealthingreatbritain/april2018tomarch2020",
  /** Access date */
  accessed: "2026-05-16",
} as const;

/**
 * Returns the decile (1-10) for a given total net household wealth.
 * Decile 1 is the least wealthy 10%, decile 10 is the wealthiest 10%.
 *
 * @param wealth - Total net household wealth in GBP
 * @returns Decile number from 1 to 10
 */
export function getDecile(wealth: number): number {
  for (let i = 0; i < DECILE_BOUNDARIES.length; i++) {
    if (wealth <= DECILE_BOUNDARIES[i]) {
      return i + 1;
    }
  }
  return 10;
}

/**
 * Returns an approximate percentile (0-100) for a given total net
 * household wealth. Uses linear interpolation within the decile.
 *
 * This is an approximation: within each decile we assume a uniform
 * distribution between the lower and upper boundaries. The real
 * distribution is skewed, especially in deciles 1 and 10.
 *
 * @param wealth - Total net household wealth in GBP
 * @returns Approximate percentile from 0 to 100
 */
export function getPercentile(wealth: number): number {
  const decile = getDecile(wealth);
  const info = DECILE_DATA[decile - 1];

  // Base percentile for the start of this decile
  const basePercentile = (decile - 1) * 10;

  // For decile 1: interpolate from 0 to the upper bound
  if (info.lowerBound === null) {
    if (info.upperBound === null) return 50; // shouldn't happen
    // Allow negative wealth — clamp at 0th percentile
    if (wealth <= 0) return Math.max(0, basePercentile);
    const fraction = Math.min(wealth / info.upperBound, 1);
    return Math.round(basePercentile + fraction * 10);
  }

  // For decile 10: cap at 99th percentile since we can't know exact position
  if (info.upperBound === null) {
    // Rough interpolation: assume the 10th decile spans to ~3M for display
    const estimatedTop = 3_000_000;
    const range = estimatedTop - info.lowerBound;
    const fraction = Math.min((wealth - info.lowerBound) / range, 1);
    return Math.min(Math.round(basePercentile + fraction * 10), 99);
  }

  // For deciles 2-9: linear interpolation
  const range = info.upperBound - info.lowerBound;
  const fraction = Math.min(Math.max((wealth - info.lowerBound) / range, 0), 1);
  return Math.round(basePercentile + fraction * 10);
}

/**
 * Returns a contextual message describing the user's position in
 * the UK household wealth distribution.
 *
 * @param decile - Decile number from 1 to 10
 * @returns A plain-English contextual message
 */
export function getContext(decile: number): string {
  const householdsBelow = (decile - 1) * 10;

  const messages: Record<number, string> = {
    1: "You are in the bottom 10% of UK households by total net wealth. Many households in this decile have zero or negative net wealth, often due to debts exceeding assets.",
    2: "You have more wealth than roughly 1 in 10 UK households. This is below the national median, and typical of younger renters with modest savings.",
    3: "You have more wealth than roughly 2 in 10 UK households. Your wealth is still well below the national median of £302,500.",
    4: "You have more wealth than roughly 3 in 10 UK households. You are approaching but still below the national median.",
    5: "You are around the middle of UK household wealth. The median UK household has about £302,500 in total net wealth.",
    6: "You have more wealth than roughly 5 in 10 UK households. You are above the national median, likely with a combination of property equity and pensions.",
    7: "You have more wealth than roughly 6 in 10 UK households. Your wealth is roughly double the national median.",
    8: "You have more wealth than roughly 7 in 10 UK households. You are in the wealthier quarter of the UK population.",
    9: "You have more wealth than roughly 8 in 10 UK households. You are approaching the top 10% threshold of £1.48 million.",
    10: "You are in the wealthiest 10% of UK households. The top 10% hold approximately 43% of all household wealth in Great Britain.",
  };

  return messages[decile] ?? `You have more wealth than roughly ${householdsBelow} in 10 UK households.`;
}

/**
 * Formats a number as a GBP currency string.
 * Uses compact notation for large numbers.
 *
 * @param value - Amount in GBP
 * @returns Formatted string like "£1,234" or "-£500"
 */
export function formatGBP(value: number): string {
  const isNeg = value < 0;
  const abs = Math.abs(value);
  const formatted = abs.toLocaleString("en-GB", {
    maximumFractionDigits: 0,
  });
  return `${isNeg ? "-" : ""}£${formatted}`;
}
