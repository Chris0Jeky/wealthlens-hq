<script setup lang="ts">
/**
 * BoeRatesChart — Line chart showing Bank of England base rate and CPI
 * inflation over time. Shows the relationship between monetary policy
 * and cost of living.
 *
 * Data source: Bank of England / ONS CPI
 * Columns: date, bank_rate, cpi_annual
 *
 * Accessibility: WCAG AA high-contrast colors, aria-label, keyboard tooltip.
 */
import { computed } from "vue";
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
import { useChartData } from "@/composables/useChartData";
import { escapeHtml, safeMinMax, warnIfSignificantDataLoss } from "@/utils/chart";

// Register only the ECharts modules we need (tree-shaking)
use([
  CanvasRenderer,
  LineChart,
  GridComponent,
  TooltipComponent,
  TitleComponent,
  LegendComponent,
]);

const { rows, loading, error } = useChartData("boe-rates");

/**
 * Respect prefers-reduced-motion (WCAG 2.3.3).
 */
const prefersReducedMotion =
  typeof window !== "undefined" &&
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// WCAG AA high-contrast colors
const COLOR_BANK_RATE = "#1a56db"; // Blue — ~7.2:1
const COLOR_CPI = "#dc2626"; // Red — ~4.6:1

/** Sorted data extracted from rows. */
const chartData = computed(() => {
  const mapped = rows.value.map((r) => ({
    date: String(r.date ?? ""),
    bankRate: Number(r.bank_rate),
    cpi: Number(r.cpi_annual),
  }));
  const sorted = mapped
    .filter((r) => r.date && !isNaN(r.bankRate) && !isNaN(r.cpi))
    .sort((a, b) => a.date.localeCompare(b.date));

  warnIfSignificantDataLoss("boe-rates", mapped.length, sorted.length);

  return {
    dates: sorted.map((r) => {
      // Format date labels: extract year or year-month
      const d = new Date(r.date);
      if (isNaN(d.getTime())) return r.date;
      return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
    }),
    bankRate: sorted.map((r) => r.bankRate),
    cpi: sorted.map((r) => r.cpi),
  };
});

/** True when the API returned actual data to display. */
const hasData = computed(() => chartData.value.dates.length > 0);

/** Bank rate range for aria-label. */
const rateRange = computed(() => safeMinMax(chartData.value.bankRate));

/** CPI range for aria-label. */
const cpiRange = computed(() => safeMinMax(chartData.value.cpi));

const option = computed(() => {
  const data = chartData.value;

  return {
    animation: !prefersReducedMotion,
    title: {
      text: "Bank of England Base Rate vs CPI Inflation",
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
        let html = `<strong>${escapeHtml(String(params[0].axisValue))}</strong><br/>`;
        for (const p of params) {
          const val = typeof p.value === "number" ? p.value.toFixed(2) : String(p.value);
          html += `${escapeHtml(String(p.seriesName))}: ${escapeHtml(val)}%<br/>`;
        }
        return html;
      },
    },
    legend: {
      bottom: 0,
      data: ["Bank Rate", "CPI Inflation"],
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
      data: data.dates,
      name: "Date",
      nameLocation: "middle" as const,
      nameGap: 30,
      axisLabel: {
        color: "#374151",
        rotate: 45,
        interval: Math.max(0, Math.floor(data.dates.length / 12)),
      },
    },
    yAxis: {
      type: "value" as const,
      name: "Rate (%)",
      nameLocation: "middle" as const,
      nameGap: 40,
      axisLabel: {
        color: "#374151",
        formatter: "{value}%",
      },
    },
    series: [
      {
        name: "Bank Rate",
        type: "line" as const,
        data: data.bankRate,
        smooth: false,
        step: "end" as const,
        lineStyle: { width: 2.5, color: COLOR_BANK_RATE },
        itemStyle: { color: COLOR_BANK_RATE },
        symbol: "circle",
        symbolSize: 4,
      },
      {
        name: "CPI Inflation",
        type: "line" as const,
        data: data.cpi,
        smooth: !prefersReducedMotion,
        lineStyle: { width: 2.5, color: COLOR_CPI },
        itemStyle: { color: COLOR_CPI },
        symbol: "circle",
        symbolSize: 4,
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
      :aria-label="`Line chart showing Bank of England base rate and CPI inflation from ${chartData.dates[0]} to ${chartData.dates[chartData.dates.length - 1]}. Bank rate ranged from ${rateRange.min.toFixed(2)}% to ${rateRange.max.toFixed(2)}%. CPI inflation ranged from ${cpiRange.min.toFixed(1)}% to ${cpiRange.max.toFixed(1)}%.`"
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
        href="https://www.bankofengland.co.uk/monetary-policy/the-interest-rate-bank-rate"
        target="_blank"
        rel="noopener"
        class="underline hover:text-[var(--wl-ink)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--wl-red)] rounded"
      >
        Bank of England<span class="sr-only"> (opens in new tab)</span></a> /
      <a
        href="https://www.ons.gov.uk/economy/inflationandpriceindices"
        target="_blank"
        rel="noopener"
        class="underline hover:text-[var(--wl-ink)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--wl-red)] rounded"
      >
        ONS CPI<span class="sr-only"> (opens in new tab)</span></a>, accessed 2026-05-14
    </p>
  </div>
</template>
