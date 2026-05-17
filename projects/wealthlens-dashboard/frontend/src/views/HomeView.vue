<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useDataStore } from '@/stores/data'
import DatasetCard from '@/components/DatasetCard.vue'
import DatasetSearch from '@/components/DatasetSearch.vue'
import { CHART_METADATA } from '@/utils/chartConstants'

const store = useDataStore()
const searchFilter = ref<{ active: boolean; names: string[] }>({
  active: false,
  names: [],
})

const descriptions: Record<string, string> = Object.fromEntries(
  Object.values(CHART_METADATA).map((c) => [c.name, c.description]),
)

const visibleDatasets = computed(() => {
  if (!searchFilter.value.active) return store.datasets
  const allowed = new Set(searchFilter.value.names)
  return store.datasets.filter((name) => allowed.has(name))
})

function onSearchFiltered(payload: { active: boolean; names: string[] }) {
  searchFilter.value = payload
}

onMounted(() => {
  store.fetchDatasets()
})
</script>

<template>
  <div class="max-w-6xl mx-auto px-6 py-10">
    <section class="mb-12" aria-labelledby="dashboard-heading">
      <h1 id="dashboard-heading" class="text-3xl font-bold mb-3">UK Wealth Inequality Dashboard</h1>
      <p class="text-[var(--wl-ink-muted)] max-w-2xl">
        Open-source, source-backed data on wealth inequality in the United
        Kingdom. Every chart cites its data source with URL and access date.
      </p>
    </section>

    <!-- Dataset search/filter -->
    <DatasetSearch @filtered-change="onSearchFiltered" />

    <section aria-labelledby="datasets-heading">
      <h2 id="datasets-heading" class="text-xl font-semibold mb-4">Available Datasets</h2>

      <div aria-live="polite">
        <p v-if="store.loading" class="text-[var(--wl-ink-muted)]">Loading datasets...</p>
      </div>
      <div aria-live="assertive">
        <p v-if="store.error" class="text-[var(--wl-red)]">{{ store.error }}</p>
      </div>

      <div v-if="!store.loading && !store.error" class="grid gap-4 sm:grid-cols-2" role="list">
        <div v-for="name in visibleDatasets" :key="name" role="listitem">
          <DatasetCard
            :name="name"
            :description="descriptions[name] ?? 'UK inequality dataset'"
          />
        </div>
      </div>
    </section>
  </div>
</template>
