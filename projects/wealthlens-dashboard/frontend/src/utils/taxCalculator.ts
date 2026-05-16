/**
 * Tax calculator utilities — compares an employee's effective tax rate
 * to a billionaire's effective tax on wealth gains.
 *
 * Uses HMRC 2024-25 tax year rates for Income Tax, National Insurance
 * Contributions, Capital Gains Tax, and Dividend Tax.
 *
 * Source: HMRC Income Tax rates and allowances 2024-25
 * URL: https://www.gov.uk/income-tax-rates
 * Accessed: 2026-05-16
 *
 * Source: HMRC National Insurance rates 2024-25
 * URL: https://www.gov.uk/national-insurance-rates-letters
 * Accessed: 2026-05-16
 *
 * Source: HMRC Capital Gains Tax rates 2024-25
 * URL: https://www.gov.uk/capital-gains-tax/rates
 * Accessed: 2026-05-16
 *
 * Source: HMRC Dividend Tax rates 2024-25
 * URL: https://www.gov.uk/tax-on-dividends
 * Accessed: 2026-05-16
 *
 * All calculation is client-side. No personal data is stored or transmitted.
 */

// ---------------------------------------------------------------------------
// HMRC 2024-25 Income Tax Thresholds and Rates
// ---------------------------------------------------------------------------

/** Personal Allowance — tax-free threshold for most earners */
export const PERSONAL_ALLOWANCE = 12_570;

/**
 * Income threshold above which the Personal Allowance starts to taper.
 * £1 of PA is lost for every £2 of income above this threshold.
 * PA reaches £0 at £125,140.
 */
export const PA_TAPER_THRESHOLD = 100_000;

/** Income Tax bands for 2024-25 (applied after Personal Allowance) */
export const INCOME_TAX_BANDS = [
  { name: "Basic Rate", from: 12_571, to: 50_270, rate: 0.20 },
  { name: "Higher Rate", from: 50_271, to: 125_140, rate: 0.40 },
  { name: "Additional Rate", from: 125_141, to: Infinity, rate: 0.45 },
] as const;

// ---------------------------------------------------------------------------
// HMRC 2024-25 Employee Class 1 NIC Thresholds and Rates
// ---------------------------------------------------------------------------

/** NIC Primary Threshold (Employee Class 1) — below this, no NICs */
export const NIC_PRIMARY_THRESHOLD = 12_570;

/** NIC Upper Earnings Limit — above this, reduced 2% rate applies */
export const NIC_UPPER_LIMIT = 50_270;

/** Main NIC rate between Primary Threshold and Upper Earnings Limit */
export const NIC_MAIN_RATE = 0.08;

/** Reduced NIC rate above Upper Earnings Limit */
export const NIC_HIGHER_RATE = 0.02;

// ---------------------------------------------------------------------------
// Capital Gains Tax (CGT) 2024-25
// ---------------------------------------------------------------------------

/** CGT annual exempt amount (2024-25) */
export const CGT_ANNUAL_EXEMPT = 3_000;

/** CGT basic rate for shares/securities (post-Autumn Budget 2024, from 30 Oct 2024) */
export const CGT_BASIC_RATE = 0.18;

/** CGT higher rate for shares/securities (post-Autumn Budget 2024, from 30 Oct 2024) */
export const CGT_HIGHER_RATE = 0.24;

/**
 * Assumed proportion of billionaire wealth realised as capital gains
 * in any given year. This is an estimate for illustrative comparison.
 * Most billionaire wealth grows via unrealised gains (taxed at 0%).
 *
 * Assumption: 20% of total wealth gains are realised annually.
 * Reality varies widely — some billionaires realise far less.
 */
export const ASSUMED_REALISATION_RATE = 0.20;

// ---------------------------------------------------------------------------
// Return types
// ---------------------------------------------------------------------------

export interface EmployeeTaxResult {
  /** Gross annual salary in GBP */
  salary: number;
  /** Income Tax payable */
  incomeTax: number;
  /** Employee National Insurance Contributions */
  nics: number;
  /** Total tax (Income Tax + NICs) */
  totalTax: number;
  /** Effective tax rate as a decimal (0–1) */
  effectiveRate: number;
  /** Net take-home pay */
  netPay: number;
  /** Breakdown of tax by band */
  bands: TaxBandBreakdown[];
}

export interface TaxBandBreakdown {
  name: string;
  taxableAmount: number;
  rate: number;
  tax: number;
}

export interface BillionaireTaxResult {
  /** Total wealth gains for the period */
  totalGains: number;
  /** CGT paid on realised gains */
  cgtPaid: number;
  /** Effective rate on realised gains only */
  realisedRate: number;
  /** Value of unrealised gains (taxed at 0%) */
  unrealisedGains: number;
  /** Realised gains amount */
  realisedGains: number;
  /** Effective rate across ALL gains (realised + unrealised) */
  effectiveRate: number;
  /** Proportion of gains assumed realised */
  realisationRate: number;
}

// ---------------------------------------------------------------------------
// Calculations
// ---------------------------------------------------------------------------

/**
 * Calculates the effective Personal Allowance for a given salary,
 * accounting for the £100k taper (£1 lost per £2 above £100,000).
 *
 * Source: HMRC Income Tax rates and allowances 2024-25
 * URL: https://www.gov.uk/income-tax-rates
 * Accessed: 2026-05-16
 */
function getEffectivePersonalAllowance(salary: number): number {
  if (salary <= PA_TAPER_THRESHOLD) {
    return PERSONAL_ALLOWANCE;
  }
  const reduction = Math.floor((salary - PA_TAPER_THRESHOLD) / 2);
  return Math.max(0, PERSONAL_ALLOWANCE - reduction);
}

/**
 * Calculates Income Tax, NICs, effective rate, and net pay for
 * an employee with a given annual salary (2024-25 tax year).
 *
 * Assumptions:
 * - Single employment income, no other income sources
 * - Standard Personal Allowance (no blind person's or marriage allowance)
 * - Employee Class 1 NICs only (not self-employed)
 * - No salary sacrifice, pension contributions, or other deductions
 * - Scottish or Welsh rates are NOT applied (uses rUK rates)
 *
 * @param salary - Gross annual salary in GBP
 * @returns Breakdown of tax, NICs, effective rate, and net pay
 */
export function calculateEmployeeTax(salary: number): EmployeeTaxResult {
  if (salary <= 0) {
    return {
      salary,
      incomeTax: 0,
      nics: 0,
      totalTax: 0,
      effectiveRate: 0,
      netPay: Math.max(0, salary),
      bands: [],
    };
  }

  // Income Tax calculation
  const effectivePA = getEffectivePersonalAllowance(salary);
  const taxableIncome = Math.max(0, salary - effectivePA);
  let incomeTax = 0;
  const bands: TaxBandBreakdown[] = [];

  // Tax-free band
  if (effectivePA > 0) {
    bands.push({
      name: "Personal Allowance",
      taxableAmount: Math.min(salary, effectivePA),
      rate: 0,
      tax: 0,
    });
  }

  // Apply each Income Tax band using absolute income thresholds.
  // The basic rate band bottom is effectivePA (not the fixed 12,570)
  // so the PA taper correctly expands the basic rate zone.
  for (let i = 0; i < INCOME_TAX_BANDS.length; i++) {
    const band = INCOME_TAX_BANDS[i];
    const bandBottom = i === 0 ? effectivePA : band.from - 1;
    const bandTop = band.to === Infinity ? salary : band.to;

    const taxableInBand = Math.max(
      0,
      Math.min(salary, bandTop) - bandBottom,
    );

    if (taxableInBand > 0) {
      const taxForBand = taxableInBand * band.rate;
      incomeTax += taxForBand;
      bands.push({
        name: band.name,
        taxableAmount: taxableInBand,
        rate: band.rate,
        tax: taxForBand,
      });
    }
  }

  // National Insurance calculation (Employee Class 1)
  let nics = 0;
  if (salary > NIC_PRIMARY_THRESHOLD) {
    const mainBand = Math.min(salary, NIC_UPPER_LIMIT) - NIC_PRIMARY_THRESHOLD;
    nics += Math.max(0, mainBand) * NIC_MAIN_RATE;

    if (salary > NIC_UPPER_LIMIT) {
      nics += (salary - NIC_UPPER_LIMIT) * NIC_HIGHER_RATE;
    }
  }

  // Round to the penny
  incomeTax = Math.round(incomeTax * 100) / 100;
  nics = Math.round(nics * 100) / 100;

  const totalTax = incomeTax + nics;
  const effectiveRate = salary > 0 ? totalTax / salary : 0;
  const netPay = salary - totalTax;

  return {
    salary,
    incomeTax,
    nics,
    totalTax,
    effectiveRate,
    netPay,
    bands,
  };
}

/**
 * Calculates the effective tax rate for a billionaire whose wealth
 * grows primarily through capital gains, most of which are unrealised.
 *
 * This is an illustrative model, not an exact calculation for any
 * individual. The key insight is that unrealised gains — the majority
 * of billionaire wealth growth — are taxed at 0% until sold.
 *
 * Assumptions:
 * - Gains are in shares/securities (not property — uses 18%/24% CGT rates post-Autumn Budget 2024)
 * - Billionaire is a higher/additional rate taxpayer (20% CGT rate applies)
 * - Only the assumed realisation percentage of gains is subject to CGT
 * - Annual exempt amount is negligible at this scale but still applied
 * - No Entrepreneurs' Relief / Business Asset Disposal Relief
 * - No dividend income modelled (gains only)
 *
 * @param totalGains - Total wealth gains for the period in GBP
 * @param realisationRate - Proportion of gains realised (default 0.20)
 * @returns Breakdown of CGT, effective rate across all gains
 */
export function calculateBillionaireTax(
  totalGains: number,
  realisationRate: number = ASSUMED_REALISATION_RATE,
): BillionaireTaxResult {
  if (totalGains <= 0) {
    return {
      totalGains,
      cgtPaid: 0,
      realisedRate: 0,
      unrealisedGains: 0,
      realisedGains: 0,
      effectiveRate: 0,
      realisationRate,
    };
  }

  const realisedGains = totalGains * realisationRate;
  const unrealisedGains = totalGains - realisedGains;

  // CGT on realised gains (higher rate — billionaire is always higher/additional)
  const taxableGains = Math.max(0, realisedGains - CGT_ANNUAL_EXEMPT);
  const cgtPaid = Math.round(taxableGains * CGT_HIGHER_RATE * 100) / 100;

  // Effective rate on realised gains only
  const realisedRate = realisedGains > 0 ? cgtPaid / realisedGains : 0;

  // Effective rate across ALL gains (the key comparison)
  const effectiveRate = totalGains > 0 ? cgtPaid / totalGains : 0;

  return {
    totalGains,
    cgtPaid,
    realisedRate,
    unrealisedGains,
    realisedGains,
    effectiveRate,
    realisationRate,
  };
}

/**
 * Formats a decimal rate as a percentage string with one decimal place.
 *
 * @param value - Decimal rate (e.g., 0.2345 for 23.45%)
 * @returns Formatted percentage string (e.g., "23.5%")
 */
export function formatPercentage(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

/**
 * Formats a number as a GBP currency string.
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

/** Source citation metadata for display */
export const TAX_SOURCE = {
  name: "HMRC Income Tax rates and allowances 2024-25",
  url: "https://www.gov.uk/income-tax-rates",
  nicUrl: "https://www.gov.uk/national-insurance-rates-letters",
  cgtUrl: "https://www.gov.uk/capital-gains-tax/rates",
  accessed: "2026-05-16",
} as const;
