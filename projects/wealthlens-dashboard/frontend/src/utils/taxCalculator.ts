/**
 * UK 2026-27 tax calculation utilities.
 *
 * Calculates income tax, National Insurance, and effective tax rates
 * for comparison with capital gains tax — highlighting the disparity
 * between how earned income and investment gains are taxed.
 *
 * Income Tax rates are for England, Wales, and Northern Ireland. Scotland uses
 * different bands for non-savings, non-dividend income.
 *
 * Source: HMRC Income Tax rates and bands 2026-27
 * URL: https://www.gov.uk/income-tax-rates
 * Accessed: 2026-05-17
 *
 * Source: HMRC National Insurance rates 2026-27
 * URL: https://www.gov.uk/national-insurance-rates-letters
 * Accessed: 2026-05-17
 *
 * Source: HMRC Capital Gains Tax rates 2026-27
 * URL: https://www.gov.uk/capital-gains-tax/rates
 * Accessed: 2026-05-17
 */

export interface TaxBand {
  name: string;
  from: number;
  to: number;
  rate: number;
  taxPaid: number;
}

export interface TaxBreakdown {
  bands: TaxBand[];
  totalTax: number;
  effectiveRate: number;
}

export interface NIBand {
  name: string;
  from: number;
  to: number;
  rate: number;
  niPaid: number;
}

export interface NIBreakdown {
  bands: NIBand[];
  totalNI: number;
  effectiveRate: number;
}

export interface EffectiveRates {
  incomeTax: TaxBreakdown;
  nationalInsurance: NIBreakdown;
  combinedTax: number;
  combinedRate: number;
  takeHomePay: number;
  capitalGainsComparison: {
    basicRate: number;
    higherRate: number;
    effectiveRate: number;
  };
}

const PERSONAL_ALLOWANCE = 12_570;
const PERSONAL_ALLOWANCE_TAPER_START = 100_000;
const PERSONAL_ALLOWANCE_TAPER_RATE = 0.5;
const INCOME_TAX_BASIC_BAND_WIDTH = 37_700;
const INCOME_TAX_ADDITIONAL_RATE_THRESHOLD = 125_140;

const NI_PRIMARY_THRESHOLD = 12_570;
const NI_UPPER_EARNINGS_LIMIT = 50_270;

const CGT_ANNUAL_EXEMPT = 3_000;
const CGT_BASIC_RATE = 0.18;
const CGT_HIGHER_RATE = 0.24;
const CGT_BASIC_RATE_BAND_WIDTH = 37_700;

/**
 * Calculates the personal allowance after taper for incomes over £100,000.
 * For every £2 earned over £100,000 the personal allowance is reduced by £1,
 * until it reaches zero at £125,140.
 */
export function getPersonalAllowance(salary: number): number {
  if (salary <= PERSONAL_ALLOWANCE_TAPER_START) {
    return PERSONAL_ALLOWANCE;
  }
  const reduction = Math.floor(
    (salary - PERSONAL_ALLOWANCE_TAPER_START) * PERSONAL_ALLOWANCE_TAPER_RATE,
  );
  return Math.max(0, PERSONAL_ALLOWANCE - reduction);
}

/**
 * Calculates income tax for a given annual gross salary using 2026-27
 * England, Wales, and Northern Ireland bands.
 *
 * Personal allowance tapers by £1 for every £2 over £100,000.
 */
export function calculateIncomeTax(salary: number): TaxBreakdown {
  if (salary <= 0) {
    return { bands: [], totalTax: 0, effectiveRate: 0 };
  }

  const personalAllowance = getPersonalAllowance(salary);
  const bands: TaxBand[] = [];

  const basicRateLimit = personalAllowance + INCOME_TAX_BASIC_BAND_WIDTH;
  const taxBands = [
    { name: "Personal Allowance", from: 0, to: personalAllowance, rate: 0 },
    { name: "Basic rate (20%)", from: personalAllowance, to: basicRateLimit, rate: 0.20 },
    {
      name: "Higher rate (40%)",
      from: basicRateLimit,
      to: INCOME_TAX_ADDITIONAL_RATE_THRESHOLD,
      rate: 0.40,
    },
    {
      name: "Additional rate (45%)",
      from: INCOME_TAX_ADDITIONAL_RATE_THRESHOLD,
      to: Infinity,
      rate: 0.45,
    },
  ];

  let totalTax = 0;

  for (const band of taxBands) {
    if (salary <= band.from) break;
    if (band.from >= band.to) continue;

    const taxableInBand = Math.min(salary, band.to) - band.from;
    const taxPaid = taxableInBand * band.rate;

    bands.push({
      name: band.name,
      from: band.from,
      to: Math.min(salary, band.to),
      rate: band.rate,
      taxPaid,
    });

    totalTax += taxPaid;
  }

  return {
    bands,
    totalTax,
    effectiveRate: salary > 0 ? totalTax / salary : 0,
  };
}

/**
 * Calculates Class 1 employee National Insurance for a given annual salary.
 * 2026-27 rates: 0% up to £12,570, 8% from £12,571 to £50,270, 2% above.
 */
export function calculateNI(salary: number): NIBreakdown {
  if (salary <= 0) {
    return { bands: [], totalNI: 0, effectiveRate: 0 };
  }

  const niBands = [
    { name: "Below threshold (0%)", from: 0, to: NI_PRIMARY_THRESHOLD, rate: 0 },
    { name: "Main rate (8%)", from: NI_PRIMARY_THRESHOLD, to: NI_UPPER_EARNINGS_LIMIT, rate: 0.08 },
    { name: "Upper rate (2%)", from: NI_UPPER_EARNINGS_LIMIT, to: Infinity, rate: 0.02 },
  ];

  const bands: NIBand[] = [];
  let totalNI = 0;

  for (const band of niBands) {
    if (salary <= band.from) break;

    const earningsInBand = Math.min(salary, band.to) - band.from;
    const niPaid = earningsInBand * band.rate;

    bands.push({
      name: band.name,
      from: band.from,
      to: Math.min(salary, band.to),
      rate: band.rate,
      niPaid,
    });

    totalNI += niPaid;
  }

  return {
    bands,
    totalNI,
    effectiveRate: salary > 0 ? totalNI / salary : 0,
  };
}

/**
 * Calculates the effective capital gains tax rate if the same amount
 * were received as capital gains rather than salary.
 * Uses 2026-27 rates (general assets, not carried interest).
 */
function calculateCGTComparison(amount: number): {
  basicRate: number;
  higherRate: number;
  effectiveRate: number;
} {
  if (amount <= 0) {
    return { basicRate: CGT_BASIC_RATE, higherRate: CGT_HIGHER_RATE, effectiveRate: 0 };
  }

  const taxableGain = Math.max(0, amount - CGT_ANNUAL_EXEMPT);

  const basicPortion = Math.min(taxableGain, CGT_BASIC_RATE_BAND_WIDTH);
  const higherPortion = Math.max(0, taxableGain - CGT_BASIC_RATE_BAND_WIDTH);
  const cgtPaid = basicPortion * CGT_BASIC_RATE + higherPortion * CGT_HIGHER_RATE;

  return {
    basicRate: CGT_BASIC_RATE,
    higherRate: CGT_HIGHER_RATE,
    effectiveRate: amount > 0 ? cgtPaid / amount : 0,
  };
}

/**
 * Calculates combined effective rates (income tax + NI) and compares
 * with capital gains tax for the same amount.
 */
export function calculateEffectiveRate(salary: number): EffectiveRates {
  const incomeTax = calculateIncomeTax(salary);
  const nationalInsurance = calculateNI(salary);
  const combinedTax = incomeTax.totalTax + nationalInsurance.totalNI;
  const combinedRate = salary > 0 ? combinedTax / salary : 0;
  const takeHomePay = salary - combinedTax;
  const capitalGainsComparison = calculateCGTComparison(salary);

  return {
    incomeTax,
    nationalInsurance,
    combinedTax,
    combinedRate,
    takeHomePay,
    capitalGainsComparison,
  };
}

/**
 * Formats a number as a percentage string with one decimal place.
 */
export function formatPercent(n: number): string {
  return `${(n * 100).toFixed(1)}%`;
}
