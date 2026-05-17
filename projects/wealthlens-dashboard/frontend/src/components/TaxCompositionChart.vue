<script setup lang="ts">
/**
 * TaxCompositionChart — Stacked bar chart showing UK tax revenue breakdown
 * between taxes on work (income tax + NICs) and taxes on wealth (CGT + IHT + SDLT).
 *
 * Data source: HMRC Tax Receipts (illustrative composite)
 * Columns: year, income_tax_bn, nics_bn, cgt_bn, iht_bn, sdlt_bn,
 *          work_taxes_bn, wealth_taxes_bn, total_selected_bn, work_pct, wealth_pct
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
  LegendComponent,
]);

const { rows, loading, error } = useChartData("tax-composition");
const chart = ref<EChartsExportable | null>(null);

defineExpose({ chart });

/**
 * Respect prefers-reduced-motion (WCAG 2.3.3).
 */
const prefersReducedMotion =
  typeof window !== "undefined" &&
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// WCAG AA high-contrast colors for stacked categories
const COLOR_INCOME_TAX = "#1a56db"; // Blue — ~7.2:1
const COLOR_NICS = "#047857"; // Green — ~5.5:1
const COLOR_CGT = "#dc2626"; // Red — ~4.6:1
const COLOR_IHT = "#7c3aed"; // Purple — ~5.0:1
const COLOR_SDLT = "#b45309"; // Amber — ~4.7:1

/** Sorted data extracted from rows. */
const chartData = computed(() => {
  const mapped = rows.value.map((r) => ({
    year: String(r.year ?? ""),
    incomeTax: Number(r.income_tax_bn),
    nics: Number(r.nics_bn),
    cgt: Number(r.cgt_bn),
    iht: Number(r.iht_bn),
    sdlt: Number(r.sdlt_bn),
    workPct: Number(r.work_pct),
    wealthPct: Number(r.wealth_pct),
  }));
  const sorted = mapped.filter((r) => r.year && !isNaN(r.incomeTax));

  warnIfSignificantDataLoss("tax-composition", mapped.length, sorted.length);

  return {
    years: sorted.map((r) => r.year),
    incomeTax: sorted.map((r) => r.incomeTax),
    nics: sorted.map((r) => r.nics),
    cgt: sorted.map((r) => r.cgt),
    iht: sorted.map((r) => r.iht),
    sdlt: sorted.map((r) => r.sdlt),
    latestWorkPct: sorted.length > 0 ? sorted[sorted.length - 1].workPct : 0,
    latestWealthPct: sorted.length > 0 ? sorted[sorted.length - 1].wealthPct : 0,
  };
});

/** True when the API returned actual data to display. */
const hasData = computed(() => chartData.value.years.length > 0);

const option = computed(() => {
  const data = chartData.value;

  return {
    animation: !prefersReducedMotion,
    title: {
      text: "UK Tax Revenue — Work vs Wealth",
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
      formatter: (params: Array<{ seriesName: string; value: number; axisValue: string }>) => {
        if (!Array.isArray(params) || params.length === 0) return "";
        let html = `<strong>${escapeHtml(String(params[0].axisValue))}</strong><br/>`;
        let total = 0;
        for (const p of params) {
          if (typeof p.value !== "number") continue;
          total += p.value;
          html += `${escapeHtml(String(p.seriesName))}: £${p.value.toFixed(1)}bn<br/>`;
        }
        html += `<strong>Total: £${total.toFixed(1)}bn</strong>`;
        return html;
      },
    },
    legend: {
      bottom: 0,
      data: ["Income Tax", "NICs", "CGT", "IHT", "SDLT"],
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
      data: data.years,
      name: "Tax Year",
      nameLocation: "middle" as const,
      nameGap: 30,
      axisLabel: {
        color: "#374151",
        rotate: 25,
      },
    },
    yAxis: {
      type: "value" as const,
      name: "Revenue (£ billion)",
      nameLocation: "middle" as const,
      nameGap: 50,
      axisLabel: {
        color: "#374151",
        formatter: "£{value}bn",
      },
    },
    series: [
      {
        name: "Income Tax",
        type: "bar" as const,
        stack: "total",
        data: data.incomeTax,
        itemStyle: { color: COLOR_INCOME_TAX },
      },
      {
        name: "NICs",
        type: "bar" as const,
        stack: "total",
        data: data.nics,
        itemStyle: { color: COLOR_NICS },
      },
      {
        name: "CGT",
        type: "bar" as const,
        stack: "total",
        data: data.cgt,
        itemStyle: { color: COLOR_CGT },
      },
      {
        name: "IHT",
        type: "bar" as const,
        stack: "total",
        data: data.iht,
        itemStyle: { color: COLOR_IHT },
      },
      {
        name: "SDLT",
        type: "bar" as const,
        stack: "total",
        data: data.sdlt,
        itemStyle: { color: COLOR_SDLT },
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
      :aria-label="`Stacked bar chart showing UK tax revenue composition from ${chartData.years[0]} to ${chartData.years[chartData.years.length - 1]}. Taxes on work (income tax and NICs) make up approximately ${chartData.latestWorkPct.toFixed(0)}% of the total, while taxes on wealth (CGT, IHT, SDLT) account for just ${chartData.latestWealthPct.toFixed(0)}%.`"
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
        href="https://www.gov.uk/government/statistics/hmrc-tax-and-nics-receipts-for-the-uk"
        target="_blank"
        rel="noopener"
        class="underline hover:text-[var(--wl-ink)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--wl-red)] rounded"
      >
        HMRC Tax Receipts<span class="sr-only"> (opens in new tab)</span></a>, accessed 2026-05-14
    </p>
  </div>
</template>
