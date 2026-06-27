<script setup lang="ts">
/**
 * ChildPovertyChart — Horizontal bar chart showing child poverty rates
 * by UK region, with a reference line for the national average.
 *
 * Data source: DWP/HMRC Children in Low Income Families (local-area statistics)
 * Columns: region, child_poverty_pct, children_in_poverty, national_avg_pct, above_national_avg
 *
 * Accessibility: WCAG AA high-contrast colors, aria-label, keyboard tooltip.
 */
import { computed, ref } from "vue"
import { use } from "echarts/core"
import { CanvasRenderer } from "echarts/renderers"
import { BarChart } from "echarts/charts"
import {
  GridComponent,
  TooltipComponent,
  TitleComponent,
  LegendComponent,
  MarkLineComponent,
} from "echarts/components"
import VChart from "vue-echarts"
import { useChartData } from "@/composables/useChartData"
import type { EChartsExportable } from "@/composables/useChartExport"
import { escapeHtml, safeMinMax, toNumberOrNaN, warnIfSignificantDataLoss } from "@/utils/chart"
import AccessibleDataTable from "@/components/AccessibleDataTable.vue"

// Register only the ECharts modules we need (tree-shaking)
use([
  CanvasRenderer,
  BarChart,
  GridComponent,
  TooltipComponent,
  TitleComponent,
  LegendComponent,
  MarkLineComponent,
])

const { rows, loading, error } = useChartData("child-poverty")
const chart = ref<EChartsExportable | null>(null)

defineExpose({ chart })

/**
 * Respect prefers-reduced-motion (WCAG 2.3.3).
 */
const prefersReducedMotion =
  typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches

// WCAG AA high-contrast colors
const COLOR_ABOVE_AVG = "#b91c1c" // Red-700 — ~5.7:1 (above national avg)
const COLOR_BELOW_AVG = "#1a56db" // Blue — ~7.2:1 (below national avg)
const COLOR_NATIONAL_AVG = "#374151" // Dark gray for reference line

/** Sorted data extracted from rows (sorted by poverty rate descending). */
const chartData = computed(() => {
  const mapped = rows.value.map((r) => ({
    region: String(r.region ?? ""),
    povertyPct: toNumberOrNaN(r.child_poverty_pct),
    childrenInPoverty: toNumberOrNaN(r.children_in_poverty),
    aboveAvg: Boolean(r.above_national_avg),
  }))
  const sorted = mapped
    .filter((r) => r.region && !isNaN(r.povertyPct))
    .sort((a, b) => b.povertyPct - a.povertyPct)

  warnIfSignificantDataLoss("child-poverty", mapped.length, sorted.length)

  // Extract national average from the first row (all rows have same value).
  // toNumberOrNaN (not bare Number) so a missing value is NaN, not a fabricated
  // 0 — the markLine self-hides, the table shows "—", and the aria-label below
  // omits the sentence rather than reading "NaN%".
  const nationalAvg = rows.value.length > 0 ? toNumberOrNaN(rows.value[0].national_avg_pct) : NaN

  return {
    regions: sorted.map((r) => r.region),
    values: sorted.map((r) => r.povertyPct),
    children: sorted.map((r) => r.childrenInPoverty),
    aboveAvg: sorted.map((r) => r.aboveAvg),
    nationalAvg,
  }
})

/** True when the API returned actual data to display. */
const hasData = computed(() => chartData.value.regions.length > 0)

/** Poverty rate range for aria-label. */
const povertyRange = computed(() => safeMinMax(chartData.value.values))

/**
 * Accessible data-table fallback (WCAG 1.1.1). Mirrors the plotted series — the
 * child-poverty rate per region (same already-loaded, filtered, poverty-rate-
 * descending order the bars use) plus the children-in-poverty count shown in the
 * tooltip and the national-average reference line the chart draws. Figures are
 * verbatim: it reuses chartData, never re-fetching or recomputing.
 */
const tableColumns = ["Region", "Child poverty (%)", "Children in poverty", "National average (%)"]
const tableNumericColumns = tableColumns.filter((c) => c !== "Region")
const tableRows = computed(() => {
  const d = chartData.value
  return d.regions.map((region, i) => {
    // Re-derive the children-in-poverty count from the raw row so a missing
    // source value (null/undefined/"") stays missing instead of becoming 0.
    // chartData parses it with Number(), and Number(null)===0 / Number("")===0,
    // which would otherwise make AccessibleDataTable render "0" (claiming zero
    // children in poverty) where the tooltip honestly shows "N/A". Mapping to
    // null lets the table render "—", keeping the visual and the fallback honest.
    const rawRow = rows.value.find((r) => String(r.region ?? "") === region)
    const rawChildren = rawRow?.children_in_poverty
    const children: number | null =
      rawChildren === null || rawChildren === undefined || rawChildren === ""
        ? null
        : Number(rawChildren)
    return {
      Region: region,
      "Child poverty (%)": d.values[i],
      "Children in poverty": children,
      "National average (%)": d.nationalAvg,
    }
  })
})

/**
 * Table caption — cites the same registered source the chart's footer credits
 * (DWP/HMRC Children in Low Income Families, matching registries/sources.yml and
 * the backend metadata) and notes the children-in-poverty counts are estimates
 * (the tooltip prefixes them with "~"), so the accessible fallback is as honest
 * as the visual and points at the same dataset.
 */
const tableCaption =
  "Child poverty rate (%) by UK region, with the estimated number of children in poverty and the UK national-average rate (%). Source: DWP/HMRC Children in Low Income Families. Children-in-poverty figures are estimates."

const option = computed(() => {
  const data = chartData.value

  return {
    animation: !prefersReducedMotion,
    title: {
      text: "Child Poverty Rate by UK Region",
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
        params: Array<{ seriesName: string; value: number; name: string; dataIndex: number }>,
      ) => {
        if (!Array.isArray(params) || params.length === 0) return ""
        const p = params[0]
        const idx = data.regions.length - 1 - p.dataIndex
        const children = data.children[idx]
        const childrenStr = children ? children.toLocaleString() : "N/A"
        return `<strong>${escapeHtml(String(p.name))}</strong><br/>Child poverty rate: ${p.value}%<br/>Children in poverty: ~${escapeHtml(childrenStr)}`
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
      name: "Child poverty rate (%)",
      nameLocation: "middle" as const,
      nameGap: 30,
      axisLabel: {
        color: "#374151",
        formatter: "{value}%",
      },
      max: data.values.length > 0 ? Math.ceil((Math.max(...data.values) * 1.1) / 5) * 5 : 45,
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
        name: "Child poverty rate",
        type: "bar" as const,
        data: [...data.values].reverse().map((val, i) => ({
          value: val,
          itemStyle: {
            color: data.aboveAvg[data.regions.length - 1 - i] ? COLOR_ABOVE_AVG : COLOR_BELOW_AVG,
          },
        })),
        barMaxWidth: 24,
        markLine: data.nationalAvg
          ? {
              silent: true,
              symbol: "none",
              lineStyle: { color: COLOR_NATIONAL_AVG, type: "dashed" as const, width: 2 },
              data: [
                {
                  xAxis: data.nationalAvg,
                  label: {
                    formatter: `UK avg: ${data.nationalAvg}%`,
                    position: "end" as const,
                  },
                },
              ],
            }
          : undefined,
      },
    ],
  }
})
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
    <p class="text-[var(--wl-ink-muted)] text-lg">No data available for this chart.</p>
  </div>

  <!-- Chart -->
  <div v-else>
    <div
      role="img"
      :aria-label="`Bar chart showing child poverty rates across ${chartData.regions.length} UK regions. Rates range from ${povertyRange.min}% to ${povertyRange.max}%.${Number.isFinite(chartData.nationalAvg) ? ` The national average is ${chartData.nationalAvg}%.` : ''} Regions above the national average are highlighted in red.`"
      class="w-full"
    >
      <VChart ref="chart" class="w-full" style="height: 520px" :option="option" autoresize />
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
        href="https://www.gov.uk/government/statistics/children-in-low-income-families-local-area-statistics-2014-to-2023"
        target="_blank"
        rel="noopener"
        class="underline hover:text-[var(--wl-ink)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--wl-red)] rounded"
      >
        DWP/HMRC Children in Low Income Families<span class="sr-only"> (opens in new tab)</span></a
      >, accessed 2026-05-16
    </p>
  </div>
</template>
