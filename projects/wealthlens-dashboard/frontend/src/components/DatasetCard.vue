<script setup lang="ts">
import { SUPPORTED_CHART_NAMES } from '@/utils/chartConstants'

const props = defineProps<{
  name: string
  description: string
  /** Override chart availability. When omitted, checks SUPPORTED_CHART_NAMES. */
  hasChart?: boolean
}>()

const chartAvailable =
  props.hasChart !== undefined
    ? props.hasChart
    : SUPPORTED_CHART_NAMES.has(props.name)

const downloadUrl = `/api/data/${props.name}/download`
</script>

<template>
  <article
    :aria-label="`Dataset: ${name}`"
    class="rounded-lg border border-[var(--wl-rule)] p-6 hover:shadow-md transition-shadow"
  >
    <h3 class="text-lg font-semibold mb-2">{{ name }}</h3>
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
