<script setup lang="ts">
/**
 * ChildPovertyChart : Horizontal bar chart showing child poverty rates
 * by UK region, with a reference line for the national average.
 *
 * Data source: DWP HBAI tables 4.16ts and 4.17ts, AHC, three-year average
 * Columns: region, child_poverty_pct, children_in_poverty, national_avg_pct, above_national_avg
 *
 * Accessibility: WCAG AA high-contrast colors, aria-label, keyboard tooltip.
 */
import { computed, onMounted, ref } from "vue"
import { useDataStore } from "@/stores/data"
import type { DatasetMetadataResponse } from "@/types/api"
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
import { useChartTheme } from "@/composables/useChartTheme"
import { useChartData } from "@/composables/useChartData"
import type { EChartsExportable } from "@/composables/useChartExport"
import { escapeHtml, safeMinMax, toNumberOrNaN, warnIfSignificantDataLoss } from "@/utils/chart"
import AccessibleDataTable from "@/components/AccessibleDataTable.vue"
import childPovertySource from "../../public/data/child-poverty-metadata.json"

const { colors, axisStyle, markColor } = useChartTheme()

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

// Use the existing metadata provenance contract; missing evidence fails closed.
type ChildPovertyMetadata = DatasetMetadataResponse &
  Partial<Pick<typeof childPovertySource, "download_url" | "tables" | "period" | "measure">>
const metadata = ref<ChildPovertyMetadata | null>(null)
const dataStore = useDataStore()
const caveat = computed(() => {
  if (metadata.value?.data_type === "illustrative_fallback") {
    return "Illustrative legacy data. Its measure, period and source are unverified."
  }
  // Require the same checked source evidence from API and static responses.
  const evidenceMatches = (["download_url", "tables", "period", "measure"] as const).every(
    (field) =>
      JSON.stringify(metadata.value?.[field]) === JSON.stringify(childPovertySource[field]),
  )
  if (
    evidenceMatches &&
    ["live_ons", "static_published"].includes(metadata.value?.data_type ?? "") &&
    metadata.value?.source_url === childPovertySource.source_url &&
    metadata.value?.source === childPovertySource.source &&
    metadata.value?.description === childPovertySource.description &&
    metadata.value?.access_date === childPovertySource.access_date
  )
    return ""
  return "Unverified provenance. These figures have not been verified as official AHC statistics."
})
onMounted(async () => {
  try {
    metadata.value = await dataStore.fetchMetadata("child-poverty")
  } catch {
    // Retain the caveat when metadata is unavailable.
  }
})

/**
 * Respect prefers-reduced-motion (WCAG 2.3.3).
 */
const prefersReducedMotion =
  typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches

// WCAG AA high-contrast colors
const COLOR_ABOVE_AVG = "#b91c1c" // Red-700 : ~5.7:1 (above national avg)
const COLOR_BELOW_AVG = "#1a56db" // Blue : ~7.2:1 (below national avg)
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
  // 0 : the markLine self-hides, the table shows a missing-value marker, and the aria-label below
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
 * Accessible data-table fallback (WCAG 1.1.1). Mirrors the plotted series : the
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
    // null lets the table render a missing-value marker, keeping the visual and the fallback honest.
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

/** Visible and screen-reader copy share the same measure and provenance. */
const tableCaption = computed(
  () =>
    "Child poverty rate (%) by UK region after housing costs (AHC), " +
    "2021/22 to 2023/24 (three-year average). Counts are survey estimates rounded " +
    "to the nearest hundred thousand. The UK reference covers the same period. " +
    (caveat.value
      ? caveat.value
      : `Source: ${metadata.value?.source}, ${childPovertySource.download_url}, accessed ${metadata.value?.access_date}.`),
)

const option = computed(() => {
  const data = chartData.value

  return {
    animation: !prefersReducedMotion,
    textStyle: { color: colors.value.text },
    title: {
      text: "Child Poverty by UK Region (AHC)",
      left: "center",
      textStyle: {
        fontSize: 16,
        fontWeight: "bold",
        color: colors.value.heading,
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
      ...axisStyle.value,
      type: "value" as const,
      name: "Child poverty rate after housing costs (%)",
      nameLocation: "middle" as const,
      nameGap: 30,
      axisLabel: {
        color: colors.value.text,
        formatter: "{value}%",
      },
      max: data.values.length > 0 ? Math.ceil((Math.max(...data.values) * 1.1) / 5) * 5 : 45,
    },
    yAxis: {
      ...axisStyle.value,
      type: "category" as const,
      data: [...data.regions].reverse(),
      axisLabel: {
        color: colors.value.text,
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
            color: markColor(
              data.aboveAvg[data.regions.length - 1 - i] ? COLOR_ABOVE_AVG : COLOR_BELOW_AVG,
            ),
          },
        })),
        barMaxWidth: 24,
        markLine: data.nationalAvg
          ? {
              silent: true,
              symbol: "none",
              lineStyle: {
                color: markColor(COLOR_NATIONAL_AVG),
                type: "dashed" as const,
                width: 2,
              },
              data: [
                {
                  xAxis: data.nationalAvg,
                  label: {
                    color: colors.value.text,
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
      :aria-label="`Bar chart showing child poverty rates across ${chartData.regions.length} UK regions. Rates range from ${povertyRange.min}% to ${povertyRange.max}%.${Number.isFinite(chartData.nationalAvg) ? ` The national average is ${chartData.nationalAvg}%.` : ''} Regions above the national average are highlighted in red. After housing costs, 2021/22 to 2023/24 (three-year average). ${caveat}`"
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

    <p v-if="caveat" role="note" class="text-sm text-[var(--wl-ink-muted)] mt-4">
      {{ caveat }}
    </p>

    <!-- Source citation -->
    <p v-if="!caveat && metadata" class="text-sm text-[var(--wl-ink-muted)] mt-4 text-center">
      Source:
      <a
        :href="childPovertySource.download_url"
        target="_blank"
        rel="noopener"
        class="underline hover:text-[var(--wl-ink)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--wl-red)] rounded"
      >
        {{ metadata.source }}<span class="sr-only"> (opens in new tab)</span></a
      >, accessed {{ metadata.access_date }}. After housing costs, 2021/22 to 2023/24 (three-year
      average).
    </p>
  </div>
</template>
