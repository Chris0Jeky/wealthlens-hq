<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useDataStore } from '@/stores/data'
import DatasetCard from '@/components/DatasetCard.vue'
import ResponsiveGrid from '@/components/ResponsiveGrid.vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import NumberStat from '@/components/NumberStat.vue'
import { CHART_METADATA } from '@/utils/chartConstants'
import { SUPPORTED_CHART_NAMES } from '@/utils/chartConstants'

const store = useDataStore()

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
  store.fetchDatasets()
  try {
    await store.fetchAllMetadata()
  } catch {
    // Metadata fetch failure is non-blocking — fallback descriptions will be used
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

      <!-- Loading state -->
      <div v-if="store.loading" aria-live="polite">
        <ResponsiveGrid min-width="280px" gap="1.5rem">
          <div
            v-for="i in 10"
            :key="i"
            class="rounded-lg border border-[var(--wl-rule)] p-6"
          >
            <SkeletonLoader height="1.5rem" width="60%" label="Loading dataset title" />
            <div class="mt-3">
              <SkeletonLoader :lines="2" label="Loading dataset description" />
            </div>
            <div class="mt-4">
              <SkeletonLoader height="1rem" width="40%" label="Loading dataset actions" />
            </div>
          </div>
        </ResponsiveGrid>
      </div>

      <!-- Error state -->
      <div
        v-else-if="store.error"
        role="alert"
        class="rounded-lg border border-[var(--wl-red)] bg-red-50 dark:bg-red-950 p-6"
      >
        <p class="text-[var(--wl-red)] font-medium mb-2">
          Failed to load datasets
        </p>
        <p class="text-sm text-[var(--wl-ink-muted)]">
          {{ store.error }}
        </p>
        <button
          class="mt-4 px-4 py-2 text-sm font-medium rounded border border-[var(--wl-red)] text-[var(--wl-red)] hover:bg-red-100 dark:hover:bg-red-900 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--wl-red)]"
          @click="store.fetchDatasets()"
        >
          Retry
        </button>
      </div>

      <!-- Dataset cards grid -->
      <ResponsiveGrid v-else min-width="280px" gap="1.5rem" role="list">
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
