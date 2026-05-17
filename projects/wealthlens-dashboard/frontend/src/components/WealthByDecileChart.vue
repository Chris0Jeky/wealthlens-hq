<script setup lang="ts">
/**
 * WealthByDecileChart — Bar chart showing total household wealth by decile.
 *
 * Data source: ONS Wealth and Assets Survey
 * Columns: decile, total_wealth_bn (GBP billions)
 *
 * The 1st (poorest) decile has negative net wealth and is highlighted
 * in a warning color. All other bars use a standard WCAG AA compliant blue.
 *
 * Accessibility: WCAG AA high-contrast colors, aria-label, escapeHtml tooltips.
 */
import { computed, ref } from "vue";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { BarChart } from "echarts/charts";
import {
  GridComponent,
  TooltipComponent,
  TitleComponent,
} from "echarts/components";
import VChart from "vue-echarts";
import { useChartData } from "@/composables/useChartData";
import type { EChartsExportable } from "@/composables/useChartExport";
import { escapeHtml, warnIfSignificantDataLoss } from "@/utils/chart";

// Register only the ECharts modules we need (tree-shaking)
use([
  CanvasRenderer,
  BarChart,
  GridComponent,
  TooltipComponent,
  TitleComponent,
]);

const { rows, loading, error } = useChartData("wealth-by-decile");
const chart = ref<EChartsExportable | null>(null);

defineExpose({ chart });

/**
 * Respect prefers-reduced-motion (WCAG 2.3.3).
 * Disables ECharts animations when the user has requested reduced motion.
 */
const prefersReducedMotion =
  typeof window !== "undefined" &&
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// WCAG AA high-contrast colors against white
// #1a56db (blue) contrast ratio ~7.2:1 — standard bars
// #b91c1c (red-700) contrast ratio ~5.7:1 — negative value warning
const COLOR_BAR = "#1a56db";
const COLOR_NEGATIVE = "#b91c1c";

/** Parsed data rows preserving CSV order (1st poorest to 10th richest). */
const parsedData = computed(() => {
  const mapped = rows.value.map((r) => ({
    decile: String(r.decile ?? ""),
    totalWealthBn: Number(r.total_wealth_bn),
  }));
  const filtered = mapped.filter((r) => r.decile && !isNaN(r.totalWealthBn));

  warnIfSignificantDataLoss("wealth-by-decile", mapped.length, filtered.length);

  return filtered;
});

const hasData = computed(() => parsedData.value.length > 0);

/** Build a headline insight for the aria-label. */
const headlineInsight = computed(() => {
  const data = parsedData.value;
  if (data.length === 0) return "";
  const richest = data[data.length - 1];
  const poorest = data[0];
  if (!richest || !poorest) return "";
  return `The ${richest.decile} decile holds ${richest.totalWealthBn.toLocaleString()}bn in total wealth, while the ${poorest.decile} decile has ${poorest.totalWealthBn.toLocaleString()}bn`;
});

const option = computed(() => {
  const data = parsedData.value;
  const labels = data.map((d) => d.decile);
  const values = data.map((d) => d.totalWealthBn);

  // Color each bar: red for negative values, blue for positive
  const barColors = values.map((v) =>
    v < 0 ? COLOR_NEGATIVE : COLOR_BAR,
  );

  return {
    animation: !prefersReducedMotion,
    title: {
      text: "Total Household Wealth by Decile (GBP Billions)",
      left: "center",
      textStyle: {
        fontSize: 16,
        fontWeight: "bold",
        color: "#111827",
      },
    },
    tooltip: {
      trigger: "axis" as const,
      axisPointer: { type: "shadow" as const },
      formatter: (
        params: Array<{
          seriesName: string;
          value: number;
          axisValue: string;
          dataIndex: number;
        }>,
      ) => {
        if (!Array.isArray(params) || params.length === 0) return "";
        const p = params[0];
        const val =
          typeof p.value === "number" ? p.value.toFixed(1) : String(p.value);
        let html = `<strong>${escapeHtml(String(p.axisValue))}</strong><br/>`;
        html += `Total wealth: ${escapeHtml(val)}bn`;
        if (typeof p.value === "number" && p.value < 0) {
          html += `<br/><em style="color:${COLOR_NEGATIVE}">Net negative wealth</em>`;
        }
        return html;
      },
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "15%",
      top: "15%",
      containLabel: true,
    },
    xAxis: {
      type: "category" as const,
      data: labels,
      axisLabel: {
        color: "#374151",
        rotate: 30,
      },
    },
    yAxis: {
      type: "value" as const,
      name: "Total wealth (GBP bn)",
      nameLocation: "middle" as const,
      nameGap: 60,
      axisLabel: {
        color: "#374151",
        formatter: (value: number) => `£${value.toLocaleString()}`,
      },
    },
    series: [
      {
        name: "Total wealth",
        type: "bar" as const,
        data: values.map((v, i) => ({
          value: v,
          itemStyle: { color: barColors[i] },
        })),
        barMaxWidth: 60,
      },
    ],
  };
});
</script>

<template>
  <!-- Loading state -->
  <div v-if="loading" class="flex items-center justify-center py-20" role="status" aria-live="polite">
    <p class="text-[var(--wl-ink-muted)] text-lg">Loading chart data...</p>
  </div>

  <!-- Error state -->
  <div v-else-if="error" class="py-10 text-center" role="alert">
    <p class="text-[var(--wl-red)] font-medium">{{ error }}</p>
    <p class="text-[var(--wl-ink-muted)] text-sm mt-2">
      Make sure the backend API is running on port 8000.
    </p>
  </div>

  <!-- No data state -->
  <div v-else-if="!hasData" class="py-10 text-center" role="status">
    <p class="text-[var(--wl-ink-muted)] text-lg">No data available for this chart.</p>
  </div>

  <!-- Chart -->
  <div v-else>
    <div
      role="img"
      :aria-label="`Bar chart showing total household wealth by decile in the UK. ${headlineInsight}. The poorest decile is highlighted in red to indicate net negative wealth.`"
      class="w-full"
    >
      <VChart
        ref="chart"
        class="w-full"
        style="height: 480px"
        :option="option"
        autoresize
      />
    </div>

    <!-- Source citation -->
    <p class="text-sm text-[var(--wl-ink-muted)] mt-4 text-center">
      Source:
      <a
        href="https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/bulletins/totalwealthingreatbritain/latest"
        target="_blank"
        rel="noopener"
        class="underline hover:text-[var(--wl-ink)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--wl-red)] rounded"
      >
        ONS Wealth and Assets Survey<span class="sr-only"> (opens in new tab)</span></a>, accessed 2026-05-15
    </p>
  </div>
</template>
