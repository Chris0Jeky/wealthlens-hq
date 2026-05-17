<script setup lang="ts">
/**
 * GenerationalWealthChart — Grouped bar chart showing median wealth
 * at key age milestones by generation (Baby Boomers, Gen X, Millennials).
 *
 * Data source: ONS Wealth and Assets Survey / Resolution Foundation
 * Columns: generation, birth_years, age_milestone, median_wealth_gbp,
 *          year_measured, projected
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
import { escapeHtml, safeMinMax, warnIfSignificantDataLoss } from "@/utils/chart";

// Register only the ECharts modules we need (tree-shaking)
use([
  CanvasRenderer,
  BarChart,
  GridComponent,
  TooltipComponent,
  TitleComponent,
  LegendComponent,
]);

const { rows, loading, error } = useChartData("generational-wealth");
const chart = ref<EChartsExportable | null>(null);

defineExpose({ chart });

/**
 * Respect prefers-reduced-motion (WCAG 2.3.3).
 */
const prefersReducedMotion =
  typeof window !== "undefined" &&
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// WCAG AA high-contrast colors for each generation
const COLOR_BOOMERS = "#1a56db"; // Blue — ~7.2:1
const COLOR_GEN_X = "#047857"; // Green — ~5.5:1
const COLOR_MILLENNIALS = "#dc2626"; // Red — ~4.6:1

/** Structured data by generation and age milestone. */
const chartData = computed(() => {
  // Group by generation
  const generations = new Map<string, { age: number; wealth: number; projected: boolean }[]>();
  const generationOrder: string[] = [];
  let skippedRows = 0;

  for (const row of rows.value) {
    const gen = String(row.generation ?? "");
    const age = Number(row.age_milestone);
    const wealth = Number(row.median_wealth_gbp);
    const projected = Boolean(row.projected);

    if (!gen || isNaN(age) || isNaN(wealth)) {
      skippedRows++;
      continue;
    }

    if (!generations.has(gen)) {
      generations.set(gen, []);
      generationOrder.push(gen);
    }
    generations.get(gen)!.push({ age, wealth, projected });
  }

  warnIfSignificantDataLoss("generational-wealth", rows.value.length, rows.value.length - skippedRows);

  // Sort each generation by age
  for (const data of generations.values()) {
    data.sort((a, b) => a.age - b.age);
  }

  // Get all unique ages across all generations
  const allAges = new Set<number>();
  for (const data of generations.values()) {
    for (const d of data) allAges.add(d.age);
  }
  const ages = Array.from(allAges).sort((a, b) => a - b);

  return { generations, generationOrder, ages };
});

/** True when the API returned actual data to display. */
const hasData = computed(() => chartData.value.generationOrder.length > 0);

/** Wealth range for aria-label. */
const wealthRange = computed(() => {
  const allWealth: number[] = [];
  for (const data of chartData.value.generations.values()) {
    for (const d of data) allWealth.push(d.wealth);
  }
  return safeMinMax(allWealth);
});

/** Map generation to color. */
function genColor(gen: string): string {
  if (gen.includes("Boomer")) return COLOR_BOOMERS;
  if (gen.includes("X")) return COLOR_GEN_X;
  return COLOR_MILLENNIALS;
}

const option = computed(() => {
  const { generations, generationOrder, ages } = chartData.value;

  // Build series for each generation
  const series = generationOrder.map((gen) => {
    const genData = generations.get(gen) ?? [];
    const dataMap = new Map<number, { wealth: number; projected: boolean }>();
    for (const d of genData) {
      dataMap.set(d.age, { wealth: d.wealth, projected: d.projected });
    }

    const color = genColor(gen);
    const data = ages.map((age) => {
      const entry = dataMap.get(age);
      if (!entry) return null;
      return {
        value: entry.wealth,
        itemStyle: entry.projected
          ? { color, opacity: 0.5, borderWidth: 2, borderColor: color, borderType: "dashed" as const }
          : { color },
      };
    });

    return {
      name: gen,
      type: "bar" as const,
      data,
      barMaxWidth: 40,
    };
  });

  return {
    animation: !prefersReducedMotion,
    title: {
      text: "Median Wealth by Generation at Key Ages",
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
      formatter: (params: Array<{ seriesName: string; value: number | null; axisValue: string }>) => {
        if (!Array.isArray(params) || params.length === 0) return "";
        let html = `<strong>Age ${escapeHtml(String(params[0].axisValue))}</strong><br/>`;
        for (const p of params) {
          if (p.value == null) continue;
          const val = typeof p.value === "number"
            ? `£${p.value.toLocaleString()}`
            : String(p.value);
          html += `${escapeHtml(String(p.seriesName))}: ${escapeHtml(val)}<br/>`;
        }
        return html;
      },
    },
    legend: {
      bottom: 0,
      data: generationOrder,
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
      data: ages.map((a) => String(a)),
      name: "Age",
      nameLocation: "middle" as const,
      nameGap: 30,
      axisLabel: {
        color: "#374151",
      },
    },
    yAxis: {
      type: "value" as const,
      name: "Median wealth (£)",
      nameLocation: "middle" as const,
      nameGap: 60,
      axisLabel: {
        color: "#374151",
        formatter: (value: number) => `£${(value / 1000).toFixed(0)}k`,
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
      :aria-label="`Grouped bar chart showing median wealth by generation at key age milestones. Compares ${chartData.generationOrder.join(', ')} across ages ${chartData.ages.join(', ')}. Wealth values range from £${wealthRange.min.toLocaleString()} to £${wealthRange.max.toLocaleString()}. Faded bars indicate projected values.`"
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

    <!-- Note about projected data -->
    <p class="text-sm text-[var(--wl-ink-muted)] mt-2 text-center italic">
      Faded bars indicate projected or estimated values based on current trends.
    </p>

    <!-- Source citation -->
    <p class="text-sm text-[var(--wl-ink-muted)] mt-4 text-center">
      Source:
      <a
        href="https://www.resolutionfoundation.org/publications/"
        target="_blank"
        rel="noopener"
        class="underline hover:text-[var(--wl-ink)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--wl-red)] rounded"
      >
        Resolution Foundation / ONS Wealth and Assets Survey<span class="sr-only"> (opens in new tab)</span></a>, accessed 2026-05-14
    </p>
  </div>
</template>
