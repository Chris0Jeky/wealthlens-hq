<script setup lang="ts">
import { VALID_CHART_NAMES } from '@/constants/charts'

const props = defineProps<{
  name: string
  description: string
  /** Override chart availability. When omitted, checks VALID_CHART_NAMES. */
  hasChart?: boolean
}>()

const chartAvailable =
  props.hasChart !== undefined
    ? props.hasChart
    : VALID_CHART_NAMES.has(props.name)
</script>

<template>
  <article
    :aria-label="`Dataset: ${name}`"
    class="rounded-lg border border-[var(--wl-rule)] p-6 hover:shadow-md transition-shadow"
  >
    <h3 class="text-lg font-semibold mb-2">{{ name }}</h3>
    <p class="text-sm text-[var(--wl-ink-muted)] mb-3">{{ description }}</p>
    <router-link
      v-if="chartAvailable"
      :to="`/charts/${name}`"
      :aria-label="`View ${name} chart`"
      class="inline-flex items-center text-sm font-medium text-[var(--wl-red)] hover:text-[var(--wl-red-deep)] focus:outline-none focus:ring-2 focus:ring-[var(--wl-red)] focus:ring-offset-2 rounded"
    >
      View Chart &rarr;
    </router-link>
    <span v-else class="text-sm text-[var(--wl-ink-faint)] italic">Chart coming soon</span>
  </article>
</template>
