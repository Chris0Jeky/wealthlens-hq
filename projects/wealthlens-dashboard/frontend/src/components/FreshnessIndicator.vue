<script setup lang="ts">
/**
 * FreshnessIndicator — shows dataset freshness as a coloured dot + text label.
 *
 * Accessibility: Uses both colour AND a visible text label so colour is
 * never the sole means of conveying information (WCAG 1.4.1). Provides
 * a tooltip with the full "Last updated: X days ago" detail. Includes
 * a screen-reader-only description for assistive technology.
 */
import { computed } from "vue"
import type { DatasetFreshnessEntry } from "@/types/api"

const props = defineProps<{
  /** Freshness data for this dataset. */
  freshness: DatasetFreshnessEntry
}>()

/** Map status to Tailwind dot colour class. */
const dotColorClass = computed(() => {
  const map: Record<string, string> = {
    fresh: "bg-green-500",
    stale: "bg-yellow-500",
    expired: "bg-red-500",
    unknown: "bg-gray-400",
  }
  return map[props.freshness.status] ?? "bg-gray-400"
})

/** Human-readable label displayed beside the dot. */
const label = computed(() => {
  const map: Record<string, string> = {
    fresh: "Fresh",
    stale: "Stale",
    expired: "Expired",
    unknown: "Unknown",
  }
  return map[props.freshness.status] ?? "Unknown"
})

/** Tooltip text with relative age. */
const tooltipText = computed(() => {
  if (props.freshness.age_hours == null) {
    return "Data file not found"
  }
  const hours = props.freshness.age_hours
  if (hours < 1) return "Last updated: less than an hour ago"
  if (hours < 24) return `Last updated: ${Math.round(hours)} hours ago`
  const days = Math.round(hours / 24)
  return `Last updated: ${days} ${days === 1 ? "day" : "days"} ago`
})
</script>

<template>
  <span
    class="freshness-indicator relative inline-flex items-center gap-1.5"
    @mouseenter="($event.currentTarget as HTMLElement).dataset.hover = 'true'"
    @mouseleave="($event.currentTarget as HTMLElement).dataset.hover = 'false'"
    @focusin="($event.currentTarget as HTMLElement).dataset.hover = 'true'"
    @focusout="($event.currentTarget as HTMLElement).dataset.hover = 'false'"
    tabindex="0"
    :aria-label="`${label}: ${tooltipText}`"
  >
    <span
      class="inline-block h-2 w-2 rounded-full"
      :class="dotColorClass"
      aria-hidden="true"
      data-testid="freshness-dot"
    />
    <span class="text-xs text-[var(--wl-ink-muted)]" data-testid="freshness-label">
      {{ label }}
    </span>
    <span
      role="tooltip"
      class="freshness-tooltip absolute left-1/2 -translate-x-1/2 bottom-full mb-2 z-40 whitespace-nowrap rounded bg-gray-900 dark:bg-gray-100 px-2.5 py-1.5 text-xs font-medium text-white dark:text-gray-900 shadow-lg pointer-events-none opacity-0 transition-opacity"
      data-testid="freshness-tooltip"
    >
      {{ tooltipText }}
    </span>
    <span class="sr-only">{{ tooltipText }}</span>
  </span>
</template>

<style scoped>
.freshness-indicator[data-hover="true"] .freshness-tooltip {
  opacity: 1;
}
</style>
