export interface ChartMeta {
  readonly name: string;
  readonly title: string;
  readonly description: string;
}

const CHARTS = {
  "wealth-shares": {
    name: "wealth-shares",
    title: "Wealth Shares — Top 1% and Top 10%",
    description:
      "Top 1% and 10% share of UK net personal wealth since 1820 (WID)",
  },
  "housing-affordability": {
    name: "housing-affordability",
    title: "Housing Affordability — Price-to-Earnings Ratios by Region",
    description:
      "House price to earnings ratio by region, 1997-2025 (ONS)",
  },
  "cgt-concentration": {
    name: "cgt-concentration",
    title: "Capital Gains Tax — Concentration by Size of Gain",
    description: "Capital gains concentration by size of gain (HMRC)",
  },
  "wealth-by-decile": {
    name: "wealth-by-decile",
    title: "Total Household Wealth by Decile",
    description:
      "Total net wealth by decile group in Great Britain (ONS WAS)",
  },
  "productivity-pay": {
    name: "productivity-pay",
    title: "Productivity and Pay",
    description:
      "UK productivity and real pay indexed over time (ONS Labour Productivity and AWE)",
  },
  "gdhi-by-region": {
    name: "gdhi-by-region",
    title: "Regional Disposable Income",
    description:
      "Gross disposable household income by UK region (ONS regional accounts)",
  },
  "tax-composition": {
    name: "tax-composition",
    title: "Tax Composition",
    description:
      "UK tax revenue composition by source (HMRC and OBR)",
  },
  "boe-rates": {
    name: "boe-rates",
    title: "Bank of England Rates",
    description:
      "Bank Rate history and monetary policy changes (Bank of England)",
  },
  "child-poverty": {
    name: "child-poverty",
    title: "Child Poverty",
    description:
      "Children in relative poverty after housing costs (DWP households below average income)",
  },
  "generational-wealth": {
    name: "generational-wealth",
    title: "Generational Wealth",
    description:
      "Wealth distribution across generations in Great Britain (ONS WAS)",
  },
} as const satisfies Record<string, ChartMeta>;

export type ChartName = keyof typeof CHARTS;

export const CHART_METADATA: typeof CHARTS = CHARTS;

export const SUPPORTED_CHART_NAMES: ReadonlySet<string> = new Set<ChartName>(
  Object.keys(CHARTS) as ChartName[],
);

export function isValidChart(name: string): name is ChartName {
  return SUPPORTED_CHART_NAMES.has(name);
}
