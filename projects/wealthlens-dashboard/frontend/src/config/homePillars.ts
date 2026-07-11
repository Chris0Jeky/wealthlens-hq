/**
 * Front-page pillar navigation — the editorial grouping of all 12 charts.
 *
 * Chart TITLES are derived from chartArticles.ts at render time (no copy
 * here to drift); only the pillar membership is editorial and lives here.
 * A guard test asserts these slugs equal VALID_CHART_NAMES exactly, so a
 * new chart cannot ship without a home for it on the front page.
 */
export interface Pillar {
  /** Pillar heading shown on the front page. */
  label: string
  /** Chart slugs (VALID_CHART_NAMES members) in display order. */
  charts: readonly string[]
}

export const HOME_PILLARS: readonly Pillar[] = [
  {
    label: "Wealth",
    charts: ["wealth-shares", "wealth-by-decile", "generational-wealth"],
  },
  {
    label: "Housing",
    charts: ["housing-affordability", "boe-rates"],
  },
  {
    label: "Tax",
    charts: ["tax-composition", "cgt-concentration", "inheritance-tax"],
  },
  {
    label: "Income & work",
    charts: ["productivity-pay", "wage-stagnation", "gdhi-by-region", "child-poverty"],
  },
]
