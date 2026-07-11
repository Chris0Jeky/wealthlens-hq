<script setup lang="ts">
/**
 * HomeView — the editorial front page.
 *
 * Broadsheet structure: one sourced headline figure (the lead), the featured
 * chart inline, a tools row, the full chart index grouped by pillar, then
 * the dataset/download layer. Every figure on this page is grounded in the
 * WID p90p100/p99p100 series the wealth-shares article plots (values
 * verified 2026-06-19 against public/data/wealth-shares.json — see the
 * provenance comment in chartArticles.ts).
 */
import { onMounted, computed, ref, defineAsyncComponent } from "vue"
import { useDataStore } from "@/stores/data"
import DatasetCard from "@/components/DatasetCard.vue"
import DatasetSearch from "@/components/DatasetSearch.vue"
import ResponsiveGrid from "@/components/ResponsiveGrid.vue"
import ChartSkeleton from "@/components/ChartSkeleton.vue"
import ChartLoadError from "@/components/ChartLoadError.vue"
import { CHART_METADATA } from "@/utils/chartConstants"
import { prefetchRouteComponents } from "@/utils/prefetch"
import { usePageMeta } from "@/composables/usePageMeta"
import { SITE_URL } from "@/constants/site"
import { chartConfigs, simpleChartTitles } from "@/config/chartArticles"
import { HOME_PILLARS } from "@/config/homePillars"

/** Featured chart is lazy so the echarts chunk loads after first paint. */
const WealthSharesChart = defineAsyncComponent({
  loader: () => import("@/components/WealthSharesChart.vue"),
  loadingComponent: ChartSkeleton,
  errorComponent: ChartLoadError,
  delay: 200,
  timeout: 10000,
})

const store = useDataStore()
const searchFilter = ref<{ active: boolean; names: string[] }>({
  active: false,
  names: [],
})

usePageMeta({
  title: "UK Wealth Inequality Dashboard",
  description:
    "The wealthiest 10% hold 57% of UK personal wealth (WID, 2024). Open-source, source-backed charts, calculators, and a policy simulator — every figure cites its source.",
  url: `${SITE_URL}/`,
  image: `${SITE_URL}/og/og-landing.png`,
  imageAlt: "WealthLens UK — UK Wealth Inequality. 57% of wealth held by top 10%.",
  twitterCard: "summary_large_image",
})

/** Interactive tools — the row that de-orphans them (reality-check F6). */
const TOOLS = [
  {
    to: "/tools/wealth-scale",
    name: "The wealth scale",
    blurb: "1 pixel = £1,000. Scroll UK wealth drawn to scale.",
  },
  {
    to: "/tools/wealth-calculator",
    name: "Where do you fit?",
    blurb: "Enter your household wealth, see your place in the distribution.",
  },
  {
    to: "/tools/tax-calculator",
    name: "Your real tax rate",
    blurb: "How much of your income actually goes in tax.",
  },
  {
    to: "/tools/wealth-tax-simulator",
    name: "Wealth tax simulator",
    blurb: "Set thresholds and rates; see what a wealth tax would raise.",
  },
  {
    to: "/faq",
    name: "FAQ & glossary",
    blurb: "The questions everyone asks, and the terms the charts use.",
  },
] as const

/** Chart title from the article config — no copy here to drift. */
function chartTitle(slug: string): string {
  const config = chartConfigs[slug]
  if (config) {
    return config.headlineEmphasis
      ? `${config.headline} ${config.headlineEmphasis}`
      : config.headline
  }
  return simpleChartTitles[slug] ?? slug
}

/** All 10 datasets in display order (the downloadable data layer). */
const ALL_DATASETS = [
  "wealth-shares",
  "housing-affordability",
  "cgt-concentration",
  "wealth-by-decile",
  "productivity-pay",
  "gdhi-by-region",
  "tax-composition",
  "boe-rates",
  "child-poverty",
  "generational-wealth",
] as const

/** Fallback descriptions for datasets without chart metadata. */
const FALLBACK_DESCRIPTIONS: Record<string, string> = {
  "wealth-shares": "Top 1% and 10% share of UK net personal wealth since 1820 (WID)",
  "housing-affordability": "House price to earnings ratio by region, 1997-2025 (ONS)",
  "cgt-concentration": "Capital gains concentration by size of gain (HMRC)",
  "wealth-by-decile": "Total net wealth by decile group in Great Britain (ONS WAS)",
  "productivity-pay": "Gap between productivity growth and median pay in the UK (ONS)",
  "gdhi-by-region": "Gross disposable household income by UK region (ONS)",
  "tax-composition": "Breakdown of UK tax receipts by source over time (HMRC/OBR)",
  "boe-rates": "Bank of England base interest rate history (BoE)",
  "child-poverty": "Children in relative poverty by UK region and nation (DWP)",
  "generational-wealth": "Wealth distribution across generations in Great Britain (ONS WAS)",
}

/** Local state for metadata enrichment (does not gate card rendering). */
const metadataLoading = ref(true)
const metadataError = ref<string | null>(null)

/** Connectivity warning when fetchDatasets fails (non-blocking — cards are hardcoded). */
const datasetsError = ref<string | null>(null)

const visibleDatasets = computed(() => {
  if (!searchFilter.value.active) return ALL_DATASETS
  const allowed = new Set(searchFilter.value.names)
  return ALL_DATASETS.filter((name) => allowed.has(name))
})

function onSearchFiltered(payload: { active: boolean; names: string[] }) {
  searchFilter.value = payload
}

/** Get description for a dataset from metadata or fallback. */
function getDescription(name: string): string {
  const meta = store.metadata.get(name)
  if (meta?.description) return meta.description
  const chart = Object.values(CHART_METADATA).find((c) => c.name === name)
  if (chart?.description) return chart.description
  return FALLBACK_DESCRIPTIONS[name] ?? "UK inequality dataset"
}

onMounted(async () => {
  // Track both fetches with Promise.allSettled so neither silently fails
  const results = await Promise.allSettled([
    store.fetchDatasets(),
    store.fetchAllMetadata(),
    store.fetchFreshness(),
  ])

  metadataLoading.value = false

  // Report dataset fetch failure (non-blocking — card list is hardcoded)
  if (results[0].status === "rejected") {
    datasetsError.value =
      results[0].reason instanceof Error
        ? results[0].reason.message
        : "Failed to connect to data service"
  }

  // Report metadata enrichment failure (non-blocking — fallback descriptions used)
  if (results[1].status === "rejected") {
    metadataError.value =
      results[1].reason instanceof Error ? results[1].reason.message : "Failed to load metadata"
  }

  // Prefetch the most likely next navigations after idle
  prefetchRouteComponents([
    () => import("@/views/ChartView.vue"),
    () => import("@/views/DatasetDetailView.vue"),
  ])
})
</script>

<template>
  <div class="front max-w-6xl mx-auto px-6 py-10">
    <!-- ================= LEAD STORY ================= -->
    <section class="lead" aria-labelledby="lead-heading">
      <p class="kicker">The headline</p>
      <h1 id="lead-heading" class="lead-claim">
        The wealthiest 10% hold
        <span class="lead-figure"
          >57<sup aria-hidden="true">%</sup><span class="sr-only"> per cent</span></span
        >
        of all UK personal wealth
      </h1>
      <p class="lead-standfirst">
        The top 1% alone hold 21%. The other nine in ten households share 43% — less than the top
        tenth holds by itself. It has been this way, or worse, for two centuries.
      </p>
      <p class="lead-source">
        Source:
        <a href="https://wid.world" target="_blank" rel="noopener">World Inequality Database</a>
        · net personal wealth, UK, 2024 · accessed 14 May 2026 · CC-BY 4.0
      </p>
      <div class="lead-actions">
        <router-link to="/charts/wealth-shares" class="wl-btn wl-btn--red">
          Read the full story →
        </router-link>
        <router-link to="/methodology" class="wl-btn wl-btn--ghost">How we source this</router-link>
      </div>
    </section>

    <!-- ================= FEATURED CHART ================= -->
    <section class="featured" aria-labelledby="featured-heading">
      <div class="rule-head"><span>Featured chart</span></div>
      <h2 id="featured-heading" class="section-title">Two centuries of concentration</h2>
      <figure class="featured-figure">
        <WealthSharesChart />
        <figcaption class="featured-caption">
          Share of UK net personal wealth held by the top 10% and the top 1%, 1820–2024. Source:
          <a href="https://wid.world" target="_blank" rel="noopener">World Inequality Database</a>
          (accessed 14 May 2026) · CC-BY 4.0.
        </figcaption>
      </figure>
      <router-link to="/charts/wealth-shares" class="section-more">
        Open the full article →
      </router-link>
    </section>

    <!-- ================= TOOLS ================= -->
    <section class="tools" aria-labelledby="tools-heading">
      <div class="rule-head"><span>Do the numbers yourself</span></div>
      <h2 id="tools-heading" class="section-title">Interactive tools</h2>
      <ul class="tools-grid" role="list">
        <li v-for="tool in TOOLS" :key="tool.to" class="tool-card">
          <router-link :to="tool.to" class="tool-link">
            <span class="tool-name">{{ tool.name }}</span>
            <span class="tool-blurb">{{ tool.blurb }}</span>
          </router-link>
        </li>
      </ul>
    </section>

    <!-- ================= ALL CHARTS BY PILLAR ================= -->
    <section id="charts" class="pillars" aria-labelledby="charts-heading">
      <div class="rule-head"><span>The data</span></div>
      <h2 id="charts-heading" class="section-title">All 12 charts</h2>
      <div class="pillars-grid">
        <div v-for="pillar in HOME_PILLARS" :key="pillar.label" class="pillar">
          <h3 class="pillar-label">{{ pillar.label }}</h3>
          <ul class="pillar-list" role="list">
            <li v-for="slug in pillar.charts" :key="slug">
              <router-link :to="`/charts/${slug}`" class="pillar-link">
                {{ chartTitle(slug) }}
              </router-link>
            </li>
          </ul>
        </div>
      </div>
    </section>

    <!-- ================= DATA LAYER ================= -->
    <section class="datasets" aria-labelledby="datasets-heading">
      <div class="rule-head"><span>Downloads</span></div>
      <h2 id="datasets-heading" class="section-title">Datasets &amp; downloads</h2>

      <!-- Dataset search/filter -->
      <DatasetSearch @filtered-change="onSearchFiltered" />

      <!-- Dataset connectivity warning (non-blocking — cards are hardcoded) -->
      <div
        v-if="datasetsError"
        role="status"
        class="rounded-lg border border-amber-300 dark:border-amber-700 bg-amber-50 dark:bg-amber-950 p-4 mb-4"
      >
        <p class="text-sm text-amber-800 dark:text-amber-200">
          Unable to reach the data service — showing cached dataset list.
        </p>
      </div>

      <!-- Metadata enrichment error (non-blocking) -->
      <div
        v-if="metadataError"
        role="status"
        class="rounded-lg border border-amber-300 dark:border-amber-700 bg-amber-50 dark:bg-amber-950 p-4 mb-4"
      >
        <p class="text-sm text-amber-800 dark:text-amber-200">
          Metadata enrichment unavailable — showing default descriptions.
        </p>
      </div>

      <!-- Dataset cards always render (hardcoded data, no API dependency) -->
      <ResponsiveGrid min-width="280px" gap="1.5rem" role="list">
        <div v-for="name in visibleDatasets" :key="name" role="listitem">
          <DatasetCard
            :name="name"
            :description="getDescription(name)"
            :freshness="store.freshness?.[name]"
          />
        </div>
      </ResponsiveGrid>
    </section>
  </div>
</template>

<style scoped>
/* ---------- shared section furniture (broadsheet rules) ---------- */
.kicker,
.rule-head span {
  font-family: var(--wl-mono);
  font-size: 11px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--wl-red);
  font-weight: 500;
}

.rule-head {
  border-top: 2px solid var(--wl-ink);
  padding-top: 8px;
  margin-bottom: 8px;
}

.section-title {
  font-family: var(--wl-serif);
  font-size: clamp(22px, 3vw, 30px);
  font-weight: 700;
  letter-spacing: -0.015em;
  color: var(--wl-ink);
  margin-bottom: 20px;
}

.section-more {
  display: inline-block;
  margin-top: 14px;
  font-size: 14px;
  font-weight: 600;
  color: var(--wl-red);
  text-decoration: none;
}

.section-more:hover {
  color: var(--wl-red-deep);
}

section {
  margin-bottom: 56px;
}

/* ---------- lead story ---------- */
.lead {
  padding-top: 8px;
}

.lead-claim {
  font-family: var(--wl-serif);
  font-size: clamp(30px, 5vw, 52px);
  font-weight: 700;
  line-height: 1.12;
  letter-spacing: -0.02em;
  color: var(--wl-ink);
  max-width: 21ch;
  margin: 10px 0 18px;
}

.lead-figure {
  color: var(--wl-red);
  font-size: 1.9em;
  line-height: 1;
  vertical-align: -0.08em;
  padding: 0 0.04em;
}

.lead-figure sup {
  font-family: var(--wl-mono);
  font-size: 0.32em;
  font-weight: 500;
  vertical-align: top;
  position: relative;
  top: 0.35em;
  opacity: 0.75;
}

.lead-standfirst {
  font-size: clamp(16px, 2vw, 19px);
  line-height: 1.55;
  color: var(--wl-ink-body);
  max-width: 58ch;
  margin-bottom: 12px;
}

.lead-source {
  font-family: var(--wl-mono);
  font-size: 12px;
  color: var(--wl-ink-muted);
  margin-bottom: 22px;
}

.lead-source a {
  color: inherit;
  text-decoration: underline;
}

.lead-source a:hover {
  color: var(--wl-ink);
}

.lead-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

/* ---------- featured chart ---------- */
.featured-figure {
  margin: 0;
}

.featured-caption {
  font-family: var(--wl-mono);
  font-size: 12px;
  line-height: 1.6;
  color: var(--wl-ink-muted);
  margin-top: 10px;
}

.featured-caption a {
  color: inherit;
  text-decoration: underline;
}

/* ---------- tools row ---------- */
.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1px;
  background: var(--wl-rule);
  border: 1px solid var(--wl-rule);
  padding: 0;
  margin: 0;
  list-style: none;
}

.tool-card {
  background: var(--wl-card);
}

.tool-link {
  display: flex;
  flex-direction: column;
  gap: 6px;
  height: 100%;
  padding: 18px 16px;
  text-decoration: none;
  transition: background 0.15s ease;
}

.tool-link:hover {
  background: var(--wl-bg-muted);
}

.tool-name {
  font-family: var(--wl-serif);
  font-size: 18px;
  font-weight: 700;
  color: var(--wl-ink);
}

.tool-link:hover .tool-name {
  color: var(--wl-red);
}

.tool-blurb {
  font-size: 13px;
  line-height: 1.5;
  color: var(--wl-ink-muted);
}

/* ---------- pillar chart index ---------- */
.pillars-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 28px;
}

.pillar-label {
  font-family: var(--wl-mono);
  font-size: 11px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--wl-ink-muted);
  font-weight: 500;
  border-bottom: 1px solid var(--wl-rule-strong);
  padding-bottom: 6px;
  margin-bottom: 10px;
}

.pillar-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
}

.pillar-link {
  display: block;
  padding: 8px 0;
  font-family: var(--wl-serif);
  font-size: 16px;
  font-weight: 600;
  line-height: 1.35;
  color: var(--wl-ink);
  text-decoration: none;
  border-bottom: 1px solid var(--wl-rule);
}

.pillar-link:hover {
  color: var(--wl-red);
}
</style>
