<script setup lang="ts">
import { computed } from "vue"
import { SUPPORTED_CHART_NAMES } from "@/utils/chartConstants"
import { csvDownloadUrl, hasCsvDownload } from "@/constants/downloads"
import FreshnessIndicator from "@/components/FreshnessIndicator.vue"
import type { DatasetFreshnessEntry } from "@/types/api"

const props = withDefaults(
  defineProps<{
    name: string
    description: string
    /** Override chart availability. When omitted, checks SUPPORTED_CHART_NAMES. */
    hasChart?: boolean
    /** Freshness info for this dataset (optional — hidden if not provided). */
    freshness?: DatasetFreshnessEntry
  }>(),
  // Vue casts an absent Boolean prop to `false`, which would make the override
  // below always win and hide every "View Chart" link. `default: undefined`
  // disables that casting so omission genuinely means "no override".
  // (`freshness` is listed only to satisfy vue/require-default-prop; object
  // props are never Boolean-cast.)
  { hasChart: undefined, freshness: undefined },
)

const chartAvailable = computed(() =>
  props.hasChart !== undefined ? props.hasChart : SUPPORTED_CHART_NAMES.has(props.name),
)

// The static CSV mirror (RFC-001a) — previously pointed at /api/data/.../download,
// a backend that does not exist on the GitHub Pages deploy (reality-check F8).
const downloadUrl = computed(() => csvDownloadUrl(props.name))
const csvAvailable = computed(() => hasCsvDownload(props.name))
</script>

<template>
  <article
    :aria-label="`Dataset: ${name}`"
    class="rounded-lg border border-[var(--wl-rule)] p-6 hover:shadow-md transition-shadow"
  >
    <div class="flex items-center justify-between mb-2">
      <h3 class="text-lg font-semibold">{{ name }}</h3>
      <FreshnessIndicator v-if="freshness" :freshness="freshness" />
    </div>
    <p class="text-sm text-[var(--wl-ink-muted)] mb-3">{{ description }}</p>
    <div class="flex items-center gap-4">
      <router-link
        :to="`/datasets/${name}`"
        class="inline-flex items-center text-sm font-medium text-[var(--wl-ink-muted)] hover:text-[var(--wl-ink)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--wl-red)] rounded"
      >
        Details
      </router-link>
      <router-link
        v-if="chartAvailable"
        :to="`/charts/${name}`"
        :aria-label="`View ${name} chart`"
        class="inline-flex items-center text-sm font-medium text-[var(--wl-red)] hover:text-[var(--wl-red-deep)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--wl-red)] rounded"
      >
        View Chart &rarr;
      </router-link>
      <span v-else class="text-sm text-[var(--wl-ink-faint)] italic">Chart coming soon</span>
      <a
        v-if="csvAvailable"
        :href="downloadUrl"
        download
        class="inline-flex items-center text-sm text-[var(--wl-ink-muted)] hover:text-[var(--wl-ink)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--wl-red)] rounded"
        :aria-label="`Download ${name} as CSV`"
      >
        &#x2913; CSV
      </a>
    </div>
  </article>
</template>
