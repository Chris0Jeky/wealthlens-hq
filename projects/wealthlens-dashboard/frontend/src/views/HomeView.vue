<script setup lang="ts">
import { onMounted } from 'vue'
import { useDataStore } from '@/stores/data'
import DatasetCard from '@/components/DatasetCard.vue'

const store = useDataStore()

const descriptions: Record<string, string> = {
  'wealth-shares':
    'Top 1% and 10% share of UK net personal wealth since 1820 (WID)',
  'housing-affordability':
    'House price to earnings ratio by region, 1997-2025 (ONS)',
  'wealth-by-decile':
    'Total net wealth by decile group in Great Britain (ONS WAS)',
  'cgt-concentration': 'Capital gains concentration by size of gain (HMRC)',
}

onMounted(() => {
  store.fetchDatasets()
})
</script>

<template>
  <div class="max-w-6xl mx-auto px-6 py-10">
    <section class="mb-12">
      <h1 class="text-3xl font-bold mb-3">UK Wealth Inequality Dashboard</h1>
      <p class="text-gray-600 max-w-2xl">
        Open-source, source-backed data on wealth inequality in the United
        Kingdom. Every chart cites its data source with URL and access date.
      </p>
    </section>

    <section>
      <h2 class="text-xl font-semibold mb-4">Available Datasets</h2>

      <p v-if="store.loading" class="text-gray-500">Loading datasets...</p>
      <p v-else-if="store.error" class="text-red-600">{{ store.error }}</p>

      <div v-else class="grid gap-4 sm:grid-cols-2">
        <DatasetCard
          v-for="name in store.datasets"
          :key="name"
          :name="name"
          :description="descriptions[name] ?? 'UK inequality dataset'"
        />
      </div>
    </section>
  </div>
</template>
