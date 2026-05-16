<script setup lang="ts">
/**
 * CgtConcentrationChart — Dual-axis bar + line chart showing capital gains
 * concentration by gain band.
 *
 * Data source: HMRC Capital Gains Tax Statistics
 * Columns: gain_band, band_lower, num_taxpayers_thousands,
 *          total_gains_millions, share_of_gains_pct, share_of_taxpayers_pct,
 *          cumul_gains_from_top_pct, cumul_taxpayers_from_top_pct
 *
 * Accessibility: WCAG AA high-contrast colors, aria-label, escapeHtml tooltips.
 */
import { computed } from "vue";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { BarChart, LineChart } from "echarts/charts";
import {
  GridComponent,
  TooltipComponent,
  TitleComponent,
  LegendComponent,
} from "echarts/components";
import VChart from "vue-echarts";
import { useChartData } from "@/composables/useChartData";
import { escapeHtml } from "@/utils/chart";

// Register only the ECharts modules we need (tree-shaking)
use([
  CanvasRenderer,
  BarChart,
  LineChart,
  GridComponent,
  TooltipComponent,
  TitleComponent,
  LegendComponent,
]);

const { rows, loading, error } = useChartData("cgt-concentration");

// WCAG AA high-contrast colors against white
// #1a56db (blue) contrast ratio ~7.2:1 — share of gains bars
// #dc2626 (red)  contrast ratio ~4.6:1 — cumulative line
const COLOR_BARS = "#1a56db";
const COLOR_LINE = "#dc2626";

/** Parsed and sorted data rows. */
const sortedData = computed(() => {
  return rows.value
    .map((r) => ({
      gainBand: String(r.gain_band ?? ""),
      bandLower: Number(r.band_lower),
      shareOfGainsPct: Number(r.share_of_gains_pct),
      cumulGainsFromTopPct: Number(r.cumul_gains_from_top_pct),
      shareOfTaxpayersPct: Number(r.share_of_taxpayers_pct),
      cumulTaxpayersFromTopPct: Number(r.cumul_taxpayers_from_top_pct),
    }))
    .filter(
      (r) =>
        r.gainBand &&
        !isNaN(r.bandLower) &&
        !isNaN(r.shareOfGainsPct) &&
        !isNaN(r.cumulGainsFromTopPct),
    )
    .sort((a, b) => a.bandLower - b.bandLower);
});

const hasData = computed(() => sortedData.value.length > 0);

/**
 * Build a headline insight for the aria-label.
 * Finds the highest-band entry and reports cumulative gains from top.
 */
const headlineInsight = computed(() => {
  const data = sortedData.value;
  if (data.length === 0) return "";
  // The last entry (highest band) has the cumulative stat from the top
  const top = data[data.length - 1];
  return `${top.cumulGainsFromTopPct.toFixed(0)}% of capital gains go to taxpayers with gains of ${top.gainBand} or more`;
});

const option = computed(() => {
  const data = sortedData.value;
  const labels = data.map((d) => d.gainBand);
  const shareValues = data.map((d) => d.shareOfGainsPct);
  const cumulValues = data.map((d) => d.cumulGainsFromTopPct);

  return {
    title: {
      text: "Capital Gains Tax — Concentration by Size of Gain",
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
        }>,
      ) => {
        if (!Array.isArray(params) || params.length === 0) return "";
        let html = `<strong>${escapeHtml(String(params[0].axisValue))}</strong><br/>`;
        for (const p of params) {
          const val =
            typeof p.value === "number" ? p.value.toFixed(1) : String(p.value);
          html += `${escapeHtml(String(p.seriesName))}: ${escapeHtml(val)}%<br/>`;
        }
        return html;
      },
    },
    legend: {
      bottom: 0,
      data: ["Share of total gains", "Cumulative from top"],
      textStyle: { color: "#374151" },
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
        rotate: labels.length > 6 ? 30 : 0,
      },
    },
    yAxis: [
      {
        type: "value" as const,
        name: "Share of total gains (%)",
        nameLocation: "middle" as const,
        nameGap: 50,
        position: "left" as const,
        axisLabel: {
          color: "#374151",
          formatter: "{value}%",
        },
      },
      {
        type: "value" as const,
        name: "Cumulative from top (%)",
        nameLocation: "middle" as const,
        nameGap: 50,
        position: "right" as const,
        axisLabel: {
          color: "#374151",
          formatter: "{value}%",
        },
      },
    ],
    series: [
      {
        name: "Share of total gains",
        type: "bar" as const,
        data: shareValues,
        yAxisIndex: 0,
        itemStyle: { color: COLOR_BARS },
        barMaxWidth: 50,
      },
      {
        name: "Cumulative from top",
        type: "line" as const,
        data: cumulValues,
        yAxisIndex: 1,
        smooth: true,
        lineStyle: { width: 2.5, color: COLOR_LINE },
        itemStyle: { color: COLOR_LINE },
        symbol: "circle",
        symbolSize: 6,
      },
    ],
  };
});
</script>

<template>
  <!-- Loading state -->
  <div v-if="loading" class="flex items-center justify-center py-20">
    <p class="text-[var(--wl-ink-muted)] text-lg">Loading chart data...</p>
  </div>

  <!-- Error state -->
  <div v-else-if="error" class="py-10 text-center">
    <p class="text-[var(--wl-red)] font-medium">{{ error }}</p>
    <p class="text-[var(--wl-ink-muted)] text-sm mt-2">
      Make sure the backend API is running on port 8000.
    </p>
  </div>

  <!-- No data state -->
  <div v-else-if="!hasData" class="py-10 text-center">
    <p class="text-[var(--wl-ink-muted)] text-lg">No data available for this chart.</p>
  </div>

  <!-- Chart -->
  <div v-else>
    <div
      role="img"
      :aria-label="`Dual-axis chart showing capital gains concentration by gain band. ${headlineInsight}. Bars show each band's share of total gains; red line shows cumulative concentration from the top.`"
      class="w-full"
    >
      <VChart
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
        href="https://www.gov.uk/government/statistics/capital-gains-tax-statistics"
        target="_blank"
        rel="noopener"
        class="underline hover:text-[var(--wl-ink)]"
      >
        HMRC Capital Gains Tax Statistics</a>, accessed 2026-05-14
    </p>
  </div>
</template>
