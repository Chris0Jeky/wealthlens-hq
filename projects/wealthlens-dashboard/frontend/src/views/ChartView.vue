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
import ChartToolbar from "@/components/ChartToolbar.vue";
import ShareBar from "@/components/ShareBar.vue";
import SharePanel from "@/components/SharePanel.vue";
import RelatedCharts from "@/components/RelatedCharts.vue";
import { useAnalytics } from "@/composables/useAnalytics";
import { usePageMeta } from "@/composables/usePageMeta";
import ChartSkeleton from "@/components/ChartSkeleton.vue";
import ChartLoadError from "@/components/ChartLoadError.vue";
import { chartConfigs, simpleChartTitles } from "@/config/chartArticles";

/**
 * Lazy-load chart components to avoid bundling ECharts on every route.
 * Each uses the object form of defineAsyncComponent with error handling,
 * a loading skeleton, and a 10-second timeout to prevent silent failures
 * when JS chunks fail to load (deploy race, network issue).
 */
const WealthSharesChart = defineAsyncComponent({
  loader: () => import("@/components/WealthSharesChart.vue"),
  loadingComponent: ChartSkeleton,
  errorComponent: ChartLoadError,
  delay: 200,
  timeout: 10000,
});
const HousingAffordabilityChart = defineAsyncComponent({
  loader: () => import("@/components/HousingAffordabilityChart.vue"),
  loadingComponent: ChartSkeleton,
  errorComponent: ChartLoadError,
  delay: 200,
  timeout: 10000,
});
const CgtConcentrationChart = defineAsyncComponent({
  loader: () => import("@/components/CgtConcentrationChart.vue"),
  loadingComponent: ChartSkeleton,
  errorComponent: ChartLoadError,
  delay: 200,
  timeout: 10000,
});
const WealthByDecileChart = defineAsyncComponent({
  loader: () => import("@/components/WealthByDecileChart.vue"),
  loadingComponent: ChartSkeleton,
  errorComponent: ChartLoadError,
  delay: 200,
  timeout: 10000,
});
const ProductivityPayChart = defineAsyncComponent({
  loader: () => import("@/components/ProductivityPayChart.vue"),
  loadingComponent: ChartSkeleton,
  errorComponent: ChartLoadError,
  delay: 200,
  timeout: 10000,
});
const GdhiByRegionChart = defineAsyncComponent({
  loader: () => import("@/components/GdhiByRegionChart.vue"),
  loadingComponent: ChartSkeleton,
  errorComponent: ChartLoadError,
  delay: 200,
  timeout: 10000,
});
const TaxCompositionChart = defineAsyncComponent({
  loader: () => import("@/components/TaxCompositionChart.vue"),
  loadingComponent: ChartSkeleton,
  errorComponent: ChartLoadError,
  delay: 200,
  timeout: 10000,
});
const BoeRatesChart = defineAsyncComponent({
  loader: () => import("@/components/BoeRatesChart.vue"),
  loadingComponent: ChartSkeleton,
  errorComponent: ChartLoadError,
  delay: 200,
  timeout: 10000,
});
const ChildPovertyChart = defineAsyncComponent({
  loader: () => import("@/components/ChildPovertyChart.vue"),
  loadingComponent: ChartSkeleton,
  errorComponent: ChartLoadError,
  delay: 200,
  timeout: 10000,
});
const GenerationalWealthChart = defineAsyncComponent({
  loader: () => import("@/components/GenerationalWealthChart.vue"),
  loadingComponent: ChartSkeleton,
  errorComponent: ChartLoadError,
  delay: 200,
  timeout: 10000,
});

const route = useRoute();
const { trackEvent } = useAnalytics();
const chartName = computed(() => route.params.name as string);

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
const activeRange = ref("");

/**
 * Reset activeRange to the chart's default when navigating between charts.
 * This prevents stale range selections from persisting across pages
 * (e.g. "200y" showing on a chart that only has ["All", "10y", "5y"]).
 */
watch(
  () => chartName.value,
  (name) => {
    const cfg = chartConfigs[name];
    activeRange.value = cfg?.toolbar.defaultRange ?? "";
  },
  { immediate: true },
);

/** Whether the share panel is visible. */
const sharePanelOpen = ref(false);

function toggleSharePanel(): void {
  sharePanelOpen.value = !sharePanelOpen.value;
}

function onRangeChange(range: string) {
  activeRange.value = range;
}

/** Convert legacy hardcoded HTML snippets to display/meta-safe plain text. */
function toPlainText(html: string): string {
  if (typeof DOMParser === "undefined") {
    return html.replace(/<[^>]*>/g, " ").replace(/\s+/g, " ").trim();
  }
  const doc = new DOMParser().parseFromString(html, "text/html");
  return doc.body.textContent?.replace(/\s+/g, " ").trim() ?? "";
}

/** Track chart views when the chart name changes. */
watch(chartName, (name) => {
  if (name && isSupported.value) {
    trackEvent("view_chart", { chart: name });
  }
}, { immediate: true });

/* ------------------------------------------------------------------ */
/* Page meta (OpenGraph / Twitter Card)                                */
/* ------------------------------------------------------------------ */

const chartTitle = computed(() => {
  if (config.value) return config.value.headline;
  return simpleChartTitles[chartName.value] ?? chartName.value;
});

const chartDescription = computed(() => {
  if (config.value) {
    return toPlainText(config.value.lede);
  }
  return `UK wealth inequality data — ${chartTitle.value}`;
});

const chartOgImage = computed(
  () => `https://chris0jeky.github.io/wealthlens-hq/og/${chartName.value}.png`,
);

const chartUrl = computed(
  () => `https://chris0jeky.github.io/wealthlens-hq/charts/${chartName.value}`,
);

usePageMeta({
  title: chartTitle,
  description: chartDescription,
  url: chartUrl,
  image: chartOgImage,
  imageAlt: computed(() => `${chartTitle.value} — WealthLens UK chart`),
  ogType: "article",
  twitterCard: "summary_large_image",
});
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
        <p class="article-head__lede">{{ toPlainText(config.lede) }}</p>
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
          <ProductivityPayChart v-else-if="chartName === 'productivity-pay'" />
          <GdhiByRegionChart v-else-if="chartName === 'gdhi-by-region'" />
          <TaxCompositionChart v-else-if="chartName === 'tax-composition'" />
          <BoeRatesChart v-else-if="chartName === 'boe-rates'" />
          <ChildPovertyChart v-else-if="chartName === 'child-poverty'" />
          <GenerationalWealthChart v-else-if="chartName === 'generational-wealth'" />
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

      <!-- Share bar with toggle button -->
      <ShareBar :chart-id="config.source.chartId">
        <template #append>
          <button
            type="button"
            class="share-toggle-btn"
            :aria-expanded="sharePanelOpen"
            aria-controls="share-panel"
            @click="toggleSharePanel"
          >
            <svg
              viewBox="0 0 16 16"
              fill="none"
              stroke="currentColor"
              stroke-width="1.5"
              aria-hidden="true"
            >
              <path d="M4 9a2 2 0 1 0 0-4 2 2 0 0 0 0 4zM12 5a2 2 0 1 0 0-4 2 2 0 0 0 0 4zM12 15a2 2 0 1 0 0-4 2 2 0 0 0 0 4zM5.7 8.2l4.6-2.4M5.7 7.8l4.6 2.4" />
            </svg>
            {{ sharePanelOpen ? "Close" : "Share & Embed" }}
          </button>
        </template>
      </ShareBar>

      <!-- Share panel (toggled) -->
      <SharePanel
        v-if="sharePanelOpen"
        id="share-panel"
        :chart-name="chartName"
        :chart-title="config.headline"
      />
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
          <p>{{ toPlainText(config.article.pullQuote.text) }}</p>
        </div>

        <p
          v-for="(para, j) in section.paragraphs"
          :key="`p-${i}-${j}`"
        >
          {{ toPlainText(para) }}
        </p>
      </template>

      <!-- Methodology accordion -->
      <details class="method">
        <summary>Methodology &amp; data quality</summary>
        <div class="method__body method__body--plain">
          {{ toPlainText(config.methodology) }}
        </div>
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
              v-else-if="chartName === 'cgt-concentration'"
            />
            <WealthByDecileChart
              v-else-if="chartName === 'wealth-by-decile'"
            />
          </div>
        </div>

        <!-- Share toggle for simple layout -->
        <div class="simple-share-row">
          <button
            type="button"
            class="share-toggle-btn"
            :aria-expanded="sharePanelOpen"
            aria-controls="share-panel-simple"
            @click="toggleSharePanel"
          >
            <svg
              viewBox="0 0 16 16"
              fill="none"
              stroke="currentColor"
              stroke-width="1.5"
              aria-hidden="true"
            >
              <path d="M4 9a2 2 0 1 0 0-4 2 2 0 0 0 0 4zM12 5a2 2 0 1 0 0-4 2 2 0 0 0 0 4zM12 15a2 2 0 1 0 0-4 2 2 0 0 0 0 4zM5.7 8.2l4.6-2.4M5.7 7.8l4.6 2.4" />
            </svg>
            {{ sharePanelOpen ? "Close" : "Share & Embed" }}
          </button>
        </div>

        <SharePanel
          v-if="sharePanelOpen"
          id="share-panel-simple"
          :chart-name="chartName"
          :chart-title="simpleChartTitles[chartName] || chartName"
        />
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
.crumb__link:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: 2px;
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

/* Ensure consistent spacing on the simple-layout chart card */
.simple-layout .chart-card {
  margin-bottom: 32px;
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
.meta-card__link:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: 2px;
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
.method summary::marker {
  display: none;
  content: "";
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
/* SIMPLE SHARE ROW                                              */
/* ============================================================ */
.simple-share-row {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

/* ============================================================ */
/* SHARE TOGGLE BUTTON                                           */
/* ============================================================ */
.share-toggle-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  background: var(--wl-red);
  border: 1px solid var(--wl-red);
  font-family: var(--wl-mono);
  font-size: 11px;
  color: #fff;
  cursor: pointer;
  letter-spacing: 0.04em;
  font-weight: 600;
  margin-left: 8px;
}
.share-toggle-btn:hover {
  background: var(--wl-ink);
  border-color: var(--wl-ink);
}
.share-toggle-btn:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: 2px;
}
.share-toggle-btn svg {
  width: 14px;
  height: 14px;
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
