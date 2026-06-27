<script setup lang="ts">
/**
 * DataSourcesView — public transparency page showing provenance info
 * for every dataset in the WealthLens platform.
 *
 * Fetches all metadata from the data store and displays source citations
 * in a searchable, responsive format (table on desktop, cards on mobile).
 */
import { ref, computed, onMounted } from "vue"
import { useDataStore, type DatasetMetadata } from "@/stores/data"
import PageHeader from "@/components/PageHeader.vue"
import SearchInput from "@/components/SearchInput.vue"
import ExternalLink from "@/components/ExternalLink.vue"
import SkeletonLoader from "@/components/SkeletonLoader.vue"

const store = useDataStore()

const allMetadata = ref<DatasetMetadata[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const searchQuery = ref("")

/** Additional source info not in the API metadata (licence, update frequency). */
const EXTRA_SOURCE_INFO: Record<string, { licence: string; frequency: string }> = {
  "wealth-shares": { licence: "Creative Commons", frequency: "Periodic" },
  "housing-affordability": { licence: "Open Government Licence v3.0", frequency: "Annual" },
  "wealth-by-decile": { licence: "Open Government Licence v3.0", frequency: "Biennial" },
  "cgt-concentration": { licence: "Open Government Licence v3.0", frequency: "Annual" },
  "productivity-pay": { licence: "Open Government Licence v3.0", frequency: "Quarterly" },
  "gdhi-by-region": { licence: "Open Government Licence v3.0", frequency: "Annual" },
  "tax-composition": { licence: "Open Government Licence v3.0", frequency: "Monthly" },
  "boe-rates": { licence: "Open Government Licence v3.0", frequency: "Monthly" },
  "child-poverty": { licence: "Open Government Licence v3.0", frequency: "Annual" },
  "generational-wealth": { licence: "Creative Commons", frequency: "Annual" },
  // inheritance-tax + wage-stagnation are served from static/hand-curated JSON
  // (outside the CSV metadata pipeline), so they are not yet in the generated
  // all-metadata this page renders. Pre-registered here so they show the correct
  // licence/frequency once wired into all-metadata (tracked follow-up).
  "wage-stagnation": { licence: "Open Government Licence v3.0", frequency: "Annual" },
  "inheritance-tax": { licence: "Open Government Licence v3.0", frequency: "Annual" },
}

const filteredDatasets = computed(() => {
  if (!searchQuery.value.trim()) return allMetadata.value
  const q = searchQuery.value.toLowerCase()
  return allMetadata.value.filter(
    (ds) =>
      ds.name.toLowerCase().includes(q) ||
      ds.description.toLowerCase().includes(q) ||
      ds.source.toLowerCase().includes(q),
  )
})

onMounted(async () => {
  try {
    allMetadata.value = await store.fetchAllMetadata()
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Failed to load data source information"
  } finally {
    loading.value = false
  }
})

function formatDatasetName(name: string): string {
  return name
    .split("-")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ")
}
</script>

<template>
  <div class="max-w-6xl mx-auto px-6 py-10">
    <PageHeader
      title="Data Sources"
      description="Every dataset in WealthLens cites its source. This page documents where our data comes from, how often it is updated, and under what licence it is published."
    />

    <!-- Intro text -->
    <section class="mb-8 max-w-3xl" aria-labelledby="transparency-heading">
      <h2 id="transparency-heading" class="sr-only">Our commitment to data transparency</h2>
      <p class="text-[var(--wl-ink-body)] leading-relaxed">
        WealthLens UK is committed to full data transparency. We source datasets directly from
        official government publications, academic databases, and reputable research organisations,
        and we do not editorialise the figures. Where values are rounded or composited for clarity,
        or a live source is temporarily unavailable, the dataset is clearly labelled illustrative
        (see each chart's methodology). Each source is linked below so you can verify the data
        yourself.
      </p>
    </section>

    <!-- Search -->
    <div class="mb-6 max-w-sm">
      <SearchInput v-model="searchQuery" placeholder="Filter data sources..." :debounce-ms="200" />
    </div>

    <!-- Loading state -->
    <div v-if="loading" aria-live="polite" class="space-y-4">
      <p class="text-[var(--wl-ink-muted)]">Loading data sources...</p>
      <SkeletonLoader :lines="5" height="1.5rem" label="Loading data sources" />
    </div>

    <!-- Error state -->
    <div v-else-if="error" aria-live="assertive" role="alert">
      <p class="text-[var(--wl-red)] font-medium">{{ error }}</p>
      <p class="text-sm text-[var(--wl-ink-muted)] mt-1">
        Please try refreshing the page. If the problem persists, the API may be temporarily
        unavailable.
      </p>
    </div>

    <!-- Data sources display -->
    <template v-else>
      <!-- No results -->
      <p
        v-if="filteredDatasets.length === 0"
        class="text-[var(--wl-ink-muted)] py-8"
        aria-live="polite"
      >
        No data sources match your search.
      </p>

      <!-- Desktop table (hidden on mobile) -->
      <div
        v-if="filteredDatasets.length > 0"
        class="hidden md:block overflow-x-auto"
        role="region"
        aria-label="Data sources table"
      >
        <table class="w-full text-sm text-left border-collapse">
          <thead>
            <tr class="border-b-2 border-[var(--wl-rule-strong)]">
              <th scope="col" class="py-3 px-4 font-semibold text-[var(--wl-ink)]">Dataset</th>
              <th scope="col" class="py-3 px-4 font-semibold text-[var(--wl-ink)]">Description</th>
              <th scope="col" class="py-3 px-4 font-semibold text-[var(--wl-ink)]">Source</th>
              <th scope="col" class="py-3 px-4 font-semibold text-[var(--wl-ink)]">Licence</th>
              <th scope="col" class="py-3 px-4 font-semibold text-[var(--wl-ink)]">Frequency</th>
              <th scope="col" class="py-3 px-4 font-semibold text-[var(--wl-ink)]">Accessed</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="ds in filteredDatasets"
              :key="ds.name"
              class="border-b border-[var(--wl-rule)] hover:bg-[var(--wl-bg-alt)]"
            >
              <td class="py-3 px-4 font-medium text-[var(--wl-ink)]">
                {{ formatDatasetName(ds.name) }}
              </td>
              <td class="py-3 px-4 text-[var(--wl-ink-body)]">
                {{ ds.description }}
              </td>
              <td class="py-3 px-4">
                <ExternalLink :href="ds.source_url">
                  {{ ds.source }}
                </ExternalLink>
              </td>
              <td class="py-3 px-4 text-[var(--wl-ink-body)]">
                {{ EXTRA_SOURCE_INFO[ds.name]?.licence ?? "Unknown" }}
              </td>
              <td class="py-3 px-4 text-[var(--wl-ink-body)]">
                {{ EXTRA_SOURCE_INFO[ds.name]?.frequency ?? "Unknown" }}
              </td>
              <td class="py-3 px-4 text-[var(--wl-ink-muted)] whitespace-nowrap">
                {{ ds.access_date }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Mobile cards (hidden on desktop) -->
      <div
        v-if="filteredDatasets.length > 0"
        class="md:hidden space-y-4"
        role="list"
        aria-label="Data sources"
      >
        <article
          v-for="ds in filteredDatasets"
          :key="ds.name"
          role="listitem"
          class="border border-[var(--wl-rule)] rounded-lg p-4"
        >
          <h3 class="font-semibold text-[var(--wl-ink)] mb-1">
            {{ formatDatasetName(ds.name) }}
          </h3>
          <p class="text-sm text-[var(--wl-ink-body)] mb-3">{{ ds.description }}</p>
          <dl class="text-sm space-y-2">
            <div class="flex gap-2">
              <dt class="font-medium text-[var(--wl-ink)] min-w-[5rem]">Source:</dt>
              <dd>
                <ExternalLink :href="ds.source_url">
                  {{ ds.source }}
                </ExternalLink>
              </dd>
            </div>
            <div class="flex gap-2">
              <dt class="font-medium text-[var(--wl-ink)] min-w-[5rem]">Licence:</dt>
              <dd class="text-[var(--wl-ink-body)]">
                {{ EXTRA_SOURCE_INFO[ds.name]?.licence ?? "Unknown" }}
              </dd>
            </div>
            <div class="flex gap-2">
              <dt class="font-medium text-[var(--wl-ink)] min-w-[5rem]">Frequency:</dt>
              <dd class="text-[var(--wl-ink-body)]">
                {{ EXTRA_SOURCE_INFO[ds.name]?.frequency ?? "Unknown" }}
              </dd>
            </div>
            <div class="flex gap-2">
              <dt class="font-medium text-[var(--wl-ink)] min-w-[5rem]">Accessed:</dt>
              <dd class="text-[var(--wl-ink-muted)]">{{ ds.access_date }}</dd>
            </div>
          </dl>
        </article>
      </div>

      <!-- Summary -->
      <p class="mt-6 text-sm text-[var(--wl-ink-muted)]" aria-live="polite">
        Showing {{ filteredDatasets.length }} of {{ allMetadata.length }} data sources.
      </p>
    </template>
  </div>
</template>
