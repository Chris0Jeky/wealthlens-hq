<script setup lang="ts">
/**
 * ChartView — Dedicated page for viewing a single chart.
 *
 * Uses the route param :name to determine which chart component to render.
 * Currently supports: wealth-shares, housing-affordability, cgt-concentration
 */
import { computed, defineAsyncComponent } from "vue";
import { useRoute } from "vue-router";

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

const chartName = computed(() => route.params.name as string);

/** Map of supported chart names to display titles. */
const chartTitles: Record<string, string> = {
  "wealth-shares": "Wealth Shares — Top 1% and Top 10%",
  "housing-affordability": "Housing Affordability — Price-to-Earnings Ratios by Region",
  "cgt-concentration": "Capital Gains Tax — Concentration by Size of Gain",
  "wealth-by-decile": "Total Household Wealth by Decile",
};

const isSupported = computed(() => chartName.value in chartTitles);
</script>

<template>
  <div class="chart-page">
    <!-- Back link -->
    <router-link
      to="/"
      class="chart-page-back"
    >
      &larr; Back to datasets
    </router-link>

    <!-- Supported chart -->
    <template v-if="isSupported">
      <h1 class="chart-page-title">{{ chartTitles[chartName] }}</h1>

      <WealthSharesChart v-if="chartName === 'wealth-shares'" />
      <HousingAffordabilityChart v-else-if="chartName === 'housing-affordability'" />
      <CgtConcentrationChart v-else-if="chartName === 'cgt-concentration'" />
      <WealthByDecileChart v-else-if="chartName === 'wealth-by-decile'" />
    </template>

    <!-- Unsupported chart name -->
    <div v-else class="chart-page-404">
      <h1 class="chart-page-404-title">Chart not found</h1>
      <p class="chart-page-404-body">
        No chart is available for "<span class="chart-page-mono">{{ chartName }}</span>".
      </p>
      <router-link
        to="/"
        class="chart-page-404-link"
      >
        Return to dashboard
      </router-link>
    </div>
  </div>
</template>

<style scoped>
/* ============================================================
   CHART VIEW — dedicated chart page layout
   ============================================================ */
.chart-page {
  max-width: 72rem;
  margin: 0 auto;
  padding: 2.5rem 1.5rem;
}

.chart-page-back {
  display: inline-flex;
  align-items: center;
  font-size: 14px;
  color: var(--wl-red);
  text-decoration: none;
  margin-bottom: 1.5rem;
  min-height: 44px;
}

.chart-page-back:hover {
  color: var(--wl-red-deep);
}

.chart-page-title {
  font-family: var(--wl-serif);
  font-size: clamp(22px, 4vw, 32px);
  font-weight: 700;
  color: var(--wl-ink);
  margin: 0 0 1.5rem;
  line-height: 1.15;
}

/* --- 404 state ----------------------------------------------- */
.chart-page-404 {
  padding: 2.5rem 0;
  text-align: center;
}

.chart-page-404-title {
  font-family: var(--wl-serif);
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--wl-ink);
  margin: 0 0 0.75rem;
}

.chart-page-404-body {
  color: var(--wl-ink-muted);
}

.chart-page-mono {
  font-family: var(--wl-mono);
}

.chart-page-404-link {
  display: inline-block;
  margin-top: 1rem;
  color: var(--wl-red);
  text-decoration: underline;
  min-height: 44px;
  line-height: 44px;
}

.chart-page-404-link:hover {
  color: var(--wl-red-deep);
}

/* --- Responsive ---------------------------------------------- */
@media (max-width: 768px) {
  .chart-page {
    padding: 1.5rem 1rem;
  }

  .chart-page-title {
    font-size: clamp(20px, 5vw, 28px);
  }
}

@media (max-width: 375px) {
  .chart-page {
    padding: 1rem 0.75rem;
  }
}
</style>
