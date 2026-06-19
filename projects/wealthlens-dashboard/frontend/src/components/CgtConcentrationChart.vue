<script setup lang="ts">
/**
 * CgtConcentrationChart — capital gains concentration, shown in two views.
 *
 * The component offers an additive tab toggle (default: the existing "By gain
 * band" view, so existing behaviour is unchanged / backward-compatible):
 *   - "By gain band" (default): dual-axis bar + line chart showing each band's
 *     share of total gains (bars) and the cumulative concentration from the top
 *     (line). This is the original chart, untouched.
 *   - "Concentration curve" (opt-in): a Lorenz-style concentration curve that
 *     plots the cumulative share of gains against the cumulative share of
 *     taxpayers (both measured FROM THE TOP), with a static y=x equality
 *     reference line, plus an AccessibleDataTable fallback of the same rows.
 *
 * Data source: HMRC Capital Gains Tax Statistics
 * Columns: gain_band, band_lower, num_taxpayers_thousands,
 *          total_gains_millions, share_of_gains_pct, share_of_taxpayers_pct,
 *          cumul_gains_from_top_pct, cumul_taxpayers_from_top_pct
 *
 * Accessibility: WCAG AA high-contrast colors, aria-label, escapeHtml tooltips,
 * an accessible tab group, and an AccessibleDataTable fallback for the
 * concentration curve (WCAG 1.1.1 non-text content).
 */
import { computed, ref } from "vue";
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
import TabGroup, { type Tab } from "@/components/TabGroup.vue";
import AccessibleDataTable from "@/components/AccessibleDataTable.vue";
import type { DatasetRow } from "@/stores/data";
import { useChartData } from "@/composables/useChartData";
import type { EChartsExportable } from "@/composables/useChartExport";
import { escapeHtml, warnIfSignificantDataLoss } from "@/utils/chart";

// Register only the ECharts modules we need (tree-shaking). The y=x equality
// reference line is drawn as an ordinary line series, so no MarkLineComponent.
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
// #1a56db (blue) contrast ratio ~7.2:1 — share of gains bars / concentration curve
// #dc2626 (red)  contrast ratio ~4.6:1 — cumulative line
// #6b7280 (gray) contrast ratio ~4.8:1 — equality reference line (dashed)
const COLOR_BARS = "#1a56db";
const COLOR_LINE = "#dc2626";
const COLOR_CURVE = "#1a56db";
const COLOR_EQUALITY = "#6b7280";

/**
 * Parse a numeric cell, treating null/undefined/empty as MISSING (NaN) rather
 * than 0. The real data has genuine nulls (e.g. a band with no cumulative
 * taxpayer figure), and Number(null) === 0 — which would fabricate a real data
 * point at the origin. Mapping missing values to NaN lets the downstream
 * isNaN() filters drop them instead of plotting a false (0, y) coordinate.
 */
function toFiniteOrNaN(v: unknown): number {
  if (v === null || v === undefined || v === "") return NaN;
  return Number(v);
}

/** Parsed and sorted data rows. */
const sortedData = computed(() => {
  const mapped = rows.value.map((r) => ({
    gainBand: String(r.gain_band ?? ""),
    bandLower: toFiniteOrNaN(r.band_lower),
    shareOfGainsPct: toFiniteOrNaN(r.share_of_gains_pct),
    cumulGainsFromTopPct: toFiniteOrNaN(r.cumul_gains_from_top_pct),
    shareOfTaxpayersPct: toFiniteOrNaN(r.share_of_taxpayers_pct),
    cumulTaxpayersFromTopPct: toFiniteOrNaN(r.cumul_taxpayers_from_top_pct),
  }));
  const filtered = mapped
    .filter(
      (r) =>
        r.gainBand &&
        !isNaN(r.bandLower) &&
        !isNaN(r.shareOfGainsPct) &&
        !isNaN(r.cumulGainsFromTopPct),
    )
    .sort((a, b) => a.bandLower - b.bandLower);

  warnIfSignificantDataLoss("cgt-concentration", mapped.length, filtered.length);

  return filtered;
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

/**
 * Additive view toggle. Defaults to "bands" so the existing dual-axis view is
 * unchanged on first load; the concentration-curve (Lorenz) view is strictly
 * opt-in (config defaults stay OFF / backward-compatible).
 */
const views: Tab[] = [
  { id: "bands", label: "By gain band" },
  { id: "curve", label: "Concentration curve" },
];
const activeView = ref<"bands" | "curve">("bands");

const option = computed(() => {
  const data = sortedData.value;
  const labels = data.map((d) => d.gainBand);
  const shareValues = data.map((d) => d.shareOfGainsPct);
  const cumulValues = data.map((d) => d.cumulGainsFromTopPct);

  return {
    animation: !prefersReducedMotion,
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
        smooth: !prefersReducedMotion,
        lineStyle: { width: 2.5, color: COLOR_LINE },
        itemStyle: { color: COLOR_LINE },
        symbol: "circle",
        symbolSize: 6,
      },
    ],
  };
});

/**
 * Concentration-curve (Lorenz) points.
 *
 * DATA INTEGRITY: both coordinates are taken VERBATIM from the data file —
 * x = cumul_taxpayers_from_top_pct, y = cumul_gains_from_top_pct. Nothing is
 * computed, smoothed, interpolated, or fabricated here.
 *
 * Orientation: these columns are cumulative measured FROM THE TOP band down, so
 * the top (largest-gain) band has the smallest cumulative taxpayer share and a
 * large cumulative gains share, and the bottom band reaches ~100/100. We order
 * the points by cumulative taxpayer share ascending (top band first) so the
 * curve runs left-to-right from the most concentrated point toward (100, 100).
 * Because both axes count from the top, the curve sits ABOVE the y=x equality
 * line (the more concentrated the gains, the higher it bulges) — the mirror
 * image of a conventional bottom-up Lorenz curve, which sits below.
 *
 * >100 rounding artifact: per-band shares are rounded before the cumulative
 * sums are taken, so the bottom band's cumulative totals can round slightly
 * above 100 (e.g. 100.1 / 100.6). We clamp ONLY the plotted coordinate to 100
 * for display so the curve does not run off the 0–100 axes; the raw, unclamped
 * value is preserved verbatim in the accessible data table below. We never clamp
 * silently — see clampPct() and the table, which always shows the real figure.
 */
const CLAMP_MAX = 100;
function clampPctForDisplay(v: number): number {
  // Clamp ONLY the >100 rounding artifact for plotting; the table keeps the raw
  // value. Note: more than one near-100 band can clamp to the same (100, 100)
  // corner and so plot as coincident points — that is expected, and the raw,
  // distinct figures remain visible in the accessible data table below.
  return v > CLAMP_MAX ? CLAMP_MAX : v;
}

const curvePoints = computed(() => {
  return sortedData.value
    .map((d) => ({
      gainBand: d.gainBand,
      // Raw, verbatim values (used for the table + tooltip text).
      taxpayersFromTop: d.cumulTaxpayersFromTopPct,
      gainsFromTop: d.cumulGainsFromTopPct,
    }))
    // Drop any band whose cumulative figures are missing/non-finite (the real
    // data has a band with a null taxpayer count) so we never plot a fabricated
    // point. Such a band still appears in the default "by gain band" view.
    .filter(
      (p) =>
        Number.isFinite(p.taxpayersFromTop) && Number.isFinite(p.gainsFromTop),
    )
    // Order from the top band (small cumulative taxpayer share) downwards.
    .sort((a, b) => a.taxpayersFromTop - b.taxpayersFromTop);
});

const hasCurveData = computed(() => curvePoints.value.length > 0);

/** ECharts option for the concentration curve (numeric x/y, with equality line). */
const curveOption = computed(() => {
  const pts = curvePoints.value;
  // [x, y] pairs; x and y are the verbatim cumulative shares, clamped only for
  // the >100 rounding artifact so the line stays within the 0–100 plot box.
  const seriesData = pts.map((p) => [
    clampPctForDisplay(p.taxpayersFromTop),
    clampPctForDisplay(p.gainsFromTop),
  ]);

  return {
    animation: !prefersReducedMotion,
    title: {
      text: "Capital gains concentration curve",
      left: "center",
      textStyle: {
        fontSize: 16,
        fontWeight: "bold",
        color: "#111827",
      },
    },
    tooltip: {
      trigger: "item" as const,
      formatter: (params: { dataIndex: number }) => {
        const p = pts[params.dataIndex];
        if (!p) return "";
        // Show the raw, verbatim values in the tooltip (not the clamped ones).
        return (
          `<strong>${escapeHtml(p.gainBand)} or more</strong><br/>` +
          `Cumulative taxpayers from top: ${escapeHtml(p.taxpayersFromTop.toFixed(1))}%<br/>` +
          `Cumulative gains from top: ${escapeHtml(p.gainsFromTop.toFixed(1))}%`
        );
      },
    },
    legend: {
      bottom: 0,
      data: ["Concentration curve", "Equality line (y = x)"],
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
      type: "value" as const,
      name: "Cumulative share of taxpayers, from top (%)",
      nameLocation: "middle" as const,
      nameGap: 32,
      min: 0,
      max: 100,
      axisLabel: {
        color: "#374151",
        formatter: "{value}%",
      },
    },
    yAxis: {
      type: "value" as const,
      name: "Cumulative share of gains, from top (%)",
      nameLocation: "middle" as const,
      nameGap: 50,
      min: 0,
      max: 100,
      axisLabel: {
        color: "#374151",
        formatter: "{value}%",
      },
    },
    series: [
      {
        name: "Concentration curve",
        type: "line" as const,
        data: seriesData,
        // No smoothing: keep the curve faithful to the actual data points.
        smooth: false,
        lineStyle: { width: 2.5, color: COLOR_CURVE },
        itemStyle: { color: COLOR_CURVE },
        symbol: "circle",
        symbolSize: 7,
      },
      {
        // Static y=x equality reference line. This is a FIXED reference, not
        // derived from the data; it marks where gains would be perfectly evenly
        // distributed across taxpayers. Dashed + labelled so it is distinct
        // from the data curve without relying on colour alone (WCAG 1.4.1).
        name: "Equality line (y = x)",
        type: "line" as const,
        data: [
          [0, 0],
          [100, 100],
        ],
        showSymbol: false,
        lineStyle: { width: 1.5, color: COLOR_EQUALITY, type: "dashed" as const },
        itemStyle: { color: COLOR_EQUALITY },
        silent: true,
      },
    ],
  };
});

/** Column headers for the concentration-curve accessible data-table fallback. */
const curveTableColumns = [
  "Gain band (or more)",
  "Cumulative taxpayers from top (%)",
  "Cumulative gains from top (%)",
];

/**
 * One row per gain band for the AccessibleDataTable fallback (WCAG 1.1.1).
 * Mirrors EXACTLY the verbatim cumulative values from the data file — including
 * any >100 rounding artifact — with no calculation, clamping, or alteration.
 */
const curveTableRows = computed<DatasetRow[]>(() => {
  return curvePoints.value.map((p) => ({
    "Gain band (or more)": p.gainBand,
    "Cumulative taxpayers from top (%)": p.taxpayersFromTop,
    "Cumulative gains from top (%)": p.gainsFromTop,
  }));
});

/**
 * Descriptive aria-label for the concentration-curve view (role=img). Reads the
 * most-concentrated point (top band) straight from the data so screen-reader
 * users get the same headline the curve conveys. No derived statistics.
 */
const curveAriaLabel = computed(() => {
  const pts = curvePoints.value;
  if (pts.length === 0) {
    return "Concentration curve of capital gains against taxpayers.";
  }
  const top = pts[0];
  return (
    `Concentration curve plotting the cumulative share of capital gains against ` +
    `the cumulative share of taxpayers, both measured from the top down. ` +
    `The curve sits above the y-equals-x equality line, showing gains are ` +
    `concentrated: the top ${top.taxpayersFromTop.toFixed(1)}% of taxpayers ` +
    `(those in the "${top.gainBand} or more" band) account for ` +
    `${top.gainsFromTop.toFixed(1)}% of all gains. A dashed equality line marks ` +
    `where gains would be evenly distributed.`
  );
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
    <!--
      Additive view toggle. The "bands" tab is selected by default, so the
      original dual-axis bar + line view renders unchanged on first load; the
      concentration-curve (Lorenz) view is opt-in.
    -->
    <TabGroup v-model:active-id="activeView" :tabs="views">
      <template #bands>
        <div
          role="img"
          :aria-label="`Dual-axis chart showing capital gains concentration by gain band. ${headlineInsight}. Bars show each band's share of total gains; red line shows cumulative concentration from the top.`"
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
      </template>

      <template #curve>
        <div v-if="!hasCurveData" class="py-10 text-center" role="status">
          <p class="text-[var(--wl-ink-muted)] text-lg">
            No concentration-curve data available for this chart.
          </p>
        </div>
        <template v-else>
          <div role="img" :aria-label="curveAriaLabel" class="w-full">
            <VChart
              class="w-full"
              style="height: 480px"
              :option="curveOption"
              autoresize
            />
          </div>

          <!-- Accessible data-table fallback (WCAG 1.1.1 non-text content). -->
          <AccessibleDataTable
            :rows="curveTableRows"
            :columns="curveTableColumns"
            :numeric-columns="[
              'Cumulative taxpayers from top (%)',
              'Cumulative gains from top (%)',
            ]"
            caption="UK capital gains concentration: cumulative share of taxpayers and of gains, measured from the top gain band down. Values verbatim from HMRC Capital Gains Tax Statistics; bottom-band totals may round slightly above 100%."
          />
        </template>
      </template>
    </TabGroup>

    <!-- Source citation -->
    <p class="text-sm text-[var(--wl-ink-muted)] mt-4 text-center">
      Source:
      <a
        href="https://www.gov.uk/government/statistics/capital-gains-tax-statistics"
        target="_blank"
        rel="noopener"
        class="underline hover:text-[var(--wl-ink)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--wl-red)] rounded"
      >
        HMRC Capital Gains Tax Statistics<span class="sr-only"> (opens in new tab)</span></a>, accessed 2026-05-14
    </p>
  </div>
</template>
