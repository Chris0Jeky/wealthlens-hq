/**
 * Chart article page configurations.
 *
 * Each entry defines the full broadsheet-style article layout for a
 * chart page: breadcrumb, headline, lede, metadata, stats, toolbar
 * settings, article body, methodology, and related charts.
 *
 * Extracted from ChartView.vue for maintainability and testability.
 */
import type { StatItem } from "@/components/StatStrip.vue";
import type { SeriesLegendItem } from "@/components/ChartToolbar.vue";
import type { RelatedChartItem } from "@/components/RelatedCharts.vue";
import { COLOR_TOP_10, COLOR_TOP_1 } from "@/config/chartColors";

/**
 * Full article configuration for a chart page. Charts without a full
 * config entry fall back to a simpler layout with just title + chart.
 */
export interface ChartConfig {
  /** Breadcrumb trail segments (last is the current page, not a link). */
  breadcrumb: { label: string; to?: string }[];
  /** Tag pills shown above the headline. */
  pills: { text: string; accent?: boolean }[];
  /** Headline text. Supports one <em> for italic red emphasis. */
  headline: string;
  /** Italicised emphasis portion of headline (rendered in red). */
  headlineEmphasis?: string;
  /** Lede paragraph (HTML allowed for <strong> tags). */
  lede: string;
  /** Metadata card key-value pairs. */
  meta: { label: string; value: string; href?: string }[];
  /** Headline stats for the stat strip. */
  stats: StatItem[];
  /** Chart toolbar configuration. */
  toolbar: {
    title: string;
    unit: string;
    series: SeriesLegendItem[];
    ranges: string[];
    defaultRange: string;
  };
  /** Source bar content. */
  source: {
    name: string;
    url: string;
    licence: string;
    accessed: string;
    chartId: string;
  };
  /** Article body sections. */
  article: {
    sections: {
      heading: string;
      headingEmphasis?: string;
      paragraphs: string[];
    }[];
    pullQuote?: {
      text: string;
    };
  };
  /** Methodology accordion content (HTML allowed). */
  methodology: string;
  /** Related charts for the bottom grid. */
  related: RelatedChartItem[];
}

/** Simple fallback config for charts without full article content. */
export const simpleChartTitles: Record<string, string> = {
  "housing-affordability":
    "Housing Affordability — Price-to-Earnings Ratios by Region",
  "cgt-concentration":
    "Capital Gains Tax — Concentration by Size of Gain",
  "wealth-by-decile": "Total Household Wealth by Decile",
  "wage-stagnation":
    "Real Wage Stagnation — UK Median Earnings Since 2008",
  "inheritance-tax": "Inheritance Tax — How Few Estates Actually Pay",
};

/**
 * Full chart configurations. Wealth-shares is the primary example,
 * matching the broadsheet design reference exactly.
 */
export const chartConfigs: Record<string, ChartConfig> = {
  "wealth-shares": {
    breadcrumb: [
      { label: "Home", to: "/" },
      { label: "The data", to: "/" },
      /* Future pillar routes: link to pillar index when it exists */
      { label: "Wealth", to: "#" },
      { label: "Who owns wealth in the UK?" },
    ],
    pills: [
      { text: "Wealth", accent: true },
      { text: "Historical · 1820–2024" },
      { text: "United Kingdom" },
      /* Display date: human-readable format is intentional for UI pills */
      { text: "Updated 14 May 2026" },
    ],
    headline: "Who owns wealth in the UK?",
    headlineEmphasis: "Same lot, mostly.",
    lede: 'For at least two centuries, the top 10% have held over <strong>half of all UK personal wealth</strong>. The post-war squeeze was real, but partial: concentration bottomed out near 52% around 1990. The slide back has been steady since, and the top 10% now hold over <strong>57%</strong> again, roughly back to early-1980s levels.',
    meta: [
      { label: "Source", value: "WID.world", href: "https://wid.world" },
      { label: "Series", value: "UK · Net personal wealth" },
      { label: "Coverage", value: "1820 — 2024" },
      /* Display date: human-readable format is intentional for the meta card */
      { label: "Updated", value: "14 May 2026" },
      { label: "Licence", value: "CC-BY 4.0" },
      /* 250 = the two plotted WID series (p90p100 + p99p100) × 125 years each
         in wealth-shares.json; guarded by the stat-card data-integrity test. */
      { label: "Data points", value: "250" },
      { label: "Chart ID", value: "WL-W-001" },
    ],
    /*
     * All four cards are grounded in the WID p90p100 / p99p100 series this page
     * actually plots (public/data/wealth-shares.json, values ×100). Verified
     * 2026-06-19: top 10% 2024 = 57.1%, top 1% 2024 = 21.3%, bottom 90% 2024 =
     * 42.9% (= 100 − 57.1), all-time low = 51.6% in 1990. The previous "28%"
     * top-1% and "1980 = 50%" cards were not supported by this series.
     */
    stats: [
      {
        label: "The headline",
        value: "57",
        unit: "%",
        description:
          "Share of UK personal wealth owned by the top 10% in 2024",
        headline: true,
      },
      {
        label: "Top 1% alone",
        value: "21",
        unit: "%",
        description: "The wealthiest 1% own over a fifth of all personal wealth",
      },
      {
        label: "Bottom 90%",
        value: "43",
        unit: "%",
        description:
          "Nine in ten people share less than the top 10% holds alone",
      },
      {
        label: "Postwar low (1990)",
        value: "52",
        unit: "%",
        description:
          "The least concentrated UK wealth has ever been, and still over half",
      },
    ],
    toolbar: {
      title: "Share of net personal wealth",
      unit: "%",
      series: [
        // Mirror the two lines WealthSharesChart.vue actually draws: it plots
        // only the WID p90p100 (top 10%) and p99p100 (top 1%) series, in the
        // shared COLOR_TOP_10 / COLOR_TOP_1 (imported from the same source of
        // truth as the chart, so they cannot drift apart). The stat cards also
        // cite the bottom 90% (a derived complement, 100 − top 10%), but that
        // is not a plotted line, so it must not appear as a legend dot.
        { label: "Top 10%", color: COLOR_TOP_10, bold: true },
        { label: "Top 1%", color: COLOR_TOP_1 },
      ],
      ranges: ["200y", "100y", "50y", "25y"],
      defaultRange: "200y",
    },
    source: {
      name: "World Inequality Database (wid.world)",
      url: "https://wid.world",
      licence: "CC-BY 4.0",
      accessed: "2026-05-14",
      chartId: "WL-W-001",
    },
    article: {
      sections: [
        {
          heading: "What this chart shows",
          paragraphs: [
            'The share of <em>net personal wealth</em> held by the top 10% and the top 1% in the United Kingdom, from 1820 to 2024. Net personal wealth is the sum of all financial assets (savings, investments, pensions) and non-financial assets (mainly housing) — minus debts.',
          ],
        },
        {
          heading: "",
          paragraphs: [
            'The shape tells a story in three acts. From 1820 to 1914, the UK was the most unequal large economy in the world by some measures — a tiny aristocratic and capitalist class held more than 90% of all personal wealth. Two world wars, progressive taxation, and the postwar welfare settlement compressed this dramatically: the top 10% share fell from 58% in 1980 to an all-time low of around 52% by 1990. Since then the curve has bent the other way.',
          ],
        },
        {
          heading: "Why it",
          headingEmphasis: "matters",
          paragraphs: [
            'Wealth, not income, is the dominant determinant of life outcomes in the UK in 2026. It funds deposits on first homes, university choices, business creation, and old-age security. When wealth is concentrated, opportunity is too — and the rate of inter-generational mobility falls. The "left-behind town" isn\'t a metaphor. It\'s a balance sheet.',
          ],
        },
      ],
      pullQuote: {
        text: 'In two hundred years of data, the top 10% have <strong>never</strong> held less than 51% of UK personal wealth. The post-war compression was real — but partial. Since the early 1990s, the trend has been steady re-concentration.',
      },
    },
    methodology: `
      <p>The data are drawn from the World Inequality Database (WID.world), which harmonises a range of national wealth estimates to produce comparable cross-country series. For the UK, WID combines:</p>
      <ul>
        <li>HMRC estate-multiplier estimates (1809 onward)</li>
        <li>ONS Wealth and Assets Survey microdata (2006 onward)</li>
        <li>National accounts household balance sheets</li>
        <li>Forbes/Sunday Times Rich List rich-list calibration at the very top</li>
      </ul>
      <p>The series uses <em>net personal wealth</em> — financial &amp; non-financial assets minus debts, on an individual basis (not household). Pension wealth is included where defined-contribution; defined-benefit entitlements are excluded in this series.</p>
      <table>
        <thead><tr><th>Year span</th><th>Primary method</th><th>Confidence</th></tr></thead>
        <tbody>
          <tr><td>1820 – 1900</td><td>Estate multiplier</td><td>Moderate</td></tr>
          <tr><td>1900 – 1960</td><td>Estate multiplier + tax tabulations</td><td>High</td></tr>
          <tr><td>1960 – 2006</td><td>Tax tabulations + survey</td><td>High</td></tr>
          <tr><td>2006 – 2024</td><td>WAS microdata + admin</td><td>Very high</td></tr>
        </tbody>
      </table>
      <p><strong>Known caveats:</strong> wealth at the very top is historically under-counted; offshore holdings are largely invisible to estate records; pension reform changes mean pre-2006 and post-2006 series are not strictly comparable for the bottom 50%.</p>
    `,
    related: [
      {
        domain: "Wealth · UK",
        title: "Composition of household wealth, 1995–2023",
        finding:
          'Housing is now <b>36%</b> of all household wealth — up from 22% in 1995.',
        to: "/charts/wealth-by-decile",
        sparkType: "line",
      },
      {
        domain: "Tax · UK",
        title: "Capital gains concentration by decile",
        finding:
          '<b>92%</b> of taxable gains accrue to the top 1% of recipients.',
        to: "/charts/cgt-concentration",
        sparkType: "bar",
      },
      {
        domain: "Housing · UK",
        title: "House price to earnings ratio, 1997–2025",
        finding:
          'England & Wales ratio peaked at <b>9.0×</b> in 2021 (7.6× in 2025).',
        to: "/charts/housing-affordability",
        sparkType: "line",
      },
    ],
  },

  /* ================================================================ */
  /* PRODUCTIVITY-PAY GAP                                              */
  /* ================================================================ */
  "productivity-pay": {
    breadcrumb: [
      { label: "Home", to: "/" },
      { label: "The data", to: "/" },
      { label: "Work & Pay", to: "#" },
      { label: "Workers produce more than ever — their pay hasn't kept up" },
    ],
    pills: [
      { text: "Work & Pay", accent: true },
      { text: "Historical · 1970–2023" },
      { text: "United Kingdom" },
      { text: "Updated 16 May 2026" },
    ],
    headline: "Workers produce more than ever —",
    headlineEmphasis: "their pay hasn't kept up.",
    lede: 'Since 1997, UK output per hour has risen by roughly <strong>32%</strong> while real pay has grown by only around <strong>11%</strong>. The gap widened sharply after the 2008 financial crisis and never closed.',
    meta: [
      { label: "Source", value: "ONS Labour Productivity / AWE", href: "https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/labourproductivity" },
      { label: "Series", value: "UK · Output per hour (LZVD) & real AWE" },
      { label: "Coverage", value: "1970 — 2023" },
      { label: "Updated", value: "16 May 2026" },
      { label: "Licence", value: "OGL v3.0" },
      { label: "Base year", value: "1997 = 100" },
      { label: "Chart ID", value: "WL-P-001" },
    ],
    stats: [
      {
        label: "Productivity (2023)",
        value: "132",
        unit: "",
        description:
          "Output-per-hour index in 2023 (base 1997 = 100)",
        headline: true,
      },
      {
        label: "Real pay (2023)",
        value: "111",
        unit: "",
        description: "Real pay index — barely moved since 2008",
      },
      {
        label: "Gap opened since 1997",
        value: "~19",
        unit: "pp",
        description:
          "Productivity gained 32 index points; pay gained only 11",
      },
      {
        label: "Lost decade",
        value: "2008–18",
        unit: "",
        description:
          "Real pay was lower in 2018 than in 2008 — unprecedented in modern UK history",
      },
    ],
    toolbar: {
      title: "Productivity vs real pay (index, 1997 = 100)",
      unit: "",
      series: [
        { label: "Productivity", color: "#1a56db", bold: true },
        { label: "Real Pay", color: "var(--wl-red)" },
      ],
      ranges: ["50y", "25y", "10y"],
      defaultRange: "50y",
    },
    source: {
      name: "ONS Labour Productivity (LZVD) & ONS AWE (KAB9) deflated by CPIH",
      url: "https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/labourproductivity/timeseries/lzvd/prdy",
      licence: "OGL v3.0",
      accessed: "2026-05-16",
      chartId: "WL-P-001",
    },
    article: {
      sections: [
        {
          heading: "What this chart shows",
          paragraphs: [
            'Two indices, both set to 100 in 1997: <em>output per hour worked</em> (a standard productivity measure) and <em>average weekly earnings deflated by CPIH</em> (a measure of real pay). When the lines diverge, workers are producing more value but receiving a smaller share of it as wages.',
          ],
        },
        {
          heading: "",
          paragraphs: [
            'From 1970 to the late 1990s, productivity and pay roughly tracked each other. After 2000, productivity continued to climb while real pay growth slowed. The 2008 financial crisis broke the link entirely: productivity stagnated (the UK\'s "productivity puzzle") while real pay <em>fell</em>, and did not recover its 2008 level until around 2020.',
          ],
        },
        {
          heading: "Why it",
          headingEmphasis: "matters",
          paragraphs: [
            'If pay had kept pace with productivity since 1997, the average UK worker would earn significantly more today. The gap represents value created by labour that flows instead to profits, rents, and capital income. It is a structural driver of wealth inequality — and it hits hardest in regions and sectors where workers have the least bargaining power.',
          ],
        },
      ],
      pullQuote: {
        text: 'Since 1997, UK productivity rose by roughly <strong>32%</strong> while real pay rose by only <strong>11%</strong>. Workers are producing more than ever — they just aren\'t being paid for it.',
      },
    },
    methodology: `
      <p>The productivity series uses ONS output per hour worked for the whole economy (series LZVD), seasonally adjusted, rebased to 1997 = 100.</p>
      <p>The pay series uses ONS Average Weekly Earnings total pay (series KAB9), deflated to real terms using the CPIH all-items index (series L55O), then rebased to 1997 = 100.</p>
      <ul>
        <li>Both series are annual averages.</li>
        <li>The gap percentage is calculated as: (productivity_index - pay_index) / pay_index × 100.</li>
        <li>When live ONS API data is unavailable, the pipeline uses illustrative values derived from published ONS bulletins.</li>
      </ul>
      <p><strong>Known caveats:</strong> AWE covers employees only (not self-employed); CPIH vs CPI choice affects the deflator; composition effects (changing mix of part-time/full-time, sectors) can shift AWE independently of individual pay growth.</p>
    `,
    related: [
      {
        domain: "Income · UK",
        title: "Gross Disposable Household Income by region",
        finding:
          'London GDHI per head is <b>4×</b> higher than the lowest areas.',
        to: "/charts/gdhi-by-region",
        sparkType: "bar",
      },
      {
        domain: "Tax · UK",
        title: "UK tax revenue — work vs wealth",
        finding:
          '<b>93%</b> of selected tax revenue comes from taxes on work.',
        to: "/charts/tax-composition",
        sparkType: "bar",
      },
      {
        domain: "Wealth · UK",
        title: "Who owns wealth in the UK?",
        finding:
          'Top 10% hold <b>57%</b> of all personal wealth.',
        to: "/charts/wealth-shares",
        sparkType: "line",
      },
    ],
  },

  /* ================================================================ */
  /* GDHI BY REGION                                                    */
  /* ================================================================ */
  "gdhi-by-region": {
    breadcrumb: [
      { label: "Home", to: "/" },
      { label: "The data", to: "/" },
      { label: "Income", to: "#" },
      { label: "The income map of Britain reveals two countries" },
    ],
    pills: [
      { text: "Income", accent: true },
      { text: "Regional · 2023" },
      { text: "United Kingdom" },
      { text: "Updated 16 May 2026" },
    ],
    headline: "The income map of Britain",
    headlineEmphasis: "reveals two countries.",
    lede: 'Gross disposable household income per head in Kensington & Chelsea is over <strong>£79,000</strong> — more than five times the £14,200 in Blackpool. The UK average of £24,800 masks enormous geographic inequality.',
    meta: [
      { label: "Source", value: "ONS Regional GDHI", href: "https://www.ons.gov.uk/economy/regionalaccounts/grossdisposablehouseholdincome" },
      { label: "Series", value: "UK · GDHI per head, all ITL regions" },
      { label: "Coverage", value: "2023 (latest year)" },
      { label: "Updated", value: "16 May 2026" },
      { label: "Licence", value: "OGL v3.0" },
      { label: "Regions", value: "25" },
      { label: "Chart ID", value: "WL-I-001" },
    ],
    stats: [
      {
        label: "Highest (Kensington & Chelsea)",
        value: "79,500",
        unit: "£",
        description:
          "GDHI per head — more than 5× the lowest area",
        headline: true,
      },
      {
        label: "UK average",
        value: "24,800",
        unit: "£",
        description: "National GDHI per head in 2023",
      },
      {
        label: "Lowest (Blackpool)",
        value: "14,200",
        unit: "£",
        description:
          "The lowest GDHI per head in England",
      },
      {
        label: "Ratio (top / bottom)",
        value: "5.6",
        unit: "×",
        description:
          "The income gap between the richest and poorest areas",
      },
    ],
    toolbar: {
      title: "GDHI per head by region (£, 2023)",
      unit: "£",
      series: [
        { label: "Above UK average", color: "#1a56db", bold: true },
        { label: "Below UK average", color: "#6b7280" },
      ],
      ranges: ["All"],
      defaultRange: "All",
    },
    source: {
      name: "ONS Regional Gross Disposable Household Income",
      url: "https://www.ons.gov.uk/economy/regionalaccounts/grossdisposablehouseholdincome/datasets/regionalgrossdisposablehouseholdincomegdhi",
      licence: "OGL v3.0",
      accessed: "2026-05-16",
      chartId: "WL-I-001",
    },
    article: {
      sections: [
        {
          heading: "What this chart shows",
          paragraphs: [
            'Gross Disposable Household Income (GDHI) per head for regions across the UK. GDHI is the amount of money households have available for spending or saving <em>after</em> taxes, benefits, and pension contributions. It is the closest single measure to "what people actually have to live on" at a regional level.',
          ],
        },
        {
          heading: "",
          paragraphs: [
            'The chart reveals a clear geographic gradient: inner London boroughs dominate the top, with values far above the UK average of roughly £24,800. At the other end, post-industrial areas in the North, Wales, and the Midlands cluster well below the national figure. The gap between the highest and lowest areas is more than fivefold — one of the widest in any developed economy.',
          ],
        },
        {
          heading: "Why it",
          headingEmphasis: "matters",
          paragraphs: [
            'Regional income inequality drives unequal access to housing, services, education, and opportunity. It is not just a North-South divide — pockets of low income exist within otherwise affluent regions. Policy interventions (levelling up, devolution, investment zones) are measured against exactly this kind of data.',
          ],
        },
      ],
      pullQuote: {
        text: 'A household in Kensington & Chelsea has over <strong>five times</strong> the disposable income per head of a household in Blackpool. The UK average of £24,800 is a statistical fiction that hides two very different countries.',
      },
    },
    methodology: `
      <p>GDHI is calculated by ONS as: total income (wages, self-employment, property, benefits) minus taxes (income tax, NICs, council tax) minus pension contributions. The per-head figure divides by resident population.</p>
      <ul>
        <li>Data is at ITL3 level (local authority groupings) for maximum geographic detail.</li>
        <li>Values are at current prices (not inflation-adjusted).</li>
        <li>The UK average row is included for reference but filtered from the regional chart to avoid distortion.</li>
        <li>When live ONS XLSX data is unavailable, the pipeline uses illustrative values from published ONS bulletins.</li>
      </ul>
      <p><strong>Known caveats:</strong> GDHI per head divides by <em>all</em> residents including children and retired people — it is not a measure of individual earnings. Areas with high commuter outflows (e.g. dormitory towns) may show lower GDHI because earnings are attributed to workplace regions in some components.</p>
    `,
    related: [
      {
        domain: "Work & Pay · UK",
        title: "Productivity vs pay — the growing divergence",
        finding:
          'Pay has lagged <b>~19 points</b> behind productivity since 1997.',
        to: "/charts/productivity-pay",
        sparkType: "line",
      },
      {
        domain: "Poverty · UK",
        title: "Child poverty by UK region",
        finding:
          'Up to <b>38%</b> of children in the North East live in poverty.',
        to: "/charts/child-poverty",
        sparkType: "bar",
      },
      {
        domain: "Housing · UK",
        title: "House price to earnings ratio by region",
        finding:
          'England & Wales ratio peaked at <b>9.0×</b> in 2021 (7.6× in 2025).',
        to: "/charts/housing-affordability",
        sparkType: "line",
      },
    ],
  },

  /* ================================================================ */
  /* TAX COMPOSITION                                                   */
  /* ================================================================ */
  "tax-composition": {
    breadcrumb: [
      { label: "Home", to: "/" },
      { label: "The data", to: "/" },
      { label: "Tax", to: "#" },
      { label: "Britain taxes work, not wealth" },
    ],
    pills: [
      { text: "Tax", accent: true },
      { text: "Annual · 2018–2024" },
      { text: "United Kingdom" },
      { text: "Updated 16 May 2026" },
    ],
    headline: "Britain taxes work,",
    headlineEmphasis: "not wealth.",
    lede: 'Income tax and National Insurance contribute around <strong>93%</strong> of selected tax revenue. Capital gains tax, inheritance tax, and stamp duty together account for just <strong>7%</strong> — despite wealth being far more concentrated than income.',
    meta: [
      { label: "Source", value: "HMRC Tax Receipts", href: "https://www.gov.uk/government/statistics/hmrc-tax-and-nics-receipts-for-the-uk" },
      { label: "Series", value: "UK · Income Tax, NICs, CGT, IHT, SDLT" },
      { label: "Coverage", value: "2018-19 — 2023-24" },
      { label: "Updated", value: "16 May 2026" },
      { label: "Licence", value: "OGL v3.0" },
      { label: "Data points", value: "30" },
      { label: "Chart ID", value: "WL-T-001" },
    ],
    stats: [
      {
        label: "Work taxes (2023-24)",
        value: "93",
        unit: "%",
        description:
          "Income tax (£270bn) + NICs (£180bn) share of selected revenue",
        headline: true,
      },
      {
        label: "Wealth taxes (2023-24)",
        value: "7",
        unit: "%",
        description: "CGT + IHT + SDLT = roughly £34.5bn combined",
      },
      {
        label: "Income Tax alone",
        value: "270",
        unit: "£bn",
        description:
          "The single largest tax, paid overwhelmingly on earned income",
      },
      {
        label: "CGT receipts",
        value: "15",
        unit: "£bn",
        description:
          "Despite £billions in capital gains, the tax raises relatively little",
      },
    ],
    toolbar: {
      title: "UK tax revenue composition (£ billion)",
      unit: "£bn",
      series: [
        { label: "Income Tax", color: "#1a56db", bold: true },
        { label: "NICs", color: "#047857" },
        { label: "CGT", color: "var(--wl-red)" },
        { label: "IHT", color: "#7c3aed" },
        { label: "SDLT", color: "#b45309" },
      ],
      ranges: ["All"],
      defaultRange: "All",
    },
    source: {
      name: "HMRC Tax and NIC Receipts for the UK",
      url: "https://www.gov.uk/government/statistics/hmrc-tax-and-nics-receipts-for-the-uk",
      licence: "OGL v3.0",
      accessed: "2026-05-16",
      chartId: "WL-T-001",
    },
    article: {
      sections: [
        {
          heading: "What this chart shows",
          paragraphs: [
            'A stacked bar chart of five major UK taxes: <em>Income Tax</em> and <em>National Insurance Contributions</em> (taxes on work/earned income) versus <em>Capital Gains Tax</em>, <em>Inheritance Tax</em>, and <em>Stamp Duty Land Tax</em> (taxes on wealth and capital). The visual contrast between the two groups is immediate and stark.',
          ],
        },
        {
          heading: "",
          paragraphs: [
            'The UK raises roughly £450 billion per year from income tax and NICs alone — taxes that fall almost entirely on workers and their employers. By contrast, the three main wealth taxes together raise only around £34–35 billion. This is not because wealth is small — UK household wealth exceeds £15 trillion — but because wealth is taxed lightly, with numerous reliefs, exemptions, and lower rates.',
          ],
        },
        {
          heading: "Why it",
          headingEmphasis: "matters",
          paragraphs: [
            'A tax system that falls heavily on work and lightly on wealth has consequences: it redistributes from younger, working-age populations to older, asset-rich generations. It makes it harder to accumulate wealth through labour alone. And it means the fiscal system does little to reduce the concentration of wealth documented elsewhere on this site.',
          ],
        },
      ],
      pullQuote: {
        text: 'The UK raises <strong>13×</strong> more from taxes on work than from taxes on wealth. The top 10% own 57% of all personal wealth — yet wealth taxes contribute just 7% of revenue.',
      },
    },
    methodology: `
      <p>Data is drawn from HMRC's published "Tax and NIC Receipts" tables, which give annual outturn figures for each tax head.</p>
      <ul>
        <li><strong>Income Tax:</strong> PAYE + Self-Assessment, the largest single revenue stream.</li>
        <li><strong>NICs:</strong> Employee + employer contributions, paid on earnings.</li>
        <li><strong>CGT:</strong> Tax on gains when assets are sold above the annual exempt amount.</li>
        <li><strong>IHT:</strong> Tax on estates above the nil-rate band at death.</li>
        <li><strong>SDLT:</strong> Stamp Duty Land Tax on property purchases.</li>
      </ul>
      <p>The "work_pct" and "wealth_pct" columns show each group's share of the five-tax total (not all UK tax revenue — council tax, VAT, corporation tax etc. are excluded for clarity).</p>
      <p><strong>Known caveats:</strong> This is a simplified framing. NICs partially fund state pension (a form of deferred wealth). Council tax is arguably a wealth tax. VAT falls on consumption. The 93/7 split refers only to the five taxes shown here.</p>
    `,
    related: [
      {
        domain: "Tax · UK",
        title: "Capital gains concentration by decile",
        finding:
          '<b>92%</b> of taxable gains accrue to the top 1% of recipients.',
        to: "/charts/cgt-concentration",
        sparkType: "bar",
      },
      {
        domain: "Wealth · UK",
        title: "Who owns wealth in the UK?",
        finding:
          'Top 10% hold <b>57%</b> of all personal wealth.',
        to: "/charts/wealth-shares",
        sparkType: "line",
      },
      {
        domain: "Generations · UK",
        title: "Median wealth by generation at key ages",
        finding:
          'Millennials hold <b>60%</b> less wealth at 30 than boomers did.',
        to: "/charts/generational-wealth",
        sparkType: "bar",
      },
    ],
  },

  /* ================================================================ */
  /* BANK OF ENGLAND RATES                                             */
  /* ================================================================ */
  "boe-rates": {
    breadcrumb: [
      { label: "Home", to: "/" },
      { label: "The data", to: "/" },
      { label: "Economy", to: "#" },
      { label: "The cost of borrowing: interest rate history" },
    ],
    pills: [
      { text: "Economy", accent: true },
      { text: "Monthly · 2000–present" },
      { text: "United Kingdom" },
      { text: "Updated 16 May 2026" },
    ],
    headline: "The cost of borrowing:",
    headlineEmphasis: "30 years of interest rate history.",
    lede: 'From <strong>6% in 2000</strong> to a historic low of <strong>0.1% in 2020–21</strong>, then the fastest rise in decades to <strong>5.25% by late 2023</strong>. The Bank Rate shapes mortgages, savings, and the real value of money.',
    meta: [
      { label: "Source", value: "Bank of England IADB", href: "https://www.bankofengland.co.uk/boeapps/database/" },
      { label: "Series", value: "IUDBEDR (Bank Rate) + D7BT (CPI)" },
      { label: "Coverage", value: "2000 — present" },
      { label: "Updated", value: "16 May 2026" },
      { label: "Licence", value: "OGL v3.0" },
      { label: "Frequency", value: "Monthly" },
      { label: "Chart ID", value: "WL-E-001" },
    ],
    stats: [
      {
        label: "Peak rate (2023)",
        value: "5.25",
        unit: "%",
        description:
          "Highest Bank Rate since 2008, reached August 2023",
        headline: true,
      },
      {
        label: "Historic low",
        value: "0.1",
        unit: "%",
        description: "Emergency rate held from March 2020 to December 2021",
      },
      {
        label: "Peak CPI (2022)",
        value: "11.1",
        unit: "%",
        description:
          "Highest CPI inflation in 41 years, October 2022",
      },
      {
        label: "Rate rises (2021–23)",
        value: "14",
        unit: "",
        description:
          "Consecutive rate increases — the fastest tightening cycle since the 1980s",
      },
    ],
    toolbar: {
      title: "Bank Rate vs CPI inflation (%)",
      unit: "%",
      series: [
        { label: "Bank Rate", color: "#1a56db", bold: true },
        { label: "CPI Inflation", color: "var(--wl-red)" },
      ],
      ranges: ["All", "10y", "5y"],
      defaultRange: "All",
    },
    source: {
      name: "Bank of England Interactive Analytical Database",
      url: "https://www.bankofengland.co.uk/boeapps/database/",
      licence: "OGL v3.0",
      accessed: "2026-05-16",
      chartId: "WL-E-001",
    },
    article: {
      sections: [
        {
          heading: "What this chart shows",
          paragraphs: [
            'Two monthly series: the <em>Bank of England official Bank Rate</em> (the interest rate the BoE charges to commercial banks, which directly influences mortgage and savings rates) and the <em>CPI annual inflation rate</em> (the 12-month percentage change in consumer prices). Together they show how monetary policy responds to — and sometimes lags behind — price pressures.',
          ],
        },
        {
          heading: "",
          paragraphs: [
            'The story has three distinct chapters. From 2000 to 2008, rates were relatively stable at 4–5%, keeping inflation near the 2% target. The 2008 crisis triggered emergency cuts to 0.5%, then 0.25%, and finally 0.1% in 2020. When inflation surged past 10% in 2022 — driven by energy prices and post-COVID supply shocks — the Bank raised rates 14 consecutive times in under two years, the fastest tightening cycle since the early 1990s.',
          ],
        },
        {
          heading: "Why it",
          headingEmphasis: "matters",
          paragraphs: [
            'Interest rates are the mechanism through which monetary policy reaches households. A 5.25% rate means a typical £200,000 mortgage costs roughly £500/month more than at 0.1%. Savers benefit, but homeowners and renters (via landlord costs) bear the burden. The interaction between rates and inflation also determines real wage growth — when CPI outstrips pay rises, workers get poorer even in a "growing" economy.',
          ],
        },
      ],
      pullQuote: {
        text: 'From <strong>0.1%</strong> to <strong>5.25%</strong> in under two years — the fastest rate-rise cycle in decades. For a typical mortgage holder, that means hundreds of pounds more per month.',
      },
    },
    methodology: `
      <p>Bank Rate data uses the BoE series IUDBEDR (Official Bank Rate, monthly, not seasonally adjusted). CPI uses series D7BT (CPI annual rate, 12-month % change) accessed via the BoE Interactive Analytical Database (IADB).</p>
      <ul>
        <li>Bank Rate is a step function — it changes only on MPC decision dates.</li>
        <li>CPI is the headline consumer price index (not CPIH which includes owner-occupier housing costs).</li>
        <li>Date range starts from January 2000 to capture the full modern inflation-targeting era.</li>
      </ul>
      <p><strong>Known caveats:</strong> CPI does not include mortgage interest payments (unlike the old RPI). The Bank Rate is not the same as the rate borrowers pay — commercial rates include a margin. Real interest rates (Bank Rate minus CPI) were deeply negative in 2021–22, effectively eroding the value of savings.</p>
    `,
    related: [
      {
        domain: "Housing · UK",
        title: "House price to earnings ratio, 1997–2025",
        finding:
          'England & Wales ratio peaked at <b>9.0×</b> in 2021 (7.6× in 2025).',
        to: "/charts/housing-affordability",
        sparkType: "line",
      },
      {
        domain: "Work & Pay · UK",
        title: "Productivity vs pay — the growing divergence",
        finding:
          'Real pay was lower in 2018 than in 2008.',
        to: "/charts/productivity-pay",
        sparkType: "line",
      },
      {
        domain: "Income · UK",
        title: "Gross Disposable Household Income by region",
        finding:
          'GDHI per head ranges from <b>£14k</b> to <b>£79k</b>.',
        to: "/charts/gdhi-by-region",
        sparkType: "bar",
      },
    ],
  },

  /* ================================================================ */
  /* CHILD POVERTY                                                     */
  /* ================================================================ */
  "child-poverty": {
    breadcrumb: [
      { label: "Home", to: "/" },
      { label: "The data", to: "/" },
      { label: "Poverty", to: "#" },
      { label: "One in three children in parts of Britain grows up in poverty" },
    ],
    pills: [
      { text: "Poverty", accent: true },
      { text: "Regional · 2022-23" },
      { text: "United Kingdom" },
      { text: "Updated 16 May 2026" },
    ],
    headline: "One in three children in parts of Britain",
    headlineEmphasis: "grows up in poverty.",
    lede: 'After housing costs, <strong>38%</strong> of children in the North East live in relative poverty — the highest regional rate in the UK. Even the lowest region (South East) has a rate of <strong>22%</strong>. Nationally, over 3.3 million children are affected.',
    meta: [
      { label: "Source", value: "DWP/HMRC Statistics", href: "https://www.gov.uk/government/statistics/children-in-low-income-families-local-area-statistics-2014-to-2023" },
      { label: "Series", value: "Children in Low Income Families" },
      { label: "Coverage", value: "2022-23 (12 regions)" },
      { label: "Updated", value: "16 May 2026" },
      { label: "Licence", value: "OGL v3.0" },
      { label: "Measure", value: "After housing costs" },
      { label: "Chart ID", value: "WL-PV-001" },
    ],
    stats: [
      {
        label: "Highest (North East)",
        value: "38",
        unit: "%",
        description:
          "More than one in three children in relative poverty after housing costs",
        headline: true,
      },
      {
        label: "London",
        value: "36",
        unit: "%",
        description: "Around 700,000 children in poverty in the capital",
      },
      {
        label: "Lowest (South East)",
        value: "22",
        unit: "%",
        description:
          "Even the 'best' region has more than one in five children in poverty",
      },
      {
        label: "Children affected (UK)",
        value: "3.3",
        unit: "m+",
        description:
          "Total children in relative poverty across all regions",
      },
    ],
    toolbar: {
      title: "Child poverty rate by UK region (%)",
      unit: "%",
      series: [
        { label: "Above UK average", color: "#b91c1c", bold: true },
        { label: "Below UK average", color: "#1a56db" },
      ],
      ranges: ["All"],
      defaultRange: "All",
    },
    source: {
      name: "DWP/HMRC Children in Low Income Families (local area statistics, 2014–2023)",
      url: "https://www.gov.uk/government/statistics/children-in-low-income-families-local-area-statistics-2014-to-2023",
      licence: "OGL v3.0",
      accessed: "2026-05-16",
      chartId: "WL-PV-001",
    },
    article: {
      sections: [
        {
          heading: "What this chart shows",
          paragraphs: [
            'The percentage of children living in relative low income <em>after housing costs</em> (AHC) by UK region. Relative low income means a household income below 60% of the median. After-housing-costs is the more policy-relevant measure because housing costs vary enormously by region and consume a large share of low-income families\' budgets.',
          ],
        },
        {
          heading: "",
          paragraphs: [
            'The North East has the highest rate at 38%, closely followed by London (36%) and the West Midlands (35%). London\'s high rate may seem paradoxical given high average incomes — but extreme housing costs push many families below the poverty line after rent is paid. The South East and East of England have the lowest rates, but even these exceed 20%. No region in the UK has a child poverty rate below one in five.',
          ],
        },
        {
          heading: "Why it",
          headingEmphasis: "matters",
          paragraphs: [
            'Child poverty is the single strongest predictor of poor outcomes in education, health, and lifetime earnings. It is also the most tractable form of inequality — targeted benefit increases (e.g. child benefit, universal credit child elements) have historically reduced child poverty rates rapidly. The regional variation shows that poverty is not evenly distributed: it clusters in areas already affected by deindustrialisation, low GDHI, and poor housing.',
          ],
        },
      ],
      pullQuote: {
        text: 'No region in the UK has a child poverty rate below <strong>one in five</strong>. In the North East, it is closer to <strong>two in five</strong>. These are not edge cases — they are millions of children.',
      },
    },
    methodology: `
      <p>Data is from the DWP/HMRC "Children in Low Income Families" local area statistics, which combine HMRC administrative data on family incomes with DWP benefit records.</p>
      <ul>
        <li><strong>Measure:</strong> Relative low income after housing costs (below 60% of national median equivalised household income, AHC).</li>
        <li><strong>Unit:</strong> Percentage of dependent children in each region.</li>
        <li><strong>Year:</strong> 2022-23 financial year (the most recent available).</li>
        <li>"Children in poverty" counts are rounded to nearest thousand.</li>
      </ul>
      <p><strong>Known caveats:</strong> The measure is "relative" — if median income falls, the poverty line falls too, potentially reducing measured poverty even if living standards worsen. Regional averages mask significant local variation (e.g. within London, rates range from under 20% in Richmond to over 50% in Tower Hamlets). Self-employed income is modelled, not directly measured.</p>
    `,
    related: [
      {
        domain: "Income · UK",
        title: "Gross Disposable Household Income by region",
        finding:
          'GDHI per head in Blackpool is just <b>£14,200</b>.',
        to: "/charts/gdhi-by-region",
        sparkType: "bar",
      },
      {
        domain: "Wealth · UK",
        title: "Total household wealth by decile",
        finding:
          'The bottom decile holds just <b>£13.9bn</b> — 0.1% of the total.',
        to: "/charts/wealth-by-decile",
        sparkType: "bar",
      },
      {
        domain: "Generations · UK",
        title: "Median wealth by generation at key ages",
        finding:
          'Millennials hold <b>60%</b> less wealth at 30 than boomers did.',
        to: "/charts/generational-wealth",
        sparkType: "bar",
      },
    ],
  },

  /* ================================================================ */
  /* GENERATIONAL WEALTH                                               */
  /* ================================================================ */
  "generational-wealth": {
    breadcrumb: [
      { label: "Home", to: "/" },
      { label: "The data", to: "/" },
      { label: "Generations", to: "#" },
      { label: "The wealth ladder is pulling up behind younger generations" },
    ],
    pills: [
      { text: "Generations", accent: true },
      { text: "Age-comparison · 1994–2026" },
      { text: "Great Britain" },
      { text: "Updated 16 May 2026" },
    ],
    headline: "The wealth ladder is pulling up",
    headlineEmphasis: "behind younger generations.",
    lede: 'At age 30, Baby Boomers had median household wealth of <strong>£68,000</strong> (in 2022 real terms). Millennials at the same age: just <strong>£27,000</strong> — a 60% shortfall. The gap widens at every subsequent age milestone.',
    meta: [
      { label: "Source", value: "Resolution Foundation / ONS WAS", href: "https://www.resolutionfoundation.org/publications/" },
      { label: "Series", value: "Median household wealth by generation" },
      { label: "Coverage", value: "1994 — 2026 (measured & projected)" },
      { label: "Updated", value: "16 May 2026" },
      { label: "Licence", value: "CC BY-NC-ND 4.0" },
      { label: "Generations", value: "3 (Boomers, Gen X, Millennials)" },
      { label: "Chart ID", value: "WL-G-001" },
    ],
    stats: [
      {
        label: "Boomers at 30",
        value: "68k",
        unit: "£",
        description:
          "Median total household wealth at age 30, 2022 real terms",
        headline: true,
      },
      {
        label: "Millennials at 30",
        value: "27k",
        unit: "£",
        description: "60% less than Boomers at the same age",
      },
      {
        label: "Boomers at 60",
        value: "395k",
        unit: "£",
        description:
          "Approaching retirement with nearly £400k median wealth",
      },
      {
        label: "Gen X at 40",
        value: "116k",
        unit: "£",
        description:
          "27% less than Boomers had at 40 (£159k)",
      },
    ],
    toolbar: {
      title: "Median household wealth at equivalent ages (£, 2022 prices)",
      unit: "£",
      series: [
        { label: "Baby Boomers", color: "#1a56db", bold: true },
        { label: "Generation X", color: "#047857" },
        { label: "Millennials", color: "var(--wl-red)" },
      ],
      ranges: ["All"],
      defaultRange: "All",
    },
    source: {
      name: "Resolution Foundation / ONS Wealth and Assets Survey",
      url: "https://www.resolutionfoundation.org/publications/",
      licence: "CC BY-NC-ND 4.0",
      accessed: "2026-05-16",
      chartId: "WL-G-001",
    },
    article: {
      sections: [
        {
          heading: "What this chart shows",
          paragraphs: [
            'Median total household wealth at equivalent age milestones (30, 40, 50, 60) for three generations: Baby Boomers (born 1946–64), Generation X (born 1965–80), and Millennials (born 1981–96). All values are adjusted to 2022 real terms so that generational comparisons are like-for-like. Faded bars indicate projected or estimated values where that generation has not yet reached the milestone.',
          ],
        },
        {
          heading: "",
          paragraphs: [
            'The pattern is consistent: each younger generation arrives at each age milestone with significantly less wealth than the generation before. At age 30, the decline from Boomers to Millennials is 60%. At age 40, Gen X had 27% less than Boomers. This is not simply a "they\'ll catch up" story — the gap reflects structural differences in housing costs, pension access, wage growth, and student debt that compound over a lifetime.',
          ],
        },
        {
          heading: "Why it",
          headingEmphasis: "matters",
          paragraphs: [
            'Wealth at key life stages determines access to home ownership, financial security, and retirement adequacy. If Millennials and Gen Z cannot accumulate wealth at the same rate as their parents did, the UK faces a future where prosperity depends almost entirely on inheritance rather than work. This makes inter-generational mobility impossible without structural policy change — and makes the distribution of inherited wealth a defining political question of the coming decades.',
          ],
        },
      ],
      pullQuote: {
        text: 'At age 30, Boomers had <strong>£68,000</strong>. Millennials at 30 had <strong>£27,000</strong>. That\'s not a lifestyle choice — it\'s a structural shift in who gets to build wealth and when.',
      },
    },
    methodology: `
      <p>Wealth figures are compiled from the Resolution Foundation's "Intergenerational Audit for the UK" (2024) and the ONS Wealth and Assets Survey (WAS), waves 1–8 (2006–2024).</p>
      <ul>
        <li><strong>Measure:</strong> Median total household wealth (financial + physical + property + private pension, net of debts).</li>
        <li><strong>Age milestones:</strong> 30, 40, 50, 60 — chosen to enable like-for-like generational comparison.</li>
        <li><strong>Adjustment:</strong> All values in 2022 real terms (deflated by CPI/CPIH to remove inflation effects).</li>
        <li><strong>Projected values:</strong> Where a generation has not yet reached a milestone (e.g. Millennials at 40), values are projected from current wealth trajectories and are clearly marked.</li>
      </ul>
      <p><strong>Known caveats:</strong> "Household" wealth divides differently for different living arrangements (single vs. couple). Pension wealth is included but valued differently across defined-benefit (Boomers) and defined-contribution (younger) schemes. The WAS sample begins in 2006, so Boomer wealth at age 30 (circa 1994) is estimated from other sources. Inheritance received is included in current wealth but not separately tracked.</p>
    `,
    related: [
      {
        domain: "Wealth · UK",
        title: "Who owns wealth in the UK?",
        finding:
          'Top 10% hold <b>57%</b> of all personal wealth.',
        to: "/charts/wealth-shares",
        sparkType: "line",
      },
      {
        domain: "Housing · UK",
        title: "House price to earnings ratio, 1997–2025",
        finding:
          'England & Wales ratio peaked at <b>9.0×</b> in 2021 (7.6× in 2025).',
        to: "/charts/housing-affordability",
        sparkType: "line",
      },
      {
        domain: "Tax · UK",
        title: "UK tax revenue — work vs wealth",
        finding:
          '<b>93%</b> of selected tax revenue comes from taxes on work.',
        to: "/charts/tax-composition",
        sparkType: "bar",
      },
    ],
  },
};
