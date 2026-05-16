/**
 * OG image metadata for each chart page.
 *
 * Maps chart slugs (matching VALID_CHART_NAMES) to title and subtitle
 * used when generating Open Graph preview images at build time.
 *
 * Subtitles should be source-backed headline statistics.
 * Update these when underlying data refreshes.
 */

import { VALID_CHART_NAMES } from "./charts";

export interface OgMetadataEntry {
  /** Headline displayed on the OG image (serif, large) */
  title: string;
  /** Supporting statistic or description (smaller text) */
  subtitle: string;
  /** Data source attribution */
  source: string;
  /** Date the source data was last accessed (YYYY-MM-DD) */
  sourceAccessDate: string;
}

export const OG_METADATA: Record<string, OgMetadataEntry> = {
  "wealth-shares": {
    title: "Who Owns the UK?",
    subtitle: "The top 10% hold 57% of all household wealth",
    source: "World Inequality Database (WID)",
    sourceAccessDate: "2025-05-14",
  },
  "housing-affordability": {
    title: "The Housing Crisis in Numbers",
    subtitle:
      "House prices are 8.3x average earnings — up from 3.5x in 1997",
    source: "ONS Housing Affordability Dataset",
    sourceAccessDate: "2025-05-14",
  },
  "wealth-by-decile": {
    title: "Wealth by Decile",
    subtitle:
      "The bottom 50% of households hold just 9% of total wealth",
    source: "ONS Wealth and Assets Survey",
    sourceAccessDate: "2025-05-14",
  },
  "cgt-concentration": {
    title: "Who Pays Capital Gains Tax?",
    subtitle:
      "78% of CGT is paid by just 5,000 individuals each year",
    source: "HMRC Capital Gains Tax Statistics",
    sourceAccessDate: "2025-05-14",
  },
};

/**
 * Validate that every chart in VALID_CHART_NAMES has OG metadata.
 * This is checked at test time to prevent missing images.
 */
export function getChartsMissingOgMetadata(): string[] {
  const missing: string[] = [];
  for (const chartName of VALID_CHART_NAMES) {
    if (!(chartName in OG_METADATA)) {
      missing.push(chartName);
    }
  }
  return missing;
}
