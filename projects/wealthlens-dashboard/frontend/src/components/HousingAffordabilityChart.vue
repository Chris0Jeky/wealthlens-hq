<script setup lang="ts">
/**
 * HousingAffordabilityChart — Multi-line chart showing house-price-to-earnings
 * ratios by region over time.
 *
 * Data source: ONS Housing Affordability
 * Columns: region, year, ratio (median affordability ratio)
 *
 * Accessibility: WCAG AA high-contrast colors, aria-label, escapeHtml tooltips.
 */
import { computed, ref } from "vue";
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

const { rows, loading, error } = useChartData("housing-affordability");
const chart = ref<EChartsExportable | null>(null);

defineExpose({ chart });

/**
 * Respect prefers-reduced-motion (WCAG 2.3.3).
 * Disables ECharts smooth lines and animations when the user has
 * requested reduced motion in their OS settings.
 */
const prefersReducedMotion =
  typeof window !== "undefined" &&
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;

/**
 * WCAG AA high-contrast colors against white (#fff).
 * Each has at least 4.5:1 contrast ratio.
 */
const REGION_COLORS = [
  "#1a56db", // Blue   — ~7.2:1
  "#dc2626", // Red    — ~4.6:1
  "#047857", // Green  — ~5.5:1
  "#7c3aed", // Purple — ~5.0:1
  "#b45309", // Amber  — ~4.7:1
  "#0e7490", // Cyan   — ~4.8:1
  "#be185d", // Pink   — ~5.2:1
  "#4338ca", // Indigo — ~7.0:1
];

/** Maximum number of region lines to display before grouping. */
const MAX_REGIONS = 8;

/** Group data by region, returning sorted region names and their series. */
const regionData = computed(() => {
  // Accumulate per region in a year-keyed Map so a repeated (region, year) is
  // coalesced (last row wins) — exactly how the series builder collapses
  // duplicates into its per-year `dataMap`. Materialising the table from this
  // same coalesced data keeps the accessible table and the plotted line in
  // lockstep (no extra/stale points for non-visual users).
  const byRegionMap = new Map<string, Map<number, number>>();

  for (const row of rows.value) {
    const region = String(row.region ?? "");
    // Coerce nullish/empty values to NaN BEFORE Number(), because Number(null)
    // and Number("") both return 0 — which would silently fabricate a "year 0"
    // or a 0 ratio. Mapping them to NaN lets the guard below drop the row from
    // BOTH the chart and the accessible table (a genuine numeric 0 still passes).
    const year =
      row.year == null || row.year === "" ? NaN : Number(row.year);
    const ratio =
      row.ratio == null || row.ratio === "" ? NaN : Number(row.ratio);
    if (!region || isNaN(year) || isNaN(ratio)) {
      continue;
    }

    if (!byRegionMap.has(region)) byRegionMap.set(region, new Map());
    byRegionMap.get(region)!.set(year, ratio);
  }

  // Count distinct (region, year) points kept, since duplicate years collapse.
  let keptPoints = 0;
  for (const yearMap of byRegionMap.values()) keptPoints += yearMap.size;
  warnIfSignificantDataLoss("housing-affordability", rows.value.length, keptPoints);

  // Materialise each region's coalesced data as a year-sorted array — the shape
  // the chart series, allYears, ratioRange and the accessible table all consume.
  const byRegion = new Map<string, { year: number; ratio: number }[]>();
  for (const [region, yearMap] of byRegionMap) {
    const data = Array.from(yearMap, ([year, ratio]) => ({ year, ratio }));
    data.sort((a, b) => a.year - b.year);
    byRegion.set(region, data);
  }

  // If too many regions, pick the ones with the highest latest ratio
  let regionNames = Array.from(byRegion.keys());
  let tooManyRegions = false;

  if (regionNames.length > MAX_REGIONS) {
    tooManyRegions = true;
    // Rank by latest ratio (descending) to show most unaffordable regions
    regionNames.sort((a, b) => {
      const aData = byRegion.get(a)!;
      const bData = byRegion.get(b)!;
      const aLatest = aData[aData.length - 1]?.ratio ?? 0;
      const bLatest = bData[bData.length - 1]?.ratio ?? 0;
      return bLatest - aLatest;
    });
    regionNames = regionNames.slice(0, MAX_REGIONS);
  }

  return { byRegion, regionNames, tooManyRegions };
});

/** Unique sorted years across all displayed regions. */
const allYears = computed(() => {
  const yearSet = new Set<number>();
  const { byRegion, regionNames } = regionData.value;
  for (const name of regionNames) {
    for (const d of byRegion.get(name) ?? []) {
      yearSet.add(d.year);
    }
  }
  return Array.from(yearSet).sort((a, b) => a - b);
});

const yearRange = computed(() => safeMinMax(allYears.value));

const hasData = computed(() => regionData.value.regionNames.length > 0);

/** Overall ratio range across all displayed regions (for aria-label). */
const ratioRange = computed(() => {
  const allRatios: number[] = [];
  const { byRegion, regionNames } = regionData.value;
  for (const name of regionNames) {
    for (const d of byRegion.get(name) ?? []) {
      allRatios.push(d.ratio);
    }
  }
  return safeMinMax(allRatios);
});

/**
 * Accessible data-table fallback (WCAG 1.1.1). Mirrors the plotted lines — one
 * row per region per year data point — using the same already-loaded, verbatim
 * figures and the same region/year ordering the chart draws.
 *
 * Faithfulness: we iterate `regionData.regionNames` (so when the chart truncates
 * to the top MAX_REGIONS least-affordable regions, the table drops the same
 * regions and keeps the same legend/series order) and, within each region, the
 * year-sorted entries from `byRegion` (which already passed the chart's
 * region/year/ratio guards AND had any duplicate (region, year) coalesced to a
 * single last-wins point, exactly as the line series does). The table therefore
 * shows EXACTLY the points the chart plots — no re-fetch, no extra/stale rows.
 *
 * "Year" is intentionally LEFT OUT of the numeric set so a calendar year renders
 * as "2008", not "2,008". "Price-to-earnings ratio" is locale-formatted via
 * tableNumericColumns; any non-finite value would render as "—" (it cannot occur
 * here because byRegion only holds rows that passed the chart's isNaN guards).
 */
const tableColumns = ["Region", "Year", "Price-to-earnings ratio"];
const tableNumericColumns = ["Price-to-earnings ratio"];
const tableRows = computed(() => {
  const { byRegion, regionNames } = regionData.value;
  // Iterate in the chart's region order; each region's entries are already
  // year-sorted inside regionData, so this reproduces the chart's plotting
  // order exactly.
  return regionNames.flatMap((region) =>
    (byRegion.get(region) ?? []).map((d) => ({
      Region: region,
      Year: d.year,
      "Price-to-earnings ratio": d.ratio,
    })),
  );
});

/**
 * Table caption — cites the same registered source the chart shows (ONS Housing
 * Affordability), so the accessible fallback carries the same provenance as the
 * visual chart. Notes the top-MAX_REGIONS truncation only when it applies.
 *
 * Geography is described as "England and Wales": the ONS lower-quartile/median
 * affordability dataset behind this chart covers English and Welsh regions only
 * (no Scotland or Northern Ireland series), so a non-visual reader of the table
 * gets the same coverage claim the plotted data supports.
 */
const tableCaption = computed(() => {
  const truncationNote = regionData.value.tooManyRegions
    ? ` Showing the top ${MAX_REGIONS} least-affordable regions (the same regions plotted).`
    : "";
  return `House price to workplace-based earnings ratio by region (England and Wales) and year.${truncationNote} Source: ONS Housing Affordability.`;
});

const option = computed(() => {
  const { byRegion, regionNames } = regionData.value;
  const years = allYears.value;

  // Build a year->ratio lookup for each region for aligned data
  const series = regionNames.map((region, idx) => {
    const dataMap = new Map<number, number>();
    for (const d of byRegion.get(region) ?? []) {
      dataMap.set(d.year, d.ratio);
    }
    // Align to the shared year axis; null for missing years
    const data = years.map((y) => dataMap.get(y) ?? null);
    const color = REGION_COLORS[idx % REGION_COLORS.length];

    return {
      name: region,
      type: "line" as const,
      data,
      smooth: !prefersReducedMotion,
      lineStyle: { width: 2.5, color },
      itemStyle: { color },
      symbol: "circle",
      symbolSize: 4,
      connectNulls: true,
    };
  });

  return {
    animation: !prefersReducedMotion,
    title: {
      text: "Housing Affordability — Price-to-Earnings Ratios by Region",
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
          const val =
            typeof p.value === "number" ? p.value.toFixed(1) : String(p.value);
          html += `${escapeHtml(String(p.seriesName))}: ${escapeHtml(val)}<br/>`;
        }
        return html;
      },
    },
    legend: {
      bottom: 0,
      type: "scroll" as const,
      data: regionNames,
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
      name: "Price-to-earnings ratio",
      nameLocation: "middle" as const,
      nameGap: 50,
      axisLabel: {
        color: "#374151",
      },
    },
    series,
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
      :aria-label="`Line chart showing house-price-to-earnings ratios by region from ${yearRange.min} to ${yearRange.max}. Ratios range from ${ratioRange.min.toFixed(1)} to ${ratioRange.max.toFixed(1)} across ${regionData.regionNames.length} regions.`"
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

    <!-- Note when regions are truncated -->
    <p
      v-if="regionData.tooManyRegions"
      class="text-sm text-[var(--wl-ink-muted)] mt-2 text-center italic"
    >
      Showing top {{ MAX_REGIONS }} least-affordable regions. Additional regions
      are available in the full dataset.
    </p>

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
        href="https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/ratioofhousepricetoworkplacebasedearningslowerquartileandmedian"
        target="_blank"
        rel="noopener"
        class="underline hover:text-[var(--wl-ink)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--wl-red)] rounded"
      >
        ONS Housing Affordability<span class="sr-only"> (opens in new tab)</span></a>, accessed 2026-05-14
    </p>
  </div>
</template>
