<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useDatasetSearch, DATASET_CATEGORIES } from '@/composables/useDatasetSearch'
import type { DatasetEntry } from '@/composables/useDatasetSearch'

const router = useRouter()
const {
  query,
  selectedCategories,
  filteredDatasets,
  isSearchActive,
  resultCount,
  clearSearch,
} = useDatasetSearch(200)

// Keyboard navigation state
const activeIndex = ref(-1)
const resultsRef = ref<HTMLElement | null>(null)

// Reset active index when results change
watch(filteredDatasets, () => {
  activeIndex.value = -1
})

function onKeydown(event: KeyboardEvent) {
  const count = filteredDatasets.value.length
  if (count === 0) return

  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault()
      activeIndex.value = Math.min(activeIndex.value + 1, count - 1)
      scrollActiveIntoView()
      break
    case 'ArrowUp':
      event.preventDefault()
      activeIndex.value = Math.max(activeIndex.value - 1, 0)
      scrollActiveIntoView()
      break
    case 'Enter':
      event.preventDefault()
      if (activeIndex.value >= 0 && activeIndex.value < count) {
        navigateToDataset(filteredDatasets.value[activeIndex.value])
      }
      break
    case 'Escape':
      event.preventDefault()
      clearSearch()
      break
  }
}

function scrollActiveIntoView() {
  nextTick(() => {
    const active = resultsRef.value?.querySelector('[data-active="true"]')
    if (active && typeof active.scrollIntoView === 'function') {
      active.scrollIntoView({ block: 'nearest' })
    }
  })
}

function navigateToDataset(entry: DatasetEntry) {
  router.push(`/charts/${entry.name}`)
}

function toggleCategory(id: string) {
  const current = new Set(selectedCategories.value)
  if (current.has(id)) {
    current.delete(id)
  } else {
    current.add(id)
  }
  selectedCategories.value = [...current]
}
</script>

<template>
  <section
    class="mb-8"
    aria-labelledby="dataset-search-heading"
  >
    <h2 id="dataset-search-heading" class="sr-only">Search datasets</h2>

    <!-- Search input -->
    <div class="relative mb-4">
      <label for="dataset-search-input" class="sr-only">
        Search datasets by keyword, category, or tag
      </label>
      <input
        id="dataset-search-input"
        v-model="query"
        type="search"
        placeholder="Search datasets..."
        autocomplete="off"
        aria-describedby="search-result-count"
        class="w-full rounded-md border border-[var(--wl-rule)] bg-[var(--wl-paper)] px-4 py-3 pl-11 text-sm text-[var(--wl-ink)] placeholder-[var(--wl-ink-muted)] focus:border-[var(--wl-teal)] focus:outline-none focus:ring-2 focus:ring-[var(--wl-teal)] font-[var(--wl-serif)]"
        role="combobox"
        aria-expanded="true"
        aria-controls="dataset-search-results"
        :aria-activedescendant="activeIndex >= 0 ? `search-result-${activeIndex}` : undefined"
        @keydown="onKeydown"
      />
      <!-- Magnifying glass icon -->
      <span
        class="absolute left-3.5 top-1/2 -translate-y-1/2 text-[var(--wl-ink-muted)] pointer-events-none"
        aria-hidden="true"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
          fill="currentColor"
          class="w-4 h-4"
        >
          <path
            fill-rule="evenodd"
            d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z"
            clip-rule="evenodd"
          />
        </svg>
      </span>
      <!-- Clear button -->
      <button
        v-if="query"
        type="button"
        aria-label="Clear search"
        class="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--wl-ink-muted)] hover:text-[var(--wl-ink)] focus:outline-none focus:ring-2 focus:ring-[var(--wl-teal)] rounded"
        @click="clearSearch"
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
          <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
        </svg>
      </button>
    </div>

    <!-- Category filter chips -->
    <fieldset class="mb-4">
      <legend class="sr-only">Filter by category</legend>
      <div
        class="flex flex-wrap gap-2"
        role="group"
        aria-label="Dataset categories"
      >
        <button
          v-for="cat in DATASET_CATEGORIES"
          :key="cat.id"
          type="button"
          :aria-pressed="selectedCategories.includes(cat.id)"
          class="inline-flex items-center rounded-full px-3 py-1 text-xs font-medium transition-colors border focus:outline-none focus:ring-2 focus:ring-[var(--wl-teal)] focus:ring-offset-1"
          :class="selectedCategories.includes(cat.id)
            ? 'bg-[var(--wl-red)] text-white border-[var(--wl-red)]'
            : 'bg-[var(--wl-paper)] text-[var(--wl-ink-muted)] border-[var(--wl-rule)] hover:border-[var(--wl-ink-muted)]'"
          @click="toggleCategory(cat.id)"
        >
          {{ cat.label }}
        </button>
      </div>
    </fieldset>

    <!-- Result count announcement for screen readers -->
    <div
      id="search-result-count"
      class="sr-only"
      aria-live="polite"
      aria-atomic="true"
    >
      {{ isSearchActive ? `${resultCount} dataset${resultCount === 1 ? '' : 's'} found` : '' }}
    </div>

    <!-- Search results -->
    <div
      v-if="isSearchActive"
      id="dataset-search-results"
      ref="resultsRef"
      role="listbox"
      aria-label="Search results"
      class="space-y-3"
    >
      <!-- Empty state -->
      <p
        v-if="filteredDatasets.length === 0"
        class="text-center text-[var(--wl-ink-muted)] py-8 text-sm italic"
      >
        No datasets match your search
      </p>

      <!-- Result cards -->
      <div
        v-for="(entry, index) in filteredDatasets"
        :id="`search-result-${index}`"
        :key="entry.name"
        role="option"
        :aria-selected="index === activeIndex"
        :data-active="index === activeIndex"
        class="rounded-lg border p-4 cursor-pointer transition-all"
        :class="index === activeIndex
          ? 'border-[var(--wl-teal)] bg-[var(--wl-teal)]/5 shadow-sm'
          : 'border-[var(--wl-rule)] hover:border-[var(--wl-ink-muted)] hover:shadow-sm'"
        tabindex="-1"
        @click="navigateToDataset(entry)"
        @mouseenter="activeIndex = index"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0 flex-1">
            <h3 class="text-sm font-semibold text-[var(--wl-ink)] truncate">
              {{ entry.title }}
            </h3>
            <p class="text-xs text-[var(--wl-ink-muted)] mt-1 line-clamp-1">
              {{ entry.description }}
            </p>
          </div>
          <span
            class="inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide border border-[var(--wl-rule)] text-[var(--wl-ink-muted)] whitespace-nowrap"
          >
            {{ entry.category }}
          </span>
        </div>
      </div>
    </div>
  </section>
</template>
