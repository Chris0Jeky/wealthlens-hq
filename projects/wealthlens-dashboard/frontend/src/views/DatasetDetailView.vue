<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useDataStore, type DatasetRow } from '@/stores/data'

const route = useRoute()
const store = useDataStore()

const datasetName = computed(() => route.params.name as string)

const metadata = ref<{
  name: string
  description: string
  source: string
  source_url: string
  access_date: string
  row_count: number
  columns: string[]
} | null>(null)
const rows = ref<DatasetRow[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

const chartTitles: Record<string, string> = {
  'wealth-shares': 'Wealth Shares',
  'housing-affordability': 'Housing Affordability',
  'wealth-by-decile': 'Wealth by Decile',
  'cgt-concentration': 'CGT Concentration',
}

const hasChart = computed(() => datasetName.value in chartTitles)

onMounted(async () => {
  try {
    const [metaRes, dataRows] = await Promise.all([
      fetch(`/api/data/${datasetName.value}/metadata`),
      store.fetchDataset(datasetName.value),
    ])
    if (!metaRes.ok) throw new Error(`Metadata request failed: ${metaRes.status}`)
    metadata.value = await metaRes.json()
    rows.value = dataRows.slice(0, 10)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Failed to load dataset'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="max-w-6xl mx-auto px-6 py-10">
    <router-link
      to="/"
      class="inline-flex items-center text-sm text-blue-600 hover:text-blue-800 mb-6"
    >
      &larr; Back to datasets
    </router-link>

    <div v-if="loading" class="py-20 text-center">
      <p class="text-gray-500 text-lg">Loading dataset...</p>
    </div>

    <div v-else-if="error" class="py-10 text-center" role="alert">
      <p class="text-red-600 font-medium">{{ error }}</p>
      <p class="text-gray-500 text-sm mt-2">
        Make sure the backend API is running on port 8000.
      </p>
    </div>

    <template v-else-if="metadata">
      <header class="mb-8">
        <h1 class="text-2xl font-bold mb-2">{{ metadata.name }}</h1>
        <p class="text-gray-600">{{ metadata.description }}</p>
      </header>

      <section class="mb-8" aria-labelledby="source-heading">
        <h2 id="source-heading" class="text-lg font-semibold mb-3">
          Data Source
        </h2>
        <dl class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-2 text-sm">
          <div>
            <dt class="text-gray-500">Source</dt>
            <dd class="font-medium">{{ metadata.source }}</dd>
          </div>
          <div>
            <dt class="text-gray-500">URL</dt>
            <dd>
              <a
                :href="metadata.source_url"
                target="_blank"
                rel="noopener noreferrer"
                class="text-blue-600 hover:text-blue-800 underline break-all"
              >
                {{ metadata.source_url }}
                <span class="sr-only">(opens in new tab)</span>
              </a>
            </dd>
          </div>
          <div>
            <dt class="text-gray-500">Access Date</dt>
            <dd class="font-medium">{{ metadata.access_date }}</dd>
          </div>
          <div>
            <dt class="text-gray-500">Row Count</dt>
            <dd class="font-medium">{{ metadata.row_count.toLocaleString() }}</dd>
          </div>
        </dl>
      </section>

      <div v-if="hasChart" class="mb-8">
        <router-link
          :to="`/charts/${datasetName}`"
          class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors text-sm font-medium"
        >
          View Chart &rarr;
        </router-link>
      </div>

      <section aria-labelledby="preview-heading">
        <h2 id="preview-heading" class="text-lg font-semibold mb-3">
          Data Preview
          <span class="text-sm font-normal text-gray-500">
            (first {{ rows.length }} of {{ metadata.row_count.toLocaleString() }} rows)
          </span>
        </h2>
        <div class="overflow-x-auto border rounded-lg">
          <table class="min-w-full text-sm">
            <thead class="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th
                  v-for="col in metadata.columns"
                  :key="col"
                  scope="col"
                  class="px-4 py-2 text-left font-medium text-gray-700 dark:text-gray-300"
                >
                  {{ col }}
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="(row, i) in rows" :key="i">
                <td
                  v-for="col in metadata.columns"
                  :key="col"
                  class="px-4 py-2 text-gray-900 dark:text-gray-100 whitespace-nowrap"
                >
                  {{ row[col] ?? '—' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </template>
  </div>
</template>
