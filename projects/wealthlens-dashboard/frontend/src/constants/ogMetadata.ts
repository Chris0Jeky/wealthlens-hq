/**
 * OG image metadata for each chart page.
 *
 * Maps chart slugs (matching VALID_CHART_NAMES) to title and subtitle
 * used when generating Open Graph preview images at build time.
 *
 * Subtitles should be source-backed headline statistics.
 * Update these when underlying data refreshes.
 */

import { VALID_CHART_NAMES } from "./charts"

export interface OgMetadataEntry {
  /** Headline displayed on the OG image (serif, large) */
  title: string
  /** Supporting statistic or description (smaller text) */
  subtitle: string
  /** Data source attribution */
  source: string
  /** Date the source data was last accessed (YYYY-MM-DD) */
  sourceAccessDate: string
}

export const OG_METADATA: Record<string, OgMetadataEntry> = {
  "wealth-shares": {
    title: "Who Owns the UK?",
    subtitle: "The top 10% hold 57% of all household wealth",
    source: "World Inequality Database (WID)",
    sourceAccessDate: "2026-05-14",
  },
  "housing-affordability": {
    title: "The Housing Crisis in Numbers",
    subtitle: "House prices are 8.3x average earnings — up from 3.5x in 1997",
    source: "ONS Housing Affordability Dataset",
    sourceAccessDate: "2026-05-14",
  },
  "wealth-by-decile": {
    title: "Wealth by Decile",
    subtitle: "The bottom 50% of households hold just 9% of total wealth",
    source: "ONS Wealth and Assets Survey",
    sourceAccessDate: "2026-05-14",
  },
  "cgt-concentration": {
    title: "Who Pays Capital Gains Tax?",
    subtitle: "78% of CGT is paid by just 5,000 individuals each year",
    source: "HMRC Capital Gains Tax Statistics",
    sourceAccessDate: "2026-05-14",
  },
  "wage-stagnation": {
    title: "Real Wage Stagnation",
    subtitle: "Median real weekly earnings remain below their 2008 peak",
    source: "ONS Annual Survey of Hours and Earnings",
    sourceAccessDate: "2026-05-16",
  },
  "productivity-pay": {
    title: "The Productivity-Pay Gap",
    subtitle: "UK productivity has outpaced real pay growth since the late 1990s",
    source: "ONS Labour Productivity and AWE",
    sourceAccessDate: "2026-05-16",
  },
  "gdhi-by-region": {
    title: "Regional Disposable Income",
    subtitle: "Disposable income varies sharply across UK regions",
    source: "ONS Regional Gross Disposable Household Income",
    sourceAccessDate: "2026-05-16",
  },
  "tax-composition": {
    title: "What Britain Taxes",
    subtitle: "A breakdown of UK tax receipts by revenue source",
    source: "HMRC Tax and NIC Receipts",
    sourceAccessDate: "2026-05-16",
  },
  "boe-rates": {
    title: "Bank Rate and Inflation",
    subtitle: "Bank of England rates alongside CPI inflation history",
    source: "Bank of England Interactive Database",
    sourceAccessDate: "2026-05-16",
  },
  "child-poverty": {
    title: "Child Poverty by Region",
    subtitle: "Children in relative poverty after housing costs",
    source: "DWP/HMRC Children in Low Income Families",
    sourceAccessDate: "2026-05-16",
  },
  "generational-wealth": {
    title: "The Generational Wealth Gap",
    subtitle: "Median household wealth differs sharply by generation",
    source: "Resolution Foundation and ONS WAS",
    sourceAccessDate: "2026-05-16",
  },
  "inheritance-tax": {
    title: "Who Pays Inheritance Tax?",
    subtitle: "Only 4.6% of UK estates were liable for inheritance tax in 2021-22",
    source: "HMRC Inheritance Tax Statistics",
    sourceAccessDate: "2026-05-16",
  },
}

/**
 * Validate that every chart in VALID_CHART_NAMES has OG metadata.
 * This is checked at test time to prevent missing images.
 */
export function getChartsMissingOgMetadata(): string[] {
  const missing: string[] = []
  for (const chartName of VALID_CHART_NAMES) {
    if (!(chartName in OG_METADATA)) {
      missing.push(chartName)
    }
  }
  return missing
}
