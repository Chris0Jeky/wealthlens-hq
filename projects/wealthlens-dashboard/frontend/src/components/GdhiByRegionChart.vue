<script setup lang="ts">
/**
 * GdhiByRegionChart — Horizontal bar chart showing Gross Disposable
 * Household Income per head by UK region.
 *
 * Data source: ONS Regional GDHI
 * Columns: region, gdhi_per_head, year
 *
 * Accessibility: WCAG AA high-contrast colors, aria-label, keyboard tooltip.
 */
import { computed, ref } from "vue";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { BarChart } from "echarts/charts";
import {
  GridComponent,
  TooltipComponent,
  TitleComponent,
  LegendComponent,
  MarkLineComponent,
} from "echarts/components";
import VChart from "vue-echarts";
import { useChartData } from "@/composables/useChartData";
import type { EChartsExportable } from "@/composables/useChartExport";
import { escapeHtml, safeMinMax, warnIfSignificantDataLoss } from "@/utils/chart";
import AccessibleDataTable from "@/components/AccessibleDataTable.vue";

// Register only the ECharts modules we need (tree-shaking)
use([
  CanvasRenderer,
  BarChart,
  GridComponent,
  TooltipComponent,
  TitleComponent,
  LegendComponent,
  MarkLineComponent,
]);

const { rows, loading, error } = useChartData("gdhi-by-region");
const chart = ref<EChartsExportable | null>(null);

defineExpose({ chart });

/**
 * Respect prefers-reduced-motion (WCAG 2.3.3).
 */
const prefersReducedMotion =
  typeof window !== "undefined" &&
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// WCAG AA high-contrast colors
const COLOR_BAR = "#1a56db"; // Blue — ~7.2:1
const COLOR_UK_AVG = "#b91c1c"; // Red-700 — ~5.7:1

/** Sorted data extracted from rows (sorted by GDHI descending). */
const chartData = computed(() => {
  const mapped = rows.value.map((r) => ({
    region: String(r.region ?? ""),
    gdhi: Number(r.gdhi_per_head),
    year: String(r.year ?? ""),
  }));
  const sorted = mapped
    .filter((r) => r.region && !isNaN(r.gdhi) && r.region !== "United Kingdom")
    .sort((a, b) => b.gdhi - a.gdhi);

  warnIfSignificantDataLoss("gdhi-by-region", mapped.length, sorted.length);

  // Extract the UK average for reference line
  const ukRow = rows.value.find((r) => String(r.region) === "United Kingdom");
  const ukAvg = ukRow ? Number(ukRow.gdhi_per_head) : 0;

  return {
    regions: sorted.map((r) => r.region),
    values: sorted.map((r) => r.gdhi),
    // Year carried per plotted row (same filter + sort) for the data-table fallback.
    years: sorted.map((r) => r.year),
    ukAvg,
  };
});

/** True when the API returned actual data to display. */
const hasData = computed(() => chartData.value.regions.length > 0);

/** GDHI range for aria-label. */
const gdhiRange = computed(() => safeMinMax(chartData.value.values));

/**
 * Accessible data-table fallback (WCAG 1.1.1). Mirrors the plotted series — one
 * row per region, highest GDHI first, with the United Kingdom aggregate excluded
 * exactly as the chart bars are — reusing the same already-loaded, verbatim
 * figures the chart draws (no re-fetch, no recompute).
 */
const tableColumns = ["Region", "GDHI per head (£)", "Year"];
const tableNumericColumns = ["GDHI per head (£)"];
const tableRows = computed(() => {
  const d = chartData.value;
  return d.regions.map((region, i) => ({
    Region: region,
    "GDHI per head (£)": d.values[i],
    Year: d.years[i],
  }));
});

/**
 * Table caption — cites the same ONS Regional GDHI source the chart shows. These
 * are official published ONS figures (no projection/illustrative caveat needed).
 */
const tableCaption =
  "Gross Disposable Household Income per head (£) by UK region, highest first, from ONS Regional GDHI. Excludes the United Kingdom aggregate, which the chart shows as a reference line.";

const option = computed(() => {
  const data = chartData.value;

  return {
    animation: !prefersReducedMotion,
    title: {
      text: "Gross Disposable Household Income by Region (2023)",
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
      formatter: (params: Array<{ seriesName: string; value: number; name: string }>) => {
        if (!Array.isArray(params) || params.length === 0) return "";
        const p = params[0];
        const val = typeof p.value === "number" ? `£${p.value.toLocaleString()}` : String(p.value);
        return `<strong>${escapeHtml(String(p.name))}</strong><br/>GDHI per head: ${escapeHtml(val)}`;
      },
    },
    grid: {
      left: "3%",
      right: "8%",
      bottom: "5%",
      top: "15%",
      containLabel: true,
    },
    xAxis: {
      type: "value" as const,
      name: "GDHI per head (£)",
      nameLocation: "middle" as const,
      nameGap: 30,
      axisLabel: {
        color: "#374151",
        formatter: (value: number) => `£${(value / 1000).toFixed(0)}k`,
      },
    },
    yAxis: {
      type: "category" as const,
      data: [...data.regions].reverse(),
      axisLabel: {
        color: "#374151",
        fontSize: 11,
      },
    },
    series: [
      {
        name: "GDHI per head",
        type: "bar" as const,
        data: [...data.values].reverse().map((val, i) => ({
          value: val,
          itemStyle: {
            color: data.values[data.regions.length - 1 - i] >= data.ukAvg
              ? COLOR_BAR
              : "#6b7280",
          },
        })),
        barMaxWidth: 24,
        markLine: data.ukAvg
          ? {
              silent: true,
              symbol: "none",
              lineStyle: { color: COLOR_UK_AVG, type: "dashed" as const, width: 2 },
              data: [{ xAxis: data.ukAvg, label: { formatter: "UK avg", position: "end" as const } }],
            }
          : undefined,
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
      :aria-label="`Bar chart showing Gross Disposable Household Income per head across ${chartData.regions.length} UK regions in 2023. Values range from £${gdhiRange.min.toLocaleString()} to £${gdhiRange.max.toLocaleString()} per head. UK average is £${chartData.ukAvg.toLocaleString()}.`"
      class="w-full"
    >
      <VChart
        ref="chart"
        class="w-full"
        style="height: 600px"
        :option="option"
        autoresize
      />
    </div>

    <!-- Accessible data-table fallback (WCAG 1.1.1 non-text content). -->
    <AccessibleDataTable
      :rows="tableRows"
      :columns="tableColumns"
      :numeric-columns="tableNumericColumns"
      :caption="tableCaption"
    />

    <!-- Source citation -->
    <p class="text-sm text-[var(--wl-ink-muted)] mt-4 text-center">
      Source:
      <a
        href="https://www.ons.gov.uk/economy/regionalaccounts/grossdisposablehouseholdincome"
        target="_blank"
        rel="noopener"
        class="underline hover:text-[var(--wl-ink)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--wl-red)] rounded"
      >
        ONS Regional GDHI<span class="sr-only"> (opens in new tab)</span></a>, accessed 2026-05-14
    </p>
  </div>
</template>
