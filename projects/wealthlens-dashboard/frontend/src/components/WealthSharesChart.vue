<script setup lang="ts">
/**
 * WealthSharesChart — Interactive line chart showing top 1% and top 10%
 * wealth share in the UK over time.
 *
 * Data source: World Inequality Database (wid.world)
 * Columns: year, percentile, value
 * Percentile filters: p99p100 (top 1%), p90p100 (top 10%)
 *
 * Accessibility: WCAG AA high-contrast colors, aria-label, keyboard tooltip.
 */
import { computed, onMounted, ref } from "vue";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { LineChart } from "echarts/charts";
import {
  GridComponent,
  TooltipComponent,
  TitleComponent,
  LegendComponent,
} from "echarts/components";
import VChart from "vue-echarts";
import { useDataStore, type DatasetRow } from "@/stores/data";

// Register only the ECharts modules we need (tree-shaking)
use([
  CanvasRenderer,
  LineChart,
  GridComponent,
  TooltipComponent,
  TitleComponent,
  LegendComponent,
]);

const store = useDataStore();
const rows = ref<DatasetRow[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);

onMounted(async () => {
  try {
    rows.value = await store.fetchDataset("wealth-shares");
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Failed to load wealth shares data";
  } finally {
    loading.value = false;
  }
});

/** Extract sorted year+value pairs for a given percentile key. */
function seriesFor(percentile: string): { years: number[]; values: number[] } {
  const filtered = rows.value
    .filter((r) => r.percentile === percentile)
    .map((r) => ({
      year: Number(r.year),
      value: Number(r.value),
    }))
    .sort((a, b) => a.year - b.year);

  return {
    years: filtered.map((r) => r.year),
    values: filtered.map((r) => r.value),
  };
}

// WCAG AA high-contrast colors against white background
// #1a56db (blue) contrast ratio ~7.2:1 — top 10%
// #dc2626 (red)  contrast ratio ~4.6:1 — top 1%
const COLOR_TOP_10 = "#1a56db";
const COLOR_TOP_1 = "#dc2626";

const option = computed(() => {
  const top1 = seriesFor("p99p100");
  const top10 = seriesFor("p90p100");

  // Use the longer year array for the x-axis (they should match)
  const years = top10.years.length >= top1.years.length ? top10.years : top1.years;

  return {
    title: {
      text: "UK Wealth Concentration Over Time",
      left: "center",
      textStyle: {
        fontSize: 16,
        fontWeight: "bold",
        color: "#111827",
      },
    },
    tooltip: {
      trigger: "axis" as const,
      axisPointer: { type: "cross" as const },
      formatter: (params: Array<{ seriesName: string; value: number; axisValue: string }>) => {
        if (!Array.isArray(params) || params.length === 0) return "";
        let html = `<strong>${params[0].axisValue}</strong><br/>`;
        for (const p of params) {
          const pct = typeof p.value === "number" ? p.value.toFixed(1) : p.value;
          html += `${p.seriesName}: ${pct}%<br/>`;
        }
        return html;
      },
    },
    legend: {
      bottom: 0,
      data: ["Top 10%", "Top 1%"],
      textStyle: { color: "#374151" },
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "12%",
      top: "15%",
      containLabel: true,
    },
    xAxis: {
      type: "category" as const,
      data: years,
      name: "Year",
      nameLocation: "middle" as const,
      nameGap: 30,
      axisLabel: {
        color: "#374151",
        rotate: years.length > 30 ? 45 : 0,
      },
    },
    yAxis: {
      type: "value" as const,
      name: "Share of wealth (%)",
      nameLocation: "middle" as const,
      nameGap: 50,
      axisLabel: {
        color: "#374151",
        formatter: "{value}%",
      },
    },
    series: [
      {
        name: "Top 10%",
        type: "line" as const,
        data: top10.values,
        smooth: true,
        lineStyle: { width: 2.5, color: COLOR_TOP_10 },
        itemStyle: { color: COLOR_TOP_10 },
        symbol: "circle",
        symbolSize: 4,
      },
      {
        name: "Top 1%",
        type: "line" as const,
        data: top1.values,
        smooth: true,
        lineStyle: { width: 2.5, color: COLOR_TOP_1 },
        itemStyle: { color: COLOR_TOP_1 },
        symbol: "circle",
        symbolSize: 4,
      },
    ],
  };
});
</script>

<template>
  <!-- Loading state -->
  <div v-if="loading" class="flex items-center justify-center py-20">
    <p class="text-gray-500 text-lg">Loading chart data...</p>
  </div>

  <!-- Error state -->
  <div v-else-if="error" class="py-10 text-center">
    <p class="text-red-600 font-medium">{{ error }}</p>
    <p class="text-gray-500 text-sm mt-2">
      Make sure the backend API is running on port 8000.
    </p>
  </div>

  <!-- Chart -->
  <div v-else>
    <div
      role="img"
      :aria-label="`Line chart showing UK wealth concentration over time. The top 10 percent held between ${Math.round(Math.min(...option.series[0].data))}% and ${Math.round(Math.max(...option.series[0].data))}% of total wealth. The top 1 percent held between ${Math.round(Math.min(...option.series[1].data))}% and ${Math.round(Math.max(...option.series[1].data))}% of total wealth.`"
      class="w-full"
    >
      <VChart
        class="w-full"
        style="height: 480px"
        :option="option"
        autoresize
      />
    </div>

    <!-- Source citation — visible text, not just tooltip (WCAG AA) -->
    <p class="text-sm text-gray-500 mt-4 text-center">
      Source:
      <a
        href="https://wid.world"
        target="_blank"
        rel="noopener"
        class="underline hover:text-gray-700"
      >
        World Inequality Database (wid.world)</a>, accessed 2026-05-14
    </p>
  </div>
</template>
