<script setup lang="ts">
/**
 * FreshnessIndicator — shows dataset freshness as a coloured dot + text label.
 *
 * Grading is cadence-aware (docs/product/freshness-grammar.md): a dataset is
 * judged against its OWN source's release rhythm, not a wall-clock ladder —
 * fully-current annual statistics no longer badge "Expired" (F3). There is
 * deliberately no red state.
 *
 * Accessibility: Uses both colour AND a visible text label so colour is
 * never the sole means of conveying information (WCAG 1.4.1). Provides
 * a tooltip with the "last updated" detail plus what the state means for
 * this series. Includes a screen-reader-only description.
 */
import { computed } from "vue"
import type { DatasetFreshnessEntry } from "@/types/api"
import { assessFreshness } from "@/utils/freshnessCadence"

const props = defineProps<{
  /** Dataset slug — keys the provenance cadence. */
  dataset: string
  /** Freshness data for this dataset. */
  freshness: DatasetFreshnessEntry
}>()

const assessment = computed(() => assessFreshness(props.dataset, props.freshness.last_updated))

/** Map cadence state to dot colour class. No red — see the grammar note. */
const dotColorClass = computed(() => {
  const map: Record<string, string> = {
    current: "bg-green-500",
    due: "bg-yellow-500",
    suspended: "bg-gray-400",
    unknown: "bg-gray-400",
  }
  return map[assessment.value.state] ?? "bg-gray-400"
})

const label = computed(() => assessment.value.label)

/** Tooltip text: relative age + what the state means for this series. */
const tooltipText = computed(() => {
  const parts: string[] = []
  if (props.freshness.age_hours == null) {
    parts.push("No update date recorded")
  } else {
    const hours = props.freshness.age_hours
    if (hours < 24) {
      parts.push(`Last updated: ${Math.max(1, Math.round(hours))} hours ago`)
    } else {
      const days = Math.round(hours / 24)
      parts.push(`Last updated: ${days} ${days === 1 ? "day" : "days"} ago`)
    }
  }
  parts.push(assessment.value.detail)
  return parts.join(" — ")
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
      class="freshness-tooltip absolute left-1/2 -translate-x-1/2 bottom-full mb-2 z-40 rounded bg-gray-900 dark:bg-gray-100 px-2.5 py-1.5 text-xs font-medium text-white dark:text-gray-900 shadow-lg pointer-events-none opacity-0 transition-opacity"
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

.freshness-tooltip {
  width: max-content;
  max-width: 280px;
  white-space: normal;
}
</style>
