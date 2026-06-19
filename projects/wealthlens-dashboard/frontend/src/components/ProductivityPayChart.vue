<script setup lang="ts">
/**
 * ProductivityPayChart — Diverging line chart showing the growing gap
 * between productivity growth and real pay growth in the UK since 1970.
 *
 * Data source: ONS Labour Productivity / ASHE (illustrative composite)
 * Columns: year, productivity_index, pay_index, gap_pct
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
import { useChartData } from "@/composables/useChartData";
import type { EChartsExportable } from "@/composables/useChartExport";
import { useDataStore } from "@/stores/data";
import { escapeHtml, safeMinMax, warnIfSignificantDataLoss } from "@/utils/chart";
import AccessibleDataTable from "@/components/AccessibleDataTable.vue";

// Register only the ECharts modules we need (tree-shaking)
use([
  CanvasRenderer,
  LineChart,
  GridComponent,
  TooltipComponent,
  TitleComponent,
  LegendComponent,
]);

const { rows, loading, error } = useChartData("productivity-pay");
const chart = ref<EChartsExportable | null>(null);

defineExpose({ chart });

/**
 * Data-honesty caveat: true only when the pipeline fell back to illustrative
 * data (sidecar data_type === "illustrative_fallback"). Default OFF — a live
 * dataset, a missing sidecar, or a failed metadata fetch all leave this false,
 * so the caveat shows ONLY when we positively know the data is illustrative.
 */
const isIllustrative = ref(false);
const dataStore = useDataStore();

onMounted(async () => {
  try {
    const meta = await dataStore.fetchMetadata("productivity-pay");
    isIllustrative.value = meta.data_type === "illustrative_fallback";
  } catch {
    // A metadata fetch failure must not break the chart; leave the caveat off.
    isIllustrative.value = false;
  }
});

/**
 * Respect prefers-reduced-motion (WCAG 2.3.3).
 */
const prefersReducedMotion =
  typeof window !== "undefined" &&
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// WCAG AA high-contrast colors
const COLOR_PRODUCTIVITY = "#1a56db"; // Blue — ~7.2:1
const COLOR_PAY = "#dc2626"; // Red — ~4.6:1

/**
 * Parse a raw dataset cell into a number, mapping missing values to NaN.
 *
 * Data honesty: `Number(null)` and `Number("")` both coerce to 0, which would
 * silently turn a missing source cell into a fabricated figure (a phantom 0%
 * gap). We map nullish/empty cells to NaN instead, so the accessible data table
 * renders the missing-value placeholder ("—") via AccessibleDataTable rather
 * than a misleading "0". Used here for the gap column, which the chart's own
 * filter does not require (so a missing gap can still reach the table).
 */
function toNumberOrNaN(value: string | number | null): number {
  return value != null && value !== "" ? Number(value) : NaN;
}

/** Sorted data extracted from rows. */
const chartData = computed(() => {
  const mapped = rows.value.map((r) => ({
    year: Number(r.year),
    productivity: Number(r.productivity_index),
    pay: Number(r.pay_index),
    // gap_pct is shown only in the accessible table, not plotted; it does not
    // gate the chart's filter below. toNumberOrNaN keeps a missing gap as NaN
    // so the table shows "—", never a fabricated 0%.
    gap: toNumberOrNaN(r.gap_pct),
  }));
  const sorted = mapped
    .filter((r) => !isNaN(r.year) && !isNaN(r.productivity) && !isNaN(r.pay))
    .sort((a, b) => a.year - b.year);

  warnIfSignificantDataLoss("productivity-pay", mapped.length, sorted.length);

  return {
    years: sorted.map((r) => r.year),
    productivity: sorted.map((r) => r.productivity),
    pay: sorted.map((r) => r.pay),
    gap: sorted.map((r) => r.gap),
  };
});

/** True when the API returned actual data to display. */
const hasData = computed(() => chartData.value.years.length > 0);

/** Year range for aria-label. */
const yearRange = computed(() => safeMinMax(chartData.value.years));

/** Productivity range for aria-label. */
const productivityRange = computed(() => safeMinMax(chartData.value.productivity));

/** Pay range for aria-label. */
const payRange = computed(() => safeMinMax(chartData.value.pay));

/**
 * Accessible data-table fallback (WCAG 1.1.1). Mirrors the plotted series — the
 * productivity and pay index per year — using the same already-loaded, verbatim,
 * filtered-and-sorted figures the chart draws, plus the gap-vs-pay percentage
 * carried alongside (see chartData). One row per plotted year, in chart order.
 */
const tableColumns = [
  "Year",
  "Productivity index",
  "Pay index",
  "Gap (%)",
];
const tableNumericColumns = ["Productivity index", "Pay index", "Gap (%)"];
const tableRows = computed<Record<string, string | number>[]>(() => {
  const d = chartData.value;
  return d.years.map((year, i) => ({
    // Year is a calendar year, deliberately kept OUT of tableNumericColumns so
    // it renders "1997", not "1,997".
    Year: year,
    "Productivity index": d.productivity[i],
    "Pay index": d.pay[i],
    "Gap (%)": d.gap[i],
  }));
});

/**
 * Table caption — appends the illustrative-provenance hedge only when the data
 * is actually illustrative (isIllustrative, set from the dataset metadata), so
 * the caption stays consistent with the on-page caveat. It self-hides if a live
 * ONS dataset is ever served (default OFF), mirroring the caveat.
 */
const tableCaption = computed(
  () =>
    "UK productivity index vs real-pay index by year (1997 = 100), with the productivity-vs-pay gap (%)." +
    (isIllustrative.value
      ? " Illustrative figures derived from ONS bulletins, not exact time-series values."
      : ""),
);

const option = computed(() => {
  const data = chartData.value;

  return {
    animation: !prefersReducedMotion,
    title: {
      text: "Productivity vs Pay — The Growing Divergence",
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
          const val = typeof p.value === "number" ? p.value.toFixed(1) : String(p.value);
          html += `${escapeHtml(String(p.seriesName))}: ${escapeHtml(val)}<br/>`;
        }
        return html;
      },
    },
    legend: {
      bottom: 0,
      data: ["Productivity (index)", "Real Pay (index)"],
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
      data: data.years,
      name: "Year",
      nameLocation: "middle" as const,
      nameGap: 30,
      axisLabel: {
        color: "#374151",
        rotate: data.years.length > 30 ? 45 : 0,
      },
    },
    yAxis: {
      type: "value" as const,
      name: "Index (1997 = 100)",
      nameLocation: "middle" as const,
      nameGap: 50,
      axisLabel: {
        color: "#374151",
      },
    },
    series: [
      {
        name: "Productivity (index)",
        type: "line" as const,
        data: data.productivity,
        smooth: !prefersReducedMotion,
        lineStyle: { width: 2.5, color: COLOR_PRODUCTIVITY },
        itemStyle: { color: COLOR_PRODUCTIVITY },
        symbol: "circle",
        symbolSize: 4,
      },
      {
        name: "Real Pay (index)",
        type: "line" as const,
        data: data.pay,
        smooth: !prefersReducedMotion,
        lineStyle: { width: 2.5, color: COLOR_PAY },
        itemStyle: { color: COLOR_PAY },
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
      :aria-label="`Line chart showing productivity vs real pay divergence from ${yearRange.min} to ${yearRange.max}. Productivity index ranges from ${productivityRange.min.toFixed(0)} to ${productivityRange.max.toFixed(0)}. Real pay index ranges from ${payRange.min.toFixed(0)} to ${payRange.max.toFixed(0)}.`"
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

    <!-- Accessible data-table fallback (WCAG 1.1.1 non-text content). -->
    <AccessibleDataTable
      :rows="tableRows"
      :columns="tableColumns"
      :numeric-columns="tableNumericColumns"
      :caption="tableCaption"
    />

    <!-- Data-honesty caveat — shown only when the pipeline used illustrative
         fallback data (data_type === "illustrative_fallback"). Default OFF. -->
    <p
      v-if="isIllustrative"
      class="text-xs text-[var(--wl-ink-muted)] mt-2 text-center italic"
    >
      Illustrative. Derived from ONS bulletins, not exact time-series values.
    </p>

    <!-- Source citation -->
    <p class="text-sm text-[var(--wl-ink-muted)] mt-4 text-center">
      Source:
      <a
        href="https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/labourproductivity"
        target="_blank"
        rel="noopener"
        class="underline hover:text-[var(--wl-ink)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--wl-red)] rounded"
      >
        ONS Labour Productivity<span class="sr-only"> (opens in new tab)</span></a>, accessed 2026-05-14
    </p>
  </div>
</template>
