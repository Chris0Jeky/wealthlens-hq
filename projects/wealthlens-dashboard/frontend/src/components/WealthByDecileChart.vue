<script setup lang="ts">
/**
 * WealthByDecileChart — Bar chart showing total household wealth by decile.
 *
 * Data source: ONS Wealth and Assets Survey
 * Columns: decile, total_wealth_bn (GBP billions)
 *
 * Any decile whose net wealth is negative is highlighted in a warning color;
 * all other bars use a standard WCAG AA compliant blue. (With the current ONS
 * data every decile's total wealth is positive, so no bar is highlighted — the
 * negative styling is a data-driven safeguard, not an assumption about a band.)
 *
 * Accessibility: WCAG AA high-contrast colors, aria-label, escapeHtml tooltips.
 */
import { computed, ref, useId } from "vue"
import { use } from "echarts/core"
import { CanvasRenderer } from "echarts/renderers"
import { BarChart } from "echarts/charts"
import { GridComponent, TooltipComponent, TitleComponent } from "echarts/components"
import VChart from "vue-echarts"
import { useChartData } from "@/composables/useChartData"
import type { EChartsExportable } from "@/composables/useChartExport"
import { escapeHtml, toNumberOrNaN, warnIfSignificantDataLoss } from "@/utils/chart"
import AccessibleDataTable from "@/components/AccessibleDataTable.vue"

// Register only the ECharts modules we need (tree-shaking)
use([CanvasRenderer, BarChart, GridComponent, TooltipComponent, TitleComponent])

const { rows, loading, error } = useChartData("wealth-by-decile")
const chart = ref<EChartsExportable | null>(null)

defineExpose({ chart })

// Stable id linking the chart's role="img" to its provenance caveat via
// aria-describedby, so the WAS under-reporting note is announced as part of the
// chart description (not just reachable later in the reading order).
const caveatId = useId()

/**
 * Respect prefers-reduced-motion (WCAG 2.3.3).
 * Disables ECharts animations when the user has requested reduced motion.
 */
const prefersReducedMotion =
  typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches

// WCAG AA high-contrast colors against white
// #1a56db (blue) contrast ratio ~7.2:1 — standard bars
// #b91c1c (red-700) contrast ratio ~5.7:1 — negative value warning
const COLOR_BAR = "#1a56db"
const COLOR_NEGATIVE = "#b91c1c"

/** Parsed data rows preserving CSV order (1st poorest to 10th richest). */
const parsedData = computed(() => {
  const mapped = rows.value.map((r) => ({
    decile: String(r.decile ?? ""),
    totalWealthBn: toNumberOrNaN(r.total_wealth_bn),
  }))
  const filtered = mapped.filter((r) => r.decile && !isNaN(r.totalWealthBn))

  warnIfSignificantDataLoss("wealth-by-decile", mapped.length, filtered.length)

  return filtered
})

const hasData = computed(() => parsedData.value.length > 0)

/** Build a headline insight for the aria-label. */
const headlineInsight = computed(() => {
  const data = parsedData.value
  if (data.length === 0) return ""
  const richest = data[data.length - 1]
  const poorest = data[0]
  if (!richest || !poorest) return ""
  return `The ${richest.decile} decile holds ${richest.totalWealthBn.toLocaleString()}bn in total wealth, while the ${poorest.decile} decile has ${poorest.totalWealthBn.toLocaleString()}bn`
})

/**
 * Only claim the "negative net wealth / red highlight" in the aria-label when the
 * poorest decile's value is actually negative. The committed ONS data is positive
 * (+£13.9bn), so the claim would otherwise describe a red bar that is never drawn.
 */
const poorestIsNegative = computed(() => {
  const poorest = parsedData.value[0]
  return poorest ? poorest.totalWealthBn < 0 : false
})

/**
 * Accessible data-table fallback (WCAG 1.1.1). Mirrors the single plotted series
 * — total household wealth (£bn) per decile — using the same already-loaded,
 * filtered, verbatim figures the chart draws, in the same poorest-to-richest order.
 */
const tableColumns = ["Decile", "Total wealth (£bn)"]
const tableNumericColumns = ["Total wealth (£bn)"]
const tableRows = computed(() =>
  parsedData.value.map((d) => ({
    Decile: d.decile,
    "Total wealth (£bn)": d.totalWealthBn,
  })),
)

const option = computed(() => {
  const data = parsedData.value
  const labels = data.map((d) => d.decile)
  const values = data.map((d) => d.totalWealthBn)

  // Color each bar: red for negative values, blue for positive
  const barColors = values.map((v) => (v < 0 ? COLOR_NEGATIVE : COLOR_BAR))

  return {
    animation: !prefersReducedMotion,
    title: {
      text: "Total Household Wealth by Decile (GBP Billions)",
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
          seriesName: string
          value: number
          axisValue: string
          dataIndex: number
        }>,
      ) => {
        if (!Array.isArray(params) || params.length === 0) return ""
        const p = params[0]
        const val = typeof p.value === "number" ? p.value.toFixed(1) : String(p.value)
        let html = `<strong>${escapeHtml(String(p.axisValue))}</strong><br/>`
        html += `Total wealth: ${escapeHtml(val)}bn`
        if (typeof p.value === "number" && p.value < 0) {
          html += `<br/><em style="color:${COLOR_NEGATIVE}">Net negative wealth</em>`
        }
        return html
      },
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
        rotate: 30,
      },
    },
    yAxis: {
      type: "value" as const,
      name: "Total wealth (GBP bn)",
      nameLocation: "middle" as const,
      nameGap: 60,
      axisLabel: {
        color: "#374151",
        formatter: (value: number) => `£${value.toLocaleString()}`,
      },
    },
    series: [
      {
        name: "Total wealth",
        type: "bar" as const,
        data: values.map((v, i) => ({
          value: v,
          itemStyle: { color: barColors[i] },
        })),
        barMaxWidth: 60,
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
      :aria-label="`Bar chart showing total household wealth by decile in Great Britain. ${headlineInsight}.${poorestIsNegative ? ' The poorest decile is highlighted in red to indicate net negative wealth.' : ''}`"
      :aria-describedby="caveatId"
      class="w-full"
    >
      <VChart ref="chart" class="w-full" style="height: 480px" :option="option" autoresize />
    </div>

    <!-- Accessible data-table fallback (WCAG 1.1.1 non-text content). -->
    <AccessibleDataTable
      :rows="tableRows"
      :columns="tableColumns"
      :numeric-columns="tableNumericColumns"
      caption="Total household wealth by decile in Great Britain (£bn), ordered from the poorest (1st) to the richest (10th) decile. Source: ONS Wealth and Assets Survey."
    />

    <!-- Source citation -->
    <p class="text-sm text-[var(--wl-ink-muted)] mt-4 text-center">
      Source:
      <a
        href="https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/bulletins/totalwealthingreatbritain/latest"
        target="_blank"
        rel="noopener"
        class="underline hover:text-[var(--wl-ink)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--wl-red)] rounded"
      >
        ONS Wealth and Assets Survey<span class="sr-only"> (opens in new tab)</span></a
      >, accessed 2026-05-15
    </p>

    <!-- Provenance caveat mandated by research/methodology/was-caveats.md: any
         WAS-sourced chart MUST flag that the survey lost accredited official
         statistics status (June 2025, OSR Report 396, on a response-rate fall
         66%->41%). Paired with the top-tail under-count note — household surveys
         miss the wealthiest few — so the chart is never read as a hard ceiling on
         top-decile wealth; the richest-vs-poorest gap is, if anything, wider. -->
    <p :id="caveatId" class="text-xs text-[var(--wl-ink-muted)] mt-2 text-center max-w-2xl mx-auto">
      Note: the Wealth and Assets Survey lost accredited official statistics status in June 2025
      (declining response rates), and household surveys under-record wealth at the very top — so the
      true gap between the richest and poorest deciles is likely wider than shown.
    </p>
  </div>
</template>
