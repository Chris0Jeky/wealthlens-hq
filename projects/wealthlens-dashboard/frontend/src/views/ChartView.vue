<script setup lang="ts">
/**
 * ChartView — Dedicated page for viewing a single chart.
 *
 * Uses the route param :name to determine which chart component to render.
 * Currently supports: wealth-shares, housing-affordability, cgt-concentration
 */
import { computed, defineAsyncComponent, watch } from "vue";
import { useRoute } from "vue-router";
import ShareButton from "@/components/ShareButton.vue";
import { CHART_METADATA, isValidChart } from "@/utils/chartConstants";
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

const isSupported = computed(() => isValidChart(chartName.value));

const chartTitle = computed(() =>
  isValidChart(chartName.value) ? CHART_METADATA[chartName.value].title : "",
);

/** Track chart views when the chart name changes. */
watch(chartName, (name) => {
  if (name && isValidChart(name)) {
    trackEvent("view_chart", { chart: name });
  }
}, { immediate: true });
</script>

<template>
  <div class="max-w-6xl mx-auto px-6 py-10">
    <!-- Back link -->
    <router-link
      to="/"
      class="inline-flex items-center text-sm text-[var(--wl-red)] hover:text-[var(--wl-red-deep)] mb-6"
    >
      &larr; Back to datasets
    </router-link>

    <!-- Supported chart -->
    <template v-if="isSupported">
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-2xl font-bold">{{ chartTitle }}</h1>
        <ShareButton />
      </div>

      <WealthSharesChart v-if="chartName === 'wealth-shares'" />
      <HousingAffordabilityChart v-else-if="chartName === 'housing-affordability'" />
      <CgtConcentrationChart v-else-if="chartName === 'cgt-concentration'" />
      <WealthByDecileChart v-else-if="chartName === 'wealth-by-decile'" />
    </template>

    <!-- Unsupported chart name -->
    <div v-else class="py-10 text-center">
      <h1 class="text-2xl font-bold mb-3">Chart not found</h1>
      <p class="text-[var(--wl-ink-muted)]">
        No chart is available for "<span class="font-mono">{{ chartName }}</span>".
      </p>
      <router-link
        to="/"
        class="inline-block mt-4 text-[var(--wl-red)] hover:text-[var(--wl-red-deep)] underline"
      >
        Return to dashboard
      </router-link>
    </div>
  </div>
</template>
