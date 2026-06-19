<script setup lang="ts">
/**
 * WageStagChart — Line chart showing UK real wage stagnation since 2008.
 *
 * Displays:
 * - Solid line: actual median real weekly earnings (2000-2024, CPI-adjusted)
 * - Dashed line: counterfactual (1.5% p.a. real growth from 2008 peak — observed 2000-2008 real wage CAGR)
 * - Shaded area below counterfactual line (visual emphasis of lost-wage zone)
 * - Mark point: 2008 peak
 * - Annotation: gap in pounds per week / per year
 *
 * Data source: ONS Annual Survey of Hours and Earnings (ASHE), Table 1
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
  MarkPointComponent,
  MarkLineComponent,
} from "echarts/components";
import VChart from "vue-echarts";
import { useChartData } from "@/composables/useChartData";
import { escapeHtml } from "@/utils/chart";
import AccessibleDataTable from "@/components/AccessibleDataTable.vue";

// Register only the ECharts modules we need (tree-shaking)
use([
  CanvasRenderer,
  LineChart,
  GridComponent,
  TooltipComponent,
  TitleComponent,
  LegendComponent,
  MarkPointComponent,
  MarkLineComponent,
]);

const { rows, loading, error } = useChartData("wage-stagnation");

/**
 * Respect prefers-reduced-motion (WCAG 2.3.3).
 * Disables ECharts smooth lines and animations when the user has
 * requested reduced motion in their OS settings.
 */
const prefersReducedMotion =
  typeof window !== "undefined" &&
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// WCAG AA high-contrast colors against white background
// #1a56db (blue) contrast ratio ~6.2:1 — actual earnings line
// #dc2626 (red)  contrast ratio ~4.8:1 — counterfactual line
// rgba(220,38,38,0.08) — shaded area below counterfactual line (subtle)
const COLOR_ACTUAL = "#1a56db";
const COLOR_COUNTERFACTUAL = "#dc2626";
const COLOR_GAP_FILL = "rgba(220, 38, 38, 0.08)";

/** Peak year for the counterfactual start. */
const PEAK_YEAR = 2008;
const PEAK_VALUE = 520;
const ANNUAL_GROWTH = 0.015;

/** Sorted actual data from the store. */
const actualData = computed(() => {
  return rows.value
    .map((r) => ({
      year: Number(r.year),
      value: Number(r.real_weekly),
    }))
    .filter((r) => !isNaN(r.year) && !isNaN(r.value))
    .sort((a, b) => a.year - b.year);
});

/** Whether valid data is available. */
const hasData = computed(() => actualData.value.length > 0);

/** All years for the x-axis. */
const years = computed(() => actualData.value.map((d) => d.year));

/** Actual values aligned with years. */
const actualValues = computed(() => actualData.value.map((d) => d.value));

/**
 * Counterfactual series: 1.5% annual growth (observed 2000-2008 real wage CAGR) from the 2008 peak.
 * Null for years before 2008 (so ECharts doesn't draw a line there).
 */
const counterfactualValues = computed(() => {
  return years.value.map((year) => {
    if (year < PEAK_YEAR) return null;
    const elapsed = year - PEAK_YEAR;
    return Math.round(PEAK_VALUE * Math.pow(1 + ANNUAL_GROWTH, elapsed));
  });
});

/** Difference between counterfactual and actual, used to shade only the gap. */
const gapValues = computed(() => {
  return counterfactualValues.value.map((counterfactual, index) => {
    if (counterfactual == null) return null;
    return Math.max(0, counterfactual - actualValues.value[index]);
  });
});

/** The gap in pounds per week between counterfactual and actual in 2024. */
const weeklyGap = computed(() => {
  const data = actualData.value;
  if (data.length === 0) return 0;
  const latest = data[data.length - 1];
  const counterfactual2024 = Math.round(
    PEAK_VALUE * Math.pow(1 + ANNUAL_GROWTH, latest.year - PEAK_YEAR),
  );
  return counterfactual2024 - latest.value;
});

/** Annual gap in thousands. */
const annualGapK = computed(() => {
  return Math.round((weeklyGap.value * 52) / 1000);
});

/** Latest actual value for aria-label. */
const latestValue = computed(() => {
  const data = actualData.value;
  return data.length > 0 ? data[data.length - 1].value : 0;
});

/** Latest year. */
const latestYear = computed(() => {
  const data = actualData.value;
  return data.length > 0 ? data[data.length - 1].year : 2024;
});

/**
 * Accessible data-table fallback (WCAG 1.1.1). Mirrors the solid "actual
 * earnings" series the chart plots — median real weekly pay per year — using the
 * same already-loaded, filtered, year-sorted, verbatim figures (`actualData`).
 * The counterfactual/gap series are derived visual aids, not source data, so the
 * table reports only the genuine ONS figures.
 */
const tableColumns = ["Year", "Real weekly pay (£)"];
const tableNumericColumns = ["Real weekly pay (£)"];
const tableRows = computed<Record<string, string | number>[]>(() =>
  actualData.value.map((d) => ({
    Year: d.year,
    // actualData already drops rows whose real_weekly is missing/non-numeric
    // (its isNaN filter), so every value here is finite; AccessibleDataTable
    // would render any non-finite value as "—" rather than a fabricated figure.
    "Real weekly pay (£)": d.value,
  })),
);

const option = computed(() => {
  return {
    animation: !prefersReducedMotion,
    title: {
      text: "UK Real Wage Stagnation",
      subtext: "Median real weekly earnings (2024 prices, CPI-adjusted)",
      left: "center",
      textStyle: {
        fontSize: 16,
        fontWeight: "bold",
        color: "#111827",
      },
      subtextStyle: {
        fontSize: 12,
        color: "#6b7280",
      },
    },
    tooltip: {
      trigger: "axis" as const,
      axisPointer: { type: "cross" as const },
      formatter: (
        params: Array<{
          seriesName: string;
          value: number | null;
          axisValue: string;
        }>,
      ) => {
        if (!Array.isArray(params) || params.length === 0) return "";
        let html = `<strong>${escapeHtml(String(params[0].axisValue))}</strong><br/>`;
        for (const p of params) {
          if (p.value == null) continue;
          const val = `£${p.value}`;
          html += `${escapeHtml(String(p.seriesName))}: ${escapeHtml(val)}/week<br/>`;
        }
        return html;
      },
    },
    legend: {
      bottom: 0,
      data: ["Actual earnings", "If 1.5% growth continued"],
      textStyle: { color: "#374151" },
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "12%",
      top: "18%",
      containLabel: true,
    },
    xAxis: {
      type: "category" as const,
      data: years.value,
      name: "Year",
      nameLocation: "middle" as const,
      nameGap: 30,
      axisLabel: {
        color: "#374151",
      },
    },
    yAxis: {
      type: "value" as const,
      name: "£ per week",
      nameLocation: "middle" as const,
      nameGap: 50,
      min: 440,
      axisLabel: {
        color: "#374151",
        formatter: "£{value}",
      },
    },
    series: [
      {
        name: "Actual earnings",
        type: "line" as const,
        stack: "lost-wage-gap",
        data: actualValues.value,
        smooth: !prefersReducedMotion,
        lineStyle: { width: 3, color: COLOR_ACTUAL },
        itemStyle: { color: COLOR_ACTUAL },
        symbol: "circle",
        symbolSize: 4,
        markPoint: {
          data: [
            {
              name: "2008 peak",
              coord: [years.value.indexOf(PEAK_YEAR), PEAK_VALUE],
              symbol: "pin",
              symbolSize: 40,
              itemStyle: { color: COLOR_ACTUAL },
              label: {
                show: true,
                formatter: "2008\npeak",
                color: "#fff",
                fontSize: 10,
              },
            },
          ],
        },
        areaStyle: undefined,
      },
      {
        name: "Lost wage gap",
        type: "line" as const,
        stack: "lost-wage-gap",
        data: gapValues.value,
        smooth: !prefersReducedMotion,
        lineStyle: { opacity: 0 },
        itemStyle: { opacity: 0 },
        symbol: "none",
        areaStyle: {
          color: COLOR_GAP_FILL,
        },
        silent: true,
        tooltip: { show: false },
        z: -1,
      },
      {
        name: "If 1.5% growth continued",
        type: "line" as const,
        data: counterfactualValues.value,
        smooth: !prefersReducedMotion,
        lineStyle: {
          width: 2,
          color: COLOR_COUNTERFACTUAL,
          type: "dashed" as const,
        },
        itemStyle: { color: COLOR_COUNTERFACTUAL },
        symbol: "none",
        z: 1,
      },
    ],
  };
});
</script>

<template>
  <!-- Loading state -->
  <div
    v-if="loading"
    class="flex items-center justify-center py-20"
    role="status"
    aria-live="polite"
  >
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
    <p class="text-[var(--wl-ink-muted)] text-lg">
      No data available for this chart.
    </p>
  </div>

  <!-- Chart -->
  <div v-else>
    <div
      role="img"
      :aria-label="`Line chart showing UK median real weekly earnings from 2000 to ${latestYear}. The 2008 peak was £${PEAK_VALUE} per week. By ${latestYear}, actual earnings were £${latestValue} per week — £${weeklyGap} per week less than if pre-crisis growth had continued, a gap of approximately £${annualGapK},000 per year.`"
      class="w-full"
    >
      <VChart
        class="w-full"
        style="height: 480px"
        :option="option"
        autoresize
      />
    </div>

    <!-- Accessible data-table fallback (WCAG 1.1.1 non-text content). -->
    <AccessibleDataTable
      :rows="tableRows"
      :columns="tableColumns"
      :numeric-columns="tableNumericColumns"
      caption="UK median real weekly earnings by year (£, 2024 prices, CPI-adjusted). Source: ONS Annual Survey of Hours and Earnings (ASHE)."
    />

    <!-- Gap annotation -->
    <p
      class="text-center text-lg font-semibold text-[var(--wl-red)] mt-4"
      aria-hidden="true"
    >
      £{{ weeklyGap }}/week gap = ~£{{ annualGapK }},000/year lost
    </p>

    <!-- Disclaimer -->
    <p class="text-xs text-[var(--wl-ink-muted)] mt-2 text-center italic">
      Illustrative. Real values CPI-adjusted to 2024 prices.
    </p>

    <!-- Source citation — visible text, not just tooltip (WCAG AA) -->
    <p class="text-sm text-[var(--wl-ink-muted)] mt-4 text-center">
      Source:
      <a
        href="https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/ashe1702"
        target="_blank"
        rel="noopener"
        class="underline hover:text-[var(--wl-ink)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--wl-red)] rounded"
      >
        ONS ASHE<span class="sr-only"> (opens in new tab)</span></a
      >, accessed 2026-05-16
    </p>
  </div>
</template>
