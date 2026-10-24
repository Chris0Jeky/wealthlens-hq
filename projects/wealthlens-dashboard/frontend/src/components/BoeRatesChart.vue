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
import { computed, onMounted, ref } from "vue"
import { use } from "echarts/core"
import { CanvasRenderer } from "echarts/renderers"
import { LineChart } from "echarts/charts"
import {
  GridComponent,
  TooltipComponent,
  TitleComponent,
  LegendComponent,
} from "echarts/components"
import VChart from "vue-echarts"
import { useChartData } from "@/composables/useChartData"
import type { EChartsExportable } from "@/composables/useChartExport"
import { escapeHtml, safeMinMax, toNumberOrNaN, warnIfSignificantDataLoss } from "@/utils/chart"
import AccessibleDataTable from "@/components/AccessibleDataTable.vue"
import { useDataStore } from "@/stores/data"
import { useChartTheme } from "@/composables/useChartTheme"

// Register only the ECharts modules we need (tree-shaking)
use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, TitleComponent, LegendComponent])

const { colors, axisStyle, markColor } = useChartTheme()
const props = withDefaults(defineProps<{ range?: string }>(), { range: "All" })
const { rows, loading, error } = useChartData("boe-rates", () => props.range)
const chart = ref<EChartsExportable | null>(null)

defineExpose({ chart })

// Reuse the embed's provenance rules and the existing chart caveat styling.
// Missing metadata must not imply that fallback-capable data is official.
const dataType = ref<string | null | undefined>(null)
const accessDate = ref("")
// Citation links come from the published metadata; until it loads (or if it
// fails) the two canonical landing pages are shown with no access date.
const FALLBACK_SOURCES = [
  {
    name: "Bank of England (IUMABEDR, monthly average)",
    url: "https://www.bankofengland.co.uk/boeapps/database/Bank-Rate.asp",
  },
  {
    name: "ONS CPI (D7G7)",
    url: "https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/d7g7/mm23",
  },
]
const sources = ref<{ name: string; url: string }[]>(FALLBACK_SOURCES)
const caveat = computed(() => {
  if (dataType.value === "illustrative_fallback") {
    return "Illustrative composite. Figures are worked examples, not published statistics."
  }
  if (dataType.value === "live_ons" || dataType.value === "static_published") return ""
  return "Unverified provenance. These figures have not been verified as official statistics."
})
const store = useDataStore()

onMounted(async () => {
  try {
    const meta = await store.fetchMetadata("boe-rates")
    dataType.value = meta.data_type
    accessDate.value = (meta.access_date ?? "").trim()
    const published = (meta.sources ?? []).filter((s) => s.name && /^https?:\/\//.test(s.url))
    if (published.length) sources.value = published
  } catch {
    // Keep the unverified caveat when metadata cannot be loaded.
  }
})

/**
 * Respect prefers-reduced-motion (WCAG 2.3.3).
 */
const prefersReducedMotion =
  typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches

// WCAG AA high-contrast colors
const COLOR_BANK_RATE = "#1a56db" // Blue — ~7.2:1
const COLOR_CPI = "#dc2626" // Red — ~4.6:1

/** Sorted data extracted from rows. */
const chartData = computed(() => {
  // toNumberOrNaN: treat null/undefined/empty-string/non-finite cells as missing
  // (NaN) rather than letting Number() fabricate a 0. Number(null) and Number("")
  // both === 0, which would otherwise plot/table a real-looking 0.0 for a blank
  // source cell. A genuine numeric 0 (e.g. a 0% rate) is preserved.
  const mapped = rows.value.map((r) => ({
    date: String(r.date ?? ""),
    bankRate: toNumberOrNaN(r.bank_rate),
    cpi: toNumberOrNaN(r.cpi_annual),
  }))
  const sorted = mapped
    .filter((r) => r.date && !isNaN(r.bankRate) && !isNaN(r.cpi))
    .sort((a, b) => a.date.localeCompare(b.date))

  warnIfSignificantDataLoss("boe-rates", mapped.length, sorted.length)

  return {
    dates: sorted.map((r) => {
      // Format date labels: extract year-month. Use UTC accessors so an ISO date
      // like "2008-01-01" (parsed as UTC midnight) yields the same YYYY-MM in
      // every timezone — local getMonth() would shift it a month behind UTC.
      const d = new Date(r.date)
      if (isNaN(d.getTime())) return r.date
      return `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, "0")}`
    }),
    bankRate: sorted.map((r) => r.bankRate),
    cpi: sorted.map((r) => r.cpi),
  }
})

/** True when the API returned actual data to display. */
const hasData = computed(() => chartData.value.dates.length > 0)

/** Bank rate range for aria-label. */
const rateRange = computed(() => safeMinMax(chartData.value.bankRate))

/** CPI range for aria-label. */
const cpiRange = computed(() => safeMinMax(chartData.value.cpi))

/**
 * Accessible data-table fallback (WCAG 1.1.1). Mirrors the two plotted line
 * series — Bank Rate and CPI annual inflation — using the same already-loaded,
 * filtered, verbatim figures the chart draws, in the same chronological order.
 * chartData.value.bankRate / .cpi are post-filter values produced by
 * toNumberOrNaN() (null/empty/non-numeric rate or CPI become NaN and are dropped
 * by the chart's own !isNaN filter), so the table never shows a row the chart
 * omitted, nor a fabricated 0 for a missing source cell. A genuine 0 is kept.
 */
const tableColumns = ["Date", "Bank rate (%)", "CPI annual (%)"]
const tableNumericColumns = ["Bank rate (%)", "CPI annual (%)"]
const tableRows = computed<Record<string, string | number>[]>(() => {
  const d = chartData.value
  return d.dates.map((date, i) => ({
    Date: date,
    "Bank rate (%)": d.bankRate[i],
    "CPI annual (%)": d.cpi[i],
  }))
})

const option = computed(() => {
  const data = chartData.value

  return {
    animation: !prefersReducedMotion,
    textStyle: { color: colors.value.text },
    title: {
      text: "Bank of England Base Rate vs CPI Inflation",
      left: "center",
      textStyle: {
        fontSize: 16,
        fontWeight: "bold",
        color: colors.value.heading,
      },
    },
    tooltip: {
      trigger: "axis" as const,
      axisPointer: { type: "cross" as const },
      formatter: (params: Array<{ seriesName: string; value: number; axisValue: string }>) => {
        if (!Array.isArray(params) || params.length === 0) return ""
        let html = `<strong>${escapeHtml(String(params[0].axisValue))}</strong><br/>`
        for (const p of params) {
          const val = typeof p.value === "number" ? p.value.toFixed(2) : String(p.value)
          html += `${escapeHtml(String(p.seriesName))}: ${escapeHtml(val)}%<br/>`
        }
        return html
      },
    },
    legend: {
      inactiveColor: colors.value.muted,
      bottom: 0,
      data: ["Bank Rate", "CPI Inflation"],
      textStyle: { color: colors.value.text },
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "12%",
      top: "15%",
      containLabel: true,
    },
    xAxis: {
      ...axisStyle.value,
      type: "category" as const,
      data: data.dates,
      name: "Date",
      nameLocation: "middle" as const,
      nameGap: 30,
      axisLabel: {
        color: colors.value.text,
        rotate: 45,
        interval: Math.max(0, Math.floor(data.dates.length / 12)),
      },
    },
    yAxis: {
      ...axisStyle.value,
      type: "value" as const,
      name: "Rate (%)",
      nameLocation: "middle" as const,
      nameGap: 40,
      axisLabel: {
        color: colors.value.text,
        formatter: "{value}%",
      },
    },
    series: [
      {
        name: "Bank Rate",
        type: "line" as const,
        data: data.bankRate,
        smooth: false,
        lineStyle: { width: 2.5, color: markColor(COLOR_BANK_RATE) },
        itemStyle: { color: markColor(COLOR_BANK_RATE) },
        symbol: "circle",
        symbolSize: 4,
      },
      {
        name: "CPI Inflation",
        type: "line" as const,
        data: data.cpi,
        smooth: !prefersReducedMotion,
        lineStyle: { width: 2.5, color: markColor(COLOR_CPI) },
        itemStyle: { color: markColor(COLOR_CPI) },
        symbol: "circle",
        symbolSize: 4,
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
      :aria-label="`Line chart showing Bank of England base rate and CPI inflation from ${chartData.dates[0]} to ${chartData.dates[chartData.dates.length - 1]}. Bank rate ranged from ${rateRange.min.toFixed(2)}% to ${rateRange.max.toFixed(2)}%. CPI inflation ranged from ${cpiRange.min.toFixed(1)}% to ${cpiRange.max.toFixed(1)}%. ${caveat}`"
      class="w-full"
    >
      <VChart ref="chart" class="w-full" style="height: 480px" :option="option" autoresize />
    </div>

    <!-- Accessible data-table fallback (WCAG 1.1.1 non-text content). -->
    <AccessibleDataTable
      :rows="tableRows"
      :columns="tableColumns"
      :numeric-columns="tableNumericColumns"
      :caption="`Monthly average of official Bank Rate (%) and CPI annual inflation rate (%) by date, in chronological order. Source: Bank of England (Bank Rate) and ONS (CPI). ${caveat}`"
    />

    <p v-if="caveat" role="note" class="text-xs text-[var(--wl-ink-muted)] mt-2 text-center italic">
      {{ caveat }}
    </p>

    <!-- Source citation: links and access date come from the dataset metadata. -->
    <p class="text-sm text-[var(--wl-ink-muted)] mt-4 text-center">
      Source:
      <template v-for="(s, i) in sources" :key="s.url">
        <template v-if="i > 0"> / </template>
        <a
          :href="s.url"
          target="_blank"
          rel="noopener"
          class="underline hover:text-[var(--wl-ink)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--wl-red)] rounded"
          >{{ s.name }}<span class="sr-only"> (opens in new tab)</span></a
        > </template
      ><template v-if="accessDate">, accessed {{ accessDate }}</template>
    </p>
  </div>
</template>
