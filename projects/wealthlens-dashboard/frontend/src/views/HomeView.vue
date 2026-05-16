<script setup lang="ts">
import { onMounted, computed, ref } from 'vue'
import { useDataStore } from '@/stores/data'
import DatasetCard from '@/components/DatasetCard.vue'
import ResponsiveGrid from '@/components/ResponsiveGrid.vue'
import NumberStat from '@/components/NumberStat.vue'
import { CHART_METADATA } from '@/utils/chartConstants'
import { SUPPORTED_CHART_NAMES } from '@/utils/chartConstants'

const store = useDataStore()

/** Local state for metadata enrichment (does not gate card rendering). */
const metadataLoading = ref(true)
const metadataError = ref<string | null>(null)

/** All 10 datasets in display order. */
const ALL_DATASETS = [
  'wealth-shares',
  'housing-affordability',
  'cgt-concentration',
  'wealth-by-decile',
  'productivity-pay',
  'gdhi-by-region',
  'tax-composition',
  'boe-rates',
  'child-poverty',
  'generational-wealth',
] as const

/** Fallback descriptions for datasets without chart metadata. */
const FALLBACK_DESCRIPTIONS: Record<string, string> = {
  'wealth-shares': 'Top 1% and 10% share of UK net personal wealth since 1820 (WID)',
  'housing-affordability': 'House price to earnings ratio by region, 1997-2025 (ONS)',
  'cgt-concentration': 'Capital gains concentration by size of gain (HMRC)',
  'wealth-by-decile': 'Total net wealth by decile group in Great Britain (ONS WAS)',
  'productivity-pay': 'Gap between productivity growth and median pay in the UK (ONS)',
  'gdhi-by-region': 'Gross disposable household income by UK region (ONS)',
  'tax-composition': 'Breakdown of UK tax receipts by source over time (HMRC/OBR)',
  'boe-rates': 'Bank of England base interest rate history (BoE)',
  'child-poverty': 'Children in relative poverty by UK region and nation (DWP)',
  'generational-wealth': 'Wealth distribution across generations in Great Britain (ONS WAS)',
}

/** Get description for a dataset from metadata or fallback. */
function getDescription(name: string): string {
  const meta = store.metadata.get(name)
  if (meta?.description) return meta.description
  const chart = Object.values(CHART_METADATA).find((c) => c.name === name)
  if (chart?.description) return chart.description
  return FALLBACK_DESCRIPTIONS[name] ?? 'UK inequality dataset'
}

/** Count of datasets with interactive charts. */
const chartCount = computed(() => SUPPORTED_CHART_NAMES.size)

/** Count of datasets to display. */
const datasetCount = computed(() => ALL_DATASETS.length)

onMounted(async () => {
  // Track both fetches with Promise.allSettled so neither silently fails
  const results = await Promise.allSettled([
    store.fetchDatasets(),
    store.fetchAllMetadata(),
  ])

  metadataLoading.value = false

  // Report metadata enrichment failure (non-blocking — fallback descriptions used)
  if (results[1].status === 'rejected') {
    metadataError.value = results[1].reason instanceof Error
      ? results[1].reason.message
      : 'Failed to load metadata'
  }
})
</script>

<template>
  <div class="max-w-6xl mx-auto px-6 py-10">
    <!-- Hero section -->
    <section class="mb-12" aria-labelledby="hero-heading">
      <h1 id="hero-heading" class="text-3xl font-bold mb-3">
        UK Wealth Inequality Dashboard
      </h1>
      <p class="text-[var(--wl-ink-muted)] max-w-2xl mb-2">
        Open-source, source-backed data on wealth inequality in the United
        Kingdom. Every chart cites its data source with URL and access date.
      </p>
      <p class="text-[var(--wl-ink-muted)] max-w-2xl text-sm">
        Making wealth data accessible, interactive, and impossible to ignore.
      </p>
    </section>

    <!-- Key statistics -->
    <section class="mb-12" aria-labelledby="stats-heading">
      <h2 id="stats-heading" class="sr-only">Key Statistics</h2>
      <div class="grid gap-4 sm:grid-cols-3">
        <NumberStat
          :value="String(datasetCount)"
          label="Datasets"
          description="Source-cited UK inequality datasets"
        />
        <NumberStat
          :value="String(chartCount)"
          label="Interactive Charts"
          description="Explorable visualisations with full data access"
        />
        <NumberStat
          value="Weekly"
          label="Update Frequency"
          description="Automated pipelines refresh data regularly"
        />
      </div>
    </section>

    <!-- Dataset cards section -->
    <section aria-labelledby="datasets-heading">
      <h2 id="datasets-heading" class="text-xl font-semibold mb-4">
        Available Datasets
      </h2>

      <!-- Metadata enrichment error (non-blocking) -->
      <div
        v-if="metadataError"
        role="status"
        class="rounded-lg border border-amber-300 dark:border-amber-700 bg-amber-50 dark:bg-amber-950 p-4 mb-4"
      >
        <p class="text-sm text-amber-800 dark:text-amber-200">
          Metadata enrichment unavailable — showing default descriptions.
        </p>
      </div>

      <!-- Dataset cards always render (hardcoded data, no API dependency) -->
      <ResponsiveGrid min-width="280px" gap="1.5rem" role="list">
        <div v-for="name in ALL_DATASETS" :key="name" role="listitem">
          <DatasetCard
            :name="name"
            :description="getDescription(name)"
          />
        </div>
      </ResponsiveGrid>
    </section>
  </div>
</template>
