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
import { escapeHtml, toNumberOrNaN, warnIfSignificantDataLoss } from "@/utils/chart";
import AccessibleDataTable from "@/components/AccessibleDataTable.vue";

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
    incomeTax: toNumberOrNaN(r.income_tax_bn),
    nics: toNumberOrNaN(r.nics_bn),
    cgt: toNumberOrNaN(r.cgt_bn),
    iht: toNumberOrNaN(r.iht_bn),
    sdlt: toNumberOrNaN(r.sdlt_bn),
    workPct: toNumberOrNaN(r.work_pct),
    wealthPct: toNumberOrNaN(r.wealth_pct),
  }));
  // Require ALL five plotted components to be finite: this is a stacked total, so
  // one missing component would understate the stack and render "£NaNbn" in the
  // tooltip total. Dropping the incomplete year keeps the stacked total honest
  // (it also drops from the accessible table, which mirrors this same data).
  const sorted = mapped.filter(
    (r) =>
      r.year &&
      !isNaN(r.incomeTax) &&
      !isNaN(r.nics) &&
      !isNaN(r.cgt) &&
      !isNaN(r.iht) &&
      !isNaN(r.sdlt),
  );

  warnIfSignificantDataLoss("tax-composition", mapped.length, sorted.length);

  return {
    years: sorted.map((r) => r.year),
    incomeTax: sorted.map((r) => r.incomeTax),
    nics: sorted.map((r) => r.nics),
    cgt: sorted.map((r) => r.cgt),
    iht: sorted.map((r) => r.iht),
    sdlt: sorted.map((r) => r.sdlt),
    workPct: sorted.map((r) => r.workPct),
    wealthPct: sorted.map((r) => r.wealthPct),
    latestWorkPct: sorted.length > 0 ? sorted[sorted.length - 1].workPct : 0,
    latestWealthPct: sorted.length > 0 ? sorted[sorted.length - 1].wealthPct : 0,
  };
});

/** True when the API returned actual data to display. */
const hasData = computed(() => chartData.value.years.length > 0);

/**
 * Data-honesty flag: the tax-composition dataset is an illustrative composite
 * (each row carries data_source === "illustrative"), so we surface a caveat
 * whenever any plotted row is illustrative. Positive signal only — if the data
 * ever carried real figures the caveat would correctly stay hidden.
 */
const isIllustrative = computed(
  () =>
    rows.value.length > 0 &&
    rows.value.some((r) => r.data_source === "illustrative"),
);

/**
 * Accessible data-table fallback (WCAG 1.1.1). Mirrors the plotted series — the
 * five component taxes per year plus the work/wealth split — using the same
 * already-loaded, verbatim figures the chart draws.
 */
const tableColumns = [
  "Tax year",
  "Income Tax (£bn)",
  "NICs (£bn)",
  "CGT (£bn)",
  "IHT (£bn)",
  "SDLT (£bn)",
  "Work taxes (%)",
  "Wealth taxes (%)",
];
const tableNumericColumns = tableColumns.filter((c) => c !== "Tax year");
const tableRows = computed(() => {
  const d = chartData.value;
  return d.years.map((year, i) => ({
    "Tax year": year,
    "Income Tax (£bn)": d.incomeTax[i],
    "NICs (£bn)": d.nics[i],
    "CGT (£bn)": d.cgt[i],
    "IHT (£bn)": d.iht[i],
    "SDLT (£bn)": d.sdlt[i],
    "Work taxes (%)": d.workPct[i],
    "Wealth taxes (%)": d.wealthPct[i],
  }));
});

/**
 * Table caption — appends the illustrative-provenance hedge only when the data is
 * actually illustrative, so the caption stays consistent with the caveat and the
 * aria-label (all three self-hide if genuine HMRC figures are ever served).
 */
const tableCaption = computed(
  () =>
    "UK tax revenue composition by year: the five component taxes (£bn) and the share from taxes on work vs wealth (%)." +
    (isIllustrative.value
      ? " Illustrative composite figures approximated from HMRC receipts, not exact published values."
      : ""),
);

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
          // Skip non-finite (NaN/Infinity) so a missing component never renders
          // "£NaNbn" or poisons the running total. (typeof NaN === "number".)
          if (!Number.isFinite(p.value)) continue;
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
      :aria-label="`Stacked bar chart showing UK tax revenue composition from ${chartData.years[0]} to ${chartData.years[chartData.years.length - 1]}. Taxes on work (income tax and NICs) make up approximately ${chartData.latestWorkPct.toFixed(0)}% of the total, while taxes on wealth (CGT, IHT, SDLT) account for just ${chartData.latestWealthPct.toFixed(0)}%.${isIllustrative ? ' Figures are an illustrative composite approximated from HMRC receipts, not exact published values.' : ''}`"
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

    <!-- Data-honesty caveat — rendered exactly when a plotted row is marked
         illustrative (a positive signal). For the current composite dataset that
         is always true; it would self-hide if genuine HMRC figures were served. -->
    <p
      v-if="isIllustrative"
      class="text-xs text-[var(--wl-ink-muted)] mt-2 text-center italic"
    >
      Illustrative composite. Approximated from HMRC receipts, not exact published values.
    </p>

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
