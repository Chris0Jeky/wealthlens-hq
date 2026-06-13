<script setup lang="ts">
/**
 * InheritanceTaxChart: IHT liability in the UK, shown in two views.
 *
 * The component offers an additive tab toggle (default: the trend view, so
 * existing behaviour is unchanged):
 *   - "Trend" (default): donut showing 4.6% of estates pay IHT vs 95.4% that
 *     don't, plus a bar chart of the IHT liability rate over time (2016–2022).
 *   - "By estate size": a bar chart of IHT paid by estate-size band, which
 *     illustrates how concentrated the tax is in larger estates, plus an
 *     accessible data table of the same band rows.
 *
 * Data source: HMRC Inheritance Tax Statistics 2021-22, Table 12.1
 * URL: https://www.gov.uk/government/statistics/inheritance-tax-statistics
 * Accessed: 2026-05-16
 *
 * Accessibility: WCAG AA high-contrast colors, aria-label, keyboard tooltip,
 * an accessible tab group, and an AccessibleDataTable fallback for the band
 * view (WCAG 1.1.1 non-text content).
 */
import { computed, onMounted, ref } from "vue";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { PieChart, BarChart } from "echarts/charts";
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
import { escapeHtml } from "@/utils/chart";
import { fetchWithRetry } from "@/utils/fetchWithRetry";

// Register only the ECharts modules we need (tree-shaking)
use([
  CanvasRenderer,
  PieChart,
  BarChart,
  GridComponent,
  TooltipComponent,
  TitleComponent,
  LegendComponent,
]);

/** Shape of the static JSON data file. */
interface IhtData {
  meta: {
    source: string;
    url: string;
    accessed: string;
    notes: string;
  };
  summary: {
    total_deaths: number;
    estates_liable: number;
    liability_rate_pct: number;
    total_iht_revenue_bn: number;
    nil_rate_band: number;
    residence_nil_rate_band: number;
  };
  by_year: Array<{
    year: string;
    deaths: number;
    liable: number;
    rate_pct: number;
    revenue_bn: number;
  }>;
  by_estate_size: Array<{
    band: string;
    estates: number;
    tax_paid_m: number;
  }>;
}

const data = ref<IhtData | null>(null);
const loading = ref(true);
const error = ref<string | null>(null);

/**
 * Respect prefers-reduced-motion (WCAG 2.3.3).
 * Disables ECharts animations when the user has requested reduced motion.
 */
const prefersReducedMotion =
  typeof window !== "undefined" &&
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// WCAG AA colors — graphical objects require 3:1 minimum
// #b91c1c (red-700) contrast ~5.7:1 — IHT liable (accent)
// #1a56db (blue) contrast ~7.2:1 — not liable / bar fill
const COLOR_LIABLE = "#b91c1c";
const COLOR_NOT_LIABLE = "#1a56db";
const COLOR_BAR = "#1a56db";

const isFiniteNumber = (value: unknown): value is number =>
  typeof value === "number" && Number.isFinite(value);

const isValidIhtData = (value: unknown): value is IhtData => {
  if (typeof value !== "object" || value === null) return false;

  const candidate = value as Partial<IhtData>;
  const summary = candidate.summary;

  return (
    typeof candidate.meta?.source === "string" &&
    typeof candidate.meta.url === "string" &&
    typeof candidate.meta.accessed === "string" &&
    typeof candidate.meta.notes === "string" &&
    typeof summary === "object" &&
    summary !== null &&
    isFiniteNumber(summary.total_deaths) &&
    isFiniteNumber(summary.estates_liable) &&
    isFiniteNumber(summary.liability_rate_pct) &&
    isFiniteNumber(summary.total_iht_revenue_bn) &&
    isFiniteNumber(summary.nil_rate_band) &&
    isFiniteNumber(summary.residence_nil_rate_band) &&
    Array.isArray(candidate.by_year) &&
    candidate.by_year.length > 0 &&
    candidate.by_year.every(
      (row) =>
        typeof row.year === "string" &&
        isFiniteNumber(row.deaths) &&
        isFiniteNumber(row.liable) &&
        isFiniteNumber(row.rate_pct) &&
        isFiniteNumber(row.revenue_bn),
    ) &&
    Array.isArray(candidate.by_estate_size) &&
    candidate.by_estate_size.every(
      (row) =>
        typeof row.band === "string" &&
        isFiniteNumber(row.estates) &&
        isFiniteNumber(row.tax_paid_m),
    )
  );
};

onMounted(async () => {
  try {
    const baseUrl = import.meta.env.BASE_URL ?? "/";
    const res = await fetchWithRetry(`${baseUrl}data/inheritance-tax.json`, undefined, 0);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const parsed = await res.json();
    if (!isValidIhtData(parsed)) {
      throw new Error("Unexpected data format");
    }
    data.value = parsed;
  } catch (e) {
    error.value =
      e instanceof Error ? e.message : "Failed to load inheritance tax data";
  } finally {
    loading.value = false;
  }
});

/** Whether we have data to show. */
const hasData = computed(() => data.value !== null);

/**
 * Additive view toggle. Defaults to "trend" so the existing dual-panel trend
 * view is unchanged; the by-estate-size band view is strictly opt-in (config
 * defaults stay OFF / backward-compatible).
 */
const views: Tab[] = [
  { id: "trend", label: "Trend" },
  { id: "bands", label: "By estate size" },
];
const activeView = ref<string>("trend");

/** Donut chart option — 4.6% pay IHT vs 95.4% don't. */
const donutOption = computed(() => {
  if (!data.value) return {};
  const { liability_rate_pct } = data.value.summary;
  const notLiable = +(100 - liability_rate_pct).toFixed(1);

  return {
    animation: !prefersReducedMotion,
    title: {
      text: "Estates paying IHT",
      left: "center",
      top: 0,
      textStyle: {
        fontSize: 15,
        fontWeight: "bold",
        color: "#111827",
      },
    },
    tooltip: {
      trigger: "item" as const,
      formatter: (params: { name: string; value: number; percent: number }) => {
        return `${escapeHtml(params.name)}: ${params.value}%`;
      },
    },
    legend: {
      bottom: 0,
      data: ["Pay IHT", "Don't pay IHT"],
      textStyle: { color: "#374151" },
    },
    series: [
      {
        name: "IHT liability",
        type: "pie" as const,
        radius: ["45%", "75%"],
        center: ["50%", "50%"],
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 4,
          borderColor: "#fff",
          borderWidth: 2,
        },
        label: {
          show: true,
          fontSize: 14,
          fontWeight: "bold",
          formatter: "{b}\n{d}%",
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: "bold",
          },
        },
        data: [
          {
            value: liability_rate_pct,
            name: "Pay IHT",
            itemStyle: { color: COLOR_LIABLE },
          },
          {
            value: notLiable,
            name: "Don't pay IHT",
            itemStyle: { color: COLOR_NOT_LIABLE },
          },
        ],
      },
    ],
  };
});

/** Bar chart option — IHT liability rate by year. */
const barOption = computed(() => {
  if (!data.value) return {};
  const years = data.value.by_year.map((d) => d.year);
  const rates = data.value.by_year.map((d) => d.rate_pct);

  return {
    animation: !prefersReducedMotion,
    title: {
      text: "IHT liability rate over time",
      left: "center",
      top: 0,
      textStyle: {
        fontSize: 15,
        fontWeight: "bold",
        color: "#111827",
      },
    },
    tooltip: {
      trigger: "axis" as const,
      axisPointer: { type: "shadow" as const },
      formatter: (
        params: Array<{ seriesName: string; value: number; axisValue: string }>,
      ) => {
        if (!Array.isArray(params) || params.length === 0) return "";
        const p = params[0];
        return `<strong>${escapeHtml(String(p.axisValue))}</strong><br/>Liability rate: ${escapeHtml(String(p.value))}%`;
      },
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "10%",
      top: "18%",
      containLabel: true,
    },
    xAxis: {
      type: "category" as const,
      data: years,
      axisLabel: {
        color: "#374151",
        rotate: 30,
      },
    },
    yAxis: {
      type: "value" as const,
      name: "% of estates",
      nameLocation: "middle" as const,
      nameGap: 40,
      min: 0,
      max: 6,
      axisLabel: {
        color: "#374151",
        formatter: "{value}%",
      },
    },
    series: [
      {
        name: "Liability rate",
        type: "bar" as const,
        data: rates,
        itemStyle: { color: COLOR_BAR },
        barMaxWidth: 40,
        label: {
          show: true,
          position: "top" as const,
          formatter: "{c}%",
          fontSize: 12,
          color: "#374151",
        },
      },
    ],
  };
});

/**
 * Bar chart option: IHT paid by estate-size band (£ million).
 *
 * Values are taken verbatim from the data file's by_estate_size array
 * (tax_paid_m, in £ millions). No figures are computed or altered here.
 * Bars use the same high-contrast blue as the trend bar chart; the band
 * labels on the x-axis and the value labels on each bar mean the chart does
 * not rely on colour alone to convey meaning (WCAG 1.4.1).
 */
const bandOption = computed(() => {
  if (!data.value) return {};
  const bands = data.value.by_estate_size.map((d) => d.band);
  const taxPaid = data.value.by_estate_size.map((d) => d.tax_paid_m);

  return {
    animation: !prefersReducedMotion,
    title: {
      text: "IHT paid by estate size",
      left: "center",
      top: 0,
      textStyle: {
        fontSize: 15,
        fontWeight: "bold",
        color: "#111827",
      },
    },
    tooltip: {
      trigger: "axis" as const,
      axisPointer: { type: "shadow" as const },
      formatter: (
        params: Array<{ seriesName: string; value: number; axisValue: string }>,
      ) => {
        if (!Array.isArray(params) || params.length === 0) return "";
        const p = params[0];
        return `<strong>${escapeHtml(String(p.axisValue))}</strong><br/>IHT paid: £${escapeHtml(String(p.value))}m`;
      },
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "10%",
      top: "18%",
      containLabel: true,
    },
    xAxis: {
      type: "category" as const,
      data: bands,
      name: "Estate size band",
      nameLocation: "middle" as const,
      nameGap: 50,
      axisLabel: {
        color: "#374151",
        rotate: 30,
      },
    },
    yAxis: {
      type: "value" as const,
      name: "IHT paid (£m)",
      nameLocation: "middle" as const,
      nameGap: 55,
      min: 0,
      axisLabel: {
        color: "#374151",
        formatter: "£{value}m",
      },
    },
    series: [
      {
        name: "IHT paid",
        type: "bar" as const,
        data: taxPaid,
        itemStyle: { color: COLOR_BAR },
        barMaxWidth: 48,
        label: {
          show: true,
          position: "top" as const,
          formatter: "£{c}m",
          fontSize: 12,
          color: "#374151",
        },
      },
    ],
  };
});

/** Column headers for the by-estate-size accessible data-table fallback. */
const bandTableColumns = ["Estate size band", "Estates", "IHT paid (£m)"];

/**
 * One row per estate-size band for the AccessibleDataTable fallback
 * (WCAG 1.1.1). Mirrors exactly the values in the data file's by_estate_size
 * array, with no calculation or alteration. Numeric columns are
 * locale-formatted by the table component.
 */
const bandTableRows = computed<DatasetRow[]>(() => {
  if (!data.value) return [];
  return data.value.by_estate_size.map((d) => ({
    "Estate size band": d.band,
    Estates: d.estates,
    "IHT paid (£m)": d.tax_paid_m,
  }));
});

/**
 * Descriptive aria-label for the band view (role=img). Reads the first and
 * last band straight from the data, so screen-reader users get the same
 * top/bottom contrast the bars convey. No derived statistics.
 */
const bandAriaLabel = computed(() => {
  if (!data.value || data.value.by_estate_size.length === 0) {
    return "Bar chart of inheritance tax paid by estate size band.";
  }
  const rows = data.value.by_estate_size;
  const first = rows[0];
  const last = rows[rows.length - 1];
  return (
    `Bar chart of inheritance tax paid by estate size band, in pounds million. ` +
    `The "${first.band}" band covers ${first.estates.toLocaleString()} estates paying £${first.tax_paid_m}m. ` +
    `The "${last.band}" band covers ${last.estates.toLocaleString()} estates paying £${last.tax_paid_m}m.`
  );
});
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
      Could not load inheritance tax data. Check that the data file exists.
    </p>
  </div>

  <!-- No data state -->
  <div v-else-if="!hasData" class="py-10 text-center" role="status">
    <p class="text-[var(--wl-ink-muted)] text-lg">
      No data available for this chart.
    </p>
  </div>

  <!-- Charts -->
  <div v-else>
    <!--
      Additive view toggle. The "trend" tab is selected by default, so the
      original dual-panel trend view renders unchanged on first load; the
      by-estate-size band view is opt-in.
    -->
    <TabGroup v-model:active-id="activeView" :tabs="views">
      <template #trend>
        <div
          role="img"
          :aria-label="`Inheritance Tax chart. Only ${data!.summary.liability_rate_pct}% of UK estates are liable for IHT. In 2021-22, ${data!.summary.estates_liable.toLocaleString()} estates out of approximately ${data!.summary.total_deaths.toLocaleString()} deaths paid IHT, raising £${data!.summary.total_iht_revenue_bn} billion.`"
          class="w-full"
        >
          <!-- Dual panel layout -->
          <div class="iht-panels">
            <div class="iht-panel">
              <VChart
                class="w-full"
                style="height: 360px"
                :option="donutOption"
                autoresize
              />
            </div>
            <div class="iht-panel">
              <VChart
                class="w-full"
                style="height: 360px"
                :option="barOption"
                autoresize
              />
            </div>
          </div>
        </div>
      </template>

      <template #bands>
        <div role="img" :aria-label="bandAriaLabel" class="w-full">
          <VChart
            class="w-full"
            style="height: 420px"
            :option="bandOption"
            autoresize
          />
        </div>

        <!-- Accessible data-table fallback (WCAG 1.1.1 non-text content). -->
        <AccessibleDataTable
          :rows="bandTableRows"
          :columns="bandTableColumns"
          :numeric-columns="['Estates', 'IHT paid (£m)']"
          caption="UK inheritance tax by estate-size band, 2021-22: estates and IHT paid (£ million). Source: HMRC Inheritance Tax Statistics 2021-22, Table 12.1."
        />
      </template>
    </TabGroup>

    <!-- Source citation -->
    <p class="text-sm text-[var(--wl-ink-muted)] mt-4 text-center">
      Source:
      <a
        href="https://www.gov.uk/government/statistics/inheritance-tax-statistics"
        target="_blank"
        rel="noopener"
        class="underline hover:text-[var(--wl-ink)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--wl-red)] rounded"
      >
        HMRC Inheritance Tax Statistics 2021-22, Table
        12.1<span class="sr-only"> (opens in new tab)</span></a
      >, accessed 2026-05-16
    </p>
  </div>
</template>

<style scoped>
.iht-panels {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  width: 100%;
}

@media (max-width: 768px) {
  .iht-panels {
    grid-template-columns: 1fr;
  }
}
</style>
