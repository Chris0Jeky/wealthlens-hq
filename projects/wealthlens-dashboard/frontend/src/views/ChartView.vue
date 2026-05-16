<script setup lang="ts">
/**
 * ChartView — Broadsheet-style chart article page.
 *
 * Renders a full article layout around a chart: breadcrumb, headline,
 * lede paragraph, tag pills, metadata card, stat strip, chart with toolbar
 * and source bar, share bar, article body with pull quotes, methodology
 * accordion, and related charts grid.
 *
 * Uses the route param :name to select chart-specific content from a
 * config map. Currently hardcodes wealth-shares data as the primary
 * example matching the broadsheet design reference. Other datasets
 * fall back to a simpler layout.
 */
import { computed, defineAsyncComponent, ref, watch } from "vue";
import { useRoute } from "vue-router";
import StatStrip from "@/components/StatStrip.vue";
import type { StatItem } from "@/components/StatStrip.vue";
import ChartToolbar from "@/components/ChartToolbar.vue";
import type { SeriesLegendItem } from "@/components/ChartToolbar.vue";
import ShareBar from "@/components/ShareBar.vue";
import RelatedCharts from "@/components/RelatedCharts.vue";
import type { RelatedChartItem } from "@/components/RelatedCharts.vue";
import { useAnalytics } from "@/composables/useAnalytics";

/** Lazy-load chart components to avoid bundling ECharts on every route. */
const WealthSharesChart = defineAsyncComponent(
  () => import("@/components/WealthSharesChart.vue"),
);
const HousingAffordabilityChart = defineAsyncComponent(
  () => import("@/components/HousingAffordabilityChart.vue"),
);
const CgtConcentrationChart = defineAsyncComponent(
  () => import("@/components/CgtConcentrationChart.vue"),
);
const WealthByDecileChart = defineAsyncComponent(
  () => import("@/components/WealthByDecileChart.vue"),
);

const route = useRoute();
const { trackEvent } = useAnalytics();
const chartName = computed(() => route.params.name as string);

/* ------------------------------------------------------------------ */
/* Chart content configuration                                         */
/* ------------------------------------------------------------------ */

/**
 * Full article configuration for a chart page. Charts without a full
 * config entry fall back to a simpler layout with just title + chart.
 */
interface ChartConfig {
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
const simpleChartTitles: Record<string, string> = {
  "housing-affordability":
    "Housing Affordability — Price-to-Earnings Ratios by Region",
  "cgt-concentration":
    "Capital Gains Tax — Concentration by Size of Gain",
  "wealth-by-decile": "Total Household Wealth by Decile",
};

/**
 * Full chart configurations. Wealth-shares is the primary example,
 * matching the broadsheet design reference exactly.
 */
const chartConfigs: Record<string, ChartConfig> = {
  "wealth-shares": {
    breadcrumb: [
      { label: "Home", to: "/" },
      { label: "The data", to: "/" },
      { label: "Wealth", to: "/" },
      { label: "Who owns wealth in the UK?" },
    ],
    pills: [
      { text: "Wealth", accent: true },
      { text: "Historical · 1820–2023" },
      { text: "United Kingdom" },
      { text: "Updated 14 May 2026" },
    ],
    headline: "Who owns wealth in the UK?",
    headlineEmphasis: "Same lot, mostly.",
    lede: 'For at least two centuries, the top 10% have held over <strong>half of all UK personal wealth</strong>. The post-war squeeze was real, but partial. The slide back has been steady since 1980. We’re now at 1910 levels — without the empire to explain it.',
    meta: [
      { label: "Source", value: "WID.world", href: "https://wid.world" },
      { label: "Series", value: "UK · Net personal wealth" },
      { label: "Coverage", value: "1820 — 2023" },
      { label: "Updated", value: "14 May 2026" },
      { label: "Licence", value: "CC-BY 4.0" },
      { label: "Data points", value: "22" },
      { label: "Chart ID", value: "WL-W-001" },
    ],
    stats: [
      {
        label: "The headline",
        value: "57",
        unit: "%",
        description:
          "Share of UK personal wealth owned by the top 10% in 2023",
        headline: true,
      },
      {
        label: "Top 1% alone",
        value: "28",
        unit: "%",
        description: "More than the bottom 70% combined",
      },
      {
        label: "Bottom 50%",
        value: "6",
        unit: "%",
        description:
          "Half the country splits one-sixteenth of the wealth",
      },
      {
        label: "Postwar low (1980)",
        value: "50",
        unit: "%",
        description:
          "The least concentrated it’s ever been — and still half",
      },
    ],
    toolbar: {
      title: "Share of net personal wealth",
      unit: "%",
      series: [
        { label: "Top 10%", color: "var(--wl-red)", bold: true },
        { label: "Top 1%", color: "var(--wl-ink)" },
        { label: "Middle 40%", color: "var(--wl-ink-faint)" },
        { label: "Bottom 50%", color: "var(--wl-ink-faint)" },
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
            'The share of <em>net personal wealth</em> held by four percentile groups in the United Kingdom, from 1820 to 2023. Net personal wealth is the sum of all financial assets (savings, investments, pensions) and non-financial assets (mainly housing) — minus debts.',
          ],
        },
        {
          heading: "",
          paragraphs: [
            'The shape tells a story in three acts. From 1820 to 1914, the UK was the most unequal large economy in the world by some measures — a tiny aristocratic and capitalist class held almost 90% of all personal wealth. Two world wars, progressive taxation, and the postwar welfare settlement compressed this dramatically: by 1980, the bottom 50% held 8% of wealth, and the top 10% had fallen to 50%. Since then the curve has bent the other way.',
          ],
        },
        {
          heading: "Why it",
          headingEmphasis: "matters",
          paragraphs: [
            'Wealth, not income, is the dominant determinant of life outcomes in the UK in 2026. It funds deposits on first homes, university choices, business creation, and old-age security. When wealth is concentrated, opportunity is too — and the rate of inter-generational mobility falls. The “left-behind town” isn’t a metaphor. It’s a balance sheet.',
          ],
        },
      ],
      pullQuote: {
        text: 'In two hundred years of data, the top 10% have <strong>never</strong> held less than 49% of UK personal wealth. The post-war compression was real — but partial. Since 1980, the trend has been steady re-concentration.',
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
          <tr><td>2006 – 2023</td><td>WAS microdata + admin</td><td>Very high</td></tr>
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
        title: "House price to earnings ratio, 1969–2024",
        finding:
          'UK ratio is <b>8.6×</b> — the highest since records began.',
        to: "/charts/housing-affordability",
        sparkType: "line",
      },
    ],
  },
};

/** Whether the current chart has a full article config. */
const hasFullConfig = computed(
  () => chartName.value in chartConfigs,
);

/** The full config for the current chart, if available. */
const config = computed(() => chartConfigs[chartName.value]);

/** Whether this chart name is supported at all (full or simple). */
const isSupported = computed(
  () =>
    chartName.value in chartConfigs ||
    chartName.value in simpleChartTitles,
);

/** Active range for toolbar (local UI state). */
const activeRange = ref("200y");

function onRangeChange(range: string) {
  activeRange.value = range;
}

/** Track chart views when the chart name changes. */
watch(chartName, (name) => {
  if (name && isSupported.value) {
    trackEvent("view_chart", { chart: name });
  }
}, { immediate: true });
</script>

<template>
  <!-- ===== FULL ARTICLE LAYOUT (broadsheet design) ===== -->
  <template v-if="hasFullConfig && config">
    <!-- Breadcrumb -->
    <nav class="crumb" aria-label="Breadcrumb">
      <ol class="crumb__list">
        <li
          v-for="(seg, i) in config.breadcrumb"
          :key="i"
          class="crumb__item"
        >
          <router-link
            v-if="seg.to && i < config.breadcrumb.length - 1"
            :to="seg.to"
            class="crumb__link"
          >
            {{ seg.label }}
          </router-link>
          <span v-else class="crumb__current" aria-current="page">
            {{ seg.label }}
          </span>
          <span
            v-if="i < config.breadcrumb.length - 1"
            class="crumb__sep"
            aria-hidden="true"
          >/</span>
        </li>
      </ol>
    </nav>

    <!-- Article header -->
    <header class="article-head">
      <div>
        <div class="article-head__tags">
          <span
            v-for="(pill, i) in config.pills"
            :key="i"
            :class="['pill', { 'pill--accent': pill.accent }]"
          >
            {{ pill.text }}
          </span>
        </div>
        <h1 class="article-head__title">
          {{ config.headline }}
          <em v-if="config.headlineEmphasis">
            {{ config.headlineEmphasis }}
          </em>
        </h1>
        <p class="article-head__lede" v-html="config.lede"></p>
      </div>
      <aside class="meta-card" aria-label="Chart metadata">
        <h2 class="meta-card__heading">Chart facts</h2>
        <dl class="meta-card__list">
          <template v-for="(m, i) in config.meta" :key="i">
            <dt>{{ m.label }}</dt>
            <dd>
              <a
                v-if="m.href"
                :href="m.href"
                target="_blank"
                rel="noopener"
                class="meta-card__link"
              >
                {{ m.value }}
              </a>
              <span
                v-else
                :class="{ 'wl-num': m.label === 'Data points' || m.label === 'Chart ID' }"
              >
                {{ m.value }}
              </span>
            </dd>
          </template>
        </dl>
      </aside>
    </header>

    <!-- Stat strip -->
    <StatStrip :stats="config.stats" />

    <!-- Chart card -->
    <div class="chart-wrap">
      <div class="chart-card">
        <ChartToolbar
          :title="config.toolbar.title"
          :unit="config.toolbar.unit"
          :series="config.toolbar.series"
          :ranges="config.toolbar.ranges"
          :active-range="activeRange"
          @range-change="onRangeChange"
        />
        <div class="chart-stage">
          <WealthSharesChart v-if="chartName === 'wealth-shares'" />
        </div>
        <div class="chart-source-bar">
          <div class="chart-source-bar__left">
            <span>
              Source:
              <a
                :href="config.source.url"
                target="_blank"
                rel="noopener"
              >
                {{ config.source.name }}
              </a>
            </span>
            <span aria-hidden="true">&middot;</span>
            <span>{{ config.source.licence }}</span>
            <span aria-hidden="true">&middot;</span>
            <span>Accessed {{ config.source.accessed }}</span>
          </div>
          <span class="wl-num">
            WealthLens UK &middot; {{ config.source.chartId }}
          </span>
        </div>
      </div>

      <!-- Share bar -->
      <ShareBar :chart-id="config.source.chartId" />
    </div>

    <!-- Article body -->
    <article class="article-body">
      <!-- First section -->
      <template
        v-for="(section, i) in config.article.sections"
        :key="i"
      >
        <h2 v-if="section.heading" class="article-body__heading">
          {{ section.heading }}
          <em v-if="section.headingEmphasis">
            {{ section.headingEmphasis }}
          </em>
        </h2>

        <!-- Insert pull quote after first section -->
        <div
          v-if="i === 0 && config.article.pullQuote"
          class="article-body__pull"
        >
          <p class="article-body__pull-label">&uarr; The takeaway</p>
          <p v-html="config.article.pullQuote.text"></p>
        </div>

        <p
          v-for="(para, j) in section.paragraphs"
          :key="`p-${i}-${j}`"
          v-html="para"
        ></p>
      </template>

      <!-- Methodology accordion -->
      <details class="method">
        <summary>Methodology &amp; data quality</summary>
        <div class="method__body" v-html="config.methodology"></div>
      </details>
    </article>

    <!-- Related charts -->
    <RelatedCharts :charts="config.related" />

    <!-- Simple footer for chart pages -->
    <footer class="chart-foot" role="contentinfo">
      <div class="chart-foot__inner">
        <span>
          &copy; 2026 WealthLens UK &middot; MIT licensed &middot;
          chart-id {{ config.source.chartId }}
        </span>
        <span>
          <router-link to="/" class="chart-foot__link">
            Suggest a chart &rarr;
          </router-link>
        </span>
      </div>
    </footer>
  </template>

  <!-- ===== SIMPLE LAYOUT (charts without full article config) ===== -->
  <template v-else-if="isSupported">
    <div class="simple-layout">
      <!-- Back link -->
      <nav class="crumb" aria-label="Breadcrumb">
        <ol class="crumb__list">
          <li class="crumb__item">
            <router-link to="/" class="crumb__link">Home</router-link>
            <span class="crumb__sep" aria-hidden="true">/</span>
          </li>
          <li class="crumb__item">
            <router-link to="/" class="crumb__link">The data</router-link>
            <span class="crumb__sep" aria-hidden="true">/</span>
          </li>
          <li class="crumb__item">
            <span class="crumb__current" aria-current="page">
              {{ simpleChartTitles[chartName] || chartName }}
            </span>
          </li>
        </ol>
      </nav>

      <h1 class="simple-layout__title">
        {{ simpleChartTitles[chartName] || chartName }}
      </h1>

      <div class="chart-wrap">
        <div class="chart-card">
          <div class="chart-stage">
            <HousingAffordabilityChart
              v-if="chartName === 'housing-affordability'"
            />
            <CgtConcentrationChart
              v-if="chartName === 'cgt-concentration'"
            />
            <WealthByDecileChart
              v-if="chartName === 'wealth-by-decile'"
            />
          </div>
        </div>
      </div>
    </div>
  </template>

  <!-- ===== NOT FOUND ===== -->
  <div v-else class="not-found">
    <nav class="crumb" aria-label="Breadcrumb">
      <ol class="crumb__list">
        <li class="crumb__item">
          <router-link to="/" class="crumb__link">Home</router-link>
          <span class="crumb__sep" aria-hidden="true">/</span>
        </li>
        <li class="crumb__item">
          <span class="crumb__current">Chart not found</span>
        </li>
      </ol>
    </nav>
    <div class="not-found__content">
      <h1 class="not-found__title">Chart not found</h1>
      <p class="not-found__text">
        No chart is available for
        "<span class="wl-num">{{ chartName }}</span>".
      </p>
      <router-link to="/" class="wl-btn wl-btn--ghost">
        Return to dashboard
      </router-link>
    </div>
  </div>
</template>

<style scoped>
/* ============================================================ */
/* BREADCRUMB                                                    */
/* ============================================================ */
.crumb {
  max-width: 1320px;
  margin: 0 auto;
  padding: 18px 32px 0;
  font-family: var(--wl-mono);
  font-size: 11px;
  color: var(--wl-ink-muted);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.crumb__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}
.crumb__item {
  display: inline-flex;
  align-items: center;
}
.crumb__link {
  color: var(--wl-ink-muted);
  text-decoration: none;
}
.crumb__link:hover {
  color: var(--wl-red);
}
.crumb__sep {
  margin: 0 8px;
  color: var(--wl-rule-strong);
}
.crumb__current {
  color: var(--wl-ink);
}

/* ============================================================ */
/* ARTICLE HEADER                                                */
/* ============================================================ */
.article-head {
  max-width: 1320px;
  margin: 24px auto 32px;
  padding: 0 32px;
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 56px;
  align-items: end;
  padding-bottom: 28px;
  border-bottom: 2px solid var(--wl-ink);
}

.article-head__tags {
  display: flex;
  gap: 8px;
  margin-bottom: 18px;
  flex-wrap: wrap;
}

.pill {
  font-family: var(--wl-mono);
  font-size: 10px;
  letter-spacing: 0.12em;
  padding: 4px 10px;
  background: var(--wl-bg);
  border: 1px solid var(--wl-rule-strong);
  color: var(--wl-ink-muted);
  text-transform: uppercase;
}
.pill--accent {
  background: var(--wl-red);
  border-color: var(--wl-red);
  color: #fff;
  font-weight: 600;
}

.article-head__title {
  font-family: var(--wl-serif);
  font-size: clamp(48px, 6vw, 84px);
  font-weight: 600;
  line-height: 0.96;
  letter-spacing: -0.025em;
  margin: 0 0 24px;
  color: var(--wl-ink);
  max-width: 14ch;
  text-wrap: balance;
}
.article-head__title em {
  font-style: italic;
  color: var(--wl-red);
  font-weight: 500;
}

.article-head__lede {
  font-size: 20px;
  color: var(--wl-ink-body);
  line-height: 1.5;
  max-width: 50ch;
  margin: 0;
}
.article-head__lede :deep(strong) {
  color: var(--wl-red);
  font-weight: 600;
  background: var(--wl-red-soft);
  padding: 1px 4px;
}

/* Metadata card */
.meta-card {
  background: var(--wl-card);
  border: 1px solid var(--wl-ink);
  padding: 24px;
  font-family: var(--wl-mono);
  font-size: 12px;
}
.meta-card__heading {
  margin: 0 0 16px;
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.16em;
  color: var(--wl-ink-muted);
  text-transform: uppercase;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--wl-rule);
}
.meta-card__list {
  margin: 0;
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 10px 18px;
}
.meta-card__list dt {
  color: var(--wl-ink-muted);
}
.meta-card__list dd {
  margin: 0;
  color: var(--wl-ink);
  font-weight: 500;
}
.meta-card__link {
  color: var(--wl-red);
  text-decoration: none;
  border-bottom: 1px solid var(--wl-red);
}

/* ============================================================ */
/* CHART AREA                                                    */
/* ============================================================ */
.chart-wrap {
  max-width: 1320px;
  margin: 0 auto;
  padding: 0 32px;
}

.chart-card {
  background: var(--wl-card);
  border: 1px solid var(--wl-ink);
  overflow: hidden;
}

.chart-stage {
  padding: 24px 28px 16px;
}

.chart-source-bar {
  padding: 14px 24px;
  border-top: 1px solid var(--wl-rule);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  background: var(--wl-bg-muted);
  font-family: var(--wl-mono);
  font-size: 11px;
  color: var(--wl-ink-muted);
  flex-wrap: wrap;
}
.chart-source-bar__left {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}
.chart-source-bar a {
  color: var(--wl-ink);
  text-decoration: none;
  border-bottom: 1px solid var(--wl-rule-strong);
}
.chart-source-bar a:hover {
  color: var(--wl-red);
  border-color: var(--wl-red);
}

/* ============================================================ */
/* ARTICLE BODY                                                  */
/* ============================================================ */
.article-body {
  max-width: 760px;
  margin: 64px auto 0;
  padding: 0 32px;
}

.article-body__heading {
  font-family: var(--wl-serif);
  font-size: 36px;
  font-weight: 600;
  letter-spacing: -0.018em;
  color: var(--wl-ink);
  margin: 48px 0 18px;
  line-height: 1.1;
}
.article-body__heading em {
  font-style: italic;
  color: var(--wl-red);
  font-weight: 500;
}

.article-body :deep(p) {
  font-size: 18px;
  line-height: 1.7;
  color: var(--wl-ink-body);
  margin: 0 0 18px;
}
.article-body :deep(p strong) {
  color: var(--wl-ink);
  font-weight: 600;
}
.article-body :deep(p em) {
  font-family: var(--wl-serif);
  font-style: italic;
}

/* Pull quote */
.article-body__pull {
  margin: 36px 0;
  padding: 28px 32px;
  border-top: 4px solid var(--wl-red);
  border-bottom: 1px solid var(--wl-rule);
  background: var(--wl-paper-tint);
}
.article-body__pull-label {
  font-family: var(--wl-mono);
  font-size: 10px;
  letter-spacing: 0.16em;
  color: var(--wl-red);
  text-transform: uppercase;
  font-weight: 600;
  margin: 0 0 12px;
}
.article-body__pull :deep(p) {
  font-family: var(--wl-serif);
  font-style: italic;
  font-size: 24px;
  line-height: 1.35;
  color: var(--wl-ink);
  margin: 0;
  letter-spacing: -0.01em;
}
.article-body__pull :deep(p strong) {
  font-style: normal;
  background: var(--wl-red);
  color: #fff;
  padding: 2px 6px;
  font-weight: 600;
}

/* ============================================================ */
/* METHODOLOGY ACCORDION                                         */
/* ============================================================ */
.method {
  background: var(--wl-card);
  border: 1px solid var(--wl-ink);
  padding: 0;
  margin: 32px 0;
}
.method summary {
  list-style: none;
  padding: 20px 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 600;
  font-size: 16px;
  color: var(--wl-ink);
  font-family: var(--wl-sans);
}
.method summary::-webkit-details-marker {
  display: none;
}
.method summary::before {
  content: "+";
  width: 22px;
  height: 22px;
  border: 1px solid var(--wl-ink);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--wl-ink);
  font-family: var(--wl-mono);
  transition: transform 0.2s ease;
  flex-shrink: 0;
}
.method[open] summary::before {
  content: "\2212"; /* minus sign */
}
.method[open] summary {
  border-bottom: 1px solid var(--wl-rule);
  background: var(--wl-paper-tint);
}
.method summary:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: -2px;
}
.method__body {
  padding: 24px;
  font-size: 15px;
  color: var(--wl-ink-body);
  line-height: 1.65;
}
.method__body :deep(p) {
  margin: 0 0 14px;
  font-size: 15px;
}
.method__body :deep(ul) {
  padding-left: 18px;
  margin: 8px 0 12px;
}
.method__body :deep(li) {
  margin-bottom: 6px;
}
.method__body :deep(table) {
  width: 100%;
  font-family: var(--wl-mono);
  font-size: 12px;
  border-collapse: collapse;
  margin-top: 12px;
}
.method__body :deep(th),
.method__body :deep(td) {
  border-bottom: 1px solid var(--wl-rule);
  padding: 10px 12px;
  text-align: left;
}
.method__body :deep(th) {
  color: var(--wl-ink-muted);
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 10px;
}

/* ============================================================ */
/* CHART PAGE FOOTER                                             */
/* ============================================================ */
.chart-foot {
  border-top: 1px solid var(--wl-ink);
  padding: 32px 0;
  background: var(--wl-bg);
  margin-top: 96px;
}
.chart-foot__inner {
  max-width: 1320px;
  margin: 0 auto;
  padding: 0 32px;
  display: flex;
  justify-content: space-between;
  gap: 24px;
  font-family: var(--wl-mono);
  font-size: 11px;
  color: var(--wl-ink-muted);
  flex-wrap: wrap;
  letter-spacing: 0.04em;
}
.chart-foot__link {
  color: var(--wl-red);
  text-decoration: none;
}
.chart-foot__link:hover {
  text-decoration: underline;
}

/* ============================================================ */
/* SIMPLE LAYOUT (for charts without full article config)        */
/* ============================================================ */
.simple-layout {
  max-width: 1320px;
  margin: 0 auto;
  padding: 0 0 96px;
}
.simple-layout__title {
  font-family: var(--wl-serif);
  font-size: clamp(32px, 4vw, 52px);
  font-weight: 600;
  line-height: 1.05;
  letter-spacing: -0.018em;
  color: var(--wl-ink);
  margin: 24px 32px 32px;
}

/* ============================================================ */
/* NOT FOUND                                                     */
/* ============================================================ */
.not-found {
  max-width: 1320px;
  margin: 0 auto;
}
.not-found__content {
  padding: 80px 32px;
  text-align: center;
}
.not-found__title {
  font-family: var(--wl-serif);
  font-size: 48px;
  font-weight: 600;
  color: var(--wl-ink);
  margin: 0 0 16px;
}
.not-found__text {
  font-size: 18px;
  color: var(--wl-ink-muted);
  margin: 0 0 32px;
}

/* ============================================================ */
/* RESPONSIVE                                                    */
/* ============================================================ */
@media (max-width: 1024px) {
  .article-head {
    grid-template-columns: 1fr;
    gap: 32px;
  }
}

@media (max-width: 768px) {
  .crumb,
  .article-head,
  .chart-wrap,
  .article-body {
    padding-left: 16px;
    padding-right: 16px;
  }

  .article-head__title {
    font-size: clamp(36px, 8vw, 56px);
  }

  .article-head__lede {
    font-size: 17px;
  }

  .chart-stage {
    padding: 16px 12px 8px;
  }

  .article-body__heading {
    font-size: 28px;
    margin-top: 36px;
  }

  .article-body :deep(p) {
    font-size: 16px;
  }

  .article-body__pull :deep(p) {
    font-size: 20px;
  }

  .chart-foot__inner {
    padding-left: 16px;
    padding-right: 16px;
  }
}
</style>
