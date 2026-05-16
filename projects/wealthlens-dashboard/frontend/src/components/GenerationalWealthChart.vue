<script setup lang="ts">
import { onMounted, ref } from "vue"
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
import { useDataStore, type DatasetRow } from "@/stores/data"

use([
  CanvasRenderer,
  LineChart,
  GridComponent,
  TooltipComponent,
  TitleComponent,
  LegendComponent,
])

const store = useDataStore()
const rows = ref<DatasetRow[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    rows.value = await store.fetchDataset("generational-wealth")
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Failed to load generational wealth data"
  } finally {
    loading.value = false
  }
})

const COLORS: Record<string, string> = {
  "Baby Boomers": "#dc2626",
  "Generation X": "#2563eb",
  "Millennials": "#059669",
}

const option = ref({})

import { computed } from "vue"

const hasData = computed(() => rows.value.length > 0)

const chartOption = computed(() => {
  const generations = [...new Set(rows.value.map((r) => r.generation as string))]

  const series = generations.map((gen) => {
    const genRows = rows.value
      .filter((r) => r.generation === gen)
      .sort((a, b) => Number(a.age_milestone) - Number(b.age_milestone))

    return {
      name: gen,
      type: "line" as const,
      data: genRows.map((r) => [Number(r.age_milestone), Number(r.median_wealth_gbp)]),
      smooth: true,
      lineStyle: {
        width: 2.5,
        color: COLORS[gen] ?? "#6b7280",
        type: genRows.some((r) => r.projected === "True") ? ("dashed" as const) : ("solid" as const),
      },
      itemStyle: { color: COLORS[gen] ?? "#6b7280" },
      symbol: "circle",
      symbolSize: 6,
    }
  })

  return {
    tooltip: {
      trigger: "axis" as const,
      formatter: (params: Array<{ seriesName: string; value: [number, number] }>) => {
        if (!Array.isArray(params) || params.length === 0) return ""
        let html = `<strong>Age ${params[0].value[0]}</strong><br/>`
        for (const p of params) {
          const val = p.value[1].toLocaleString("en-GB", { style: "currency", currency: "GBP", maximumFractionDigits: 0 })
          html += `${p.seriesName}: ${val}<br/>`
        }
        return html
      },
    },
    legend: {
      bottom: 0,
      data: generations,
      textStyle: { color: "#374151" },
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "12%",
      top: "10%",
      containLabel: true,
    },
    xAxis: {
      type: "value" as const,
      name: "Age",
      nameLocation: "middle" as const,
      nameGap: 30,
      min: 25,
      max: 65,
      axisLabel: { color: "#374151" },
    },
    yAxis: {
      type: "value" as const,
      name: "Median wealth (GBP)",
      nameLocation: "middle" as const,
      nameGap: 60,
      axisLabel: {
        color: "#374151",
        formatter: (v: number) => `£${(v / 1000).toFixed(0)}k`,
      },
    },
    series,
  }
})
</script>

<template>
  <div v-if="loading" class="flex items-center justify-center py-20">
    <p class="text-gray-500 text-lg">Loading chart data...</p>
  </div>

  <div v-else-if="error" class="py-10 text-center">
    <p class="text-red-600 font-medium">{{ error }}</p>
    <p class="text-gray-500 text-sm mt-2">
      Make sure the backend API is running on port 8000.
    </p>
  </div>

  <div v-else-if="!hasData" class="py-10 text-center">
    <p class="text-gray-500 text-lg">No data available for this chart.</p>
  </div>

  <div v-else>
    <div
      role="img"
      aria-label="Line chart showing median household wealth by generation at ages 30, 40, 50, and 60. Baby Boomers accumulated significantly more wealth at each milestone compared to Generation X and Millennials."
      class="w-full"
    >
      <VChart
        class="w-full"
        style="height: 480px"
        :option="chartOption"
        autoresize
      />
    </div>
    <p class="text-sm text-gray-500 mt-4 text-center">
      Source:
      <a
        href="https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/bulletins/totalwealthingreatbritain/latest"
        target="_blank"
        rel="noopener noreferrer"
        class="underline hover:text-gray-700"
      >Resolution Foundation / ONS Wealth and Assets Survey</a>,
      accessed 2026-05-16. Values in 2022 real-term GBP.
    </p>
  </div>
</template>
