<script setup lang="ts">
/**
 * DataFreshnessBadge — Small badge indicating when a dataset was last updated.
 *
 * Displays a coloured dot and relative time since last data update. The dot
 * is cadence-aware (docs/product/freshness-grammar.md): green while the
 * source is not expected to have published a newer release, amber when our
 * ingest may lag one, grey for a suspended source or unknown cadence.
 * There is deliberately no red state (F3).
 *
 * Shows a tooltip on hover with the full date, source name, and what the
 * state means for this series. Renders nothing without freshness data.
 */
import { computed, toRef } from "vue"
import { useDataFreshness, relativeTime } from "@/composables/useDataFreshness"
import { assessFreshness } from "@/utils/freshnessCadence"

const props = defineProps<{
  dataset: string
}>()

const { freshnessInfo, loading } = useDataFreshness(toRef(props, "dataset"))

/** Cadence-aware grading against this source's own release rhythm. */
const assessment = computed(() => {
  if (!freshnessInfo.value) return null
  return assessFreshness(props.dataset, freshnessInfo.value.lastUpdated.toISOString())
})

/** CSS class for the state dot — no red (see the grammar note). */
const colorClass = computed(() => {
  switch (assessment.value?.state) {
    case "current":
      return "freshness-badge__dot--green"
    case "due":
      return "freshness-badge__dot--amber"
    default:
      return "freshness-badge__dot--grey"
  }
})

/** Relative time display text. */
const timeText = computed(() => {
  if (!freshnessInfo.value) return ""
  return relativeTime(freshnessInfo.value.lastUpdated)
})

/** Full tooltip text with date and source. */
const tooltipText = computed(() => {
  if (!freshnessInfo.value) return ""
  const dateStr = freshnessInfo.value.lastUpdated.toLocaleDateString("en-GB", {
    day: "numeric",
    month: "long",
    year: "numeric",
  })
  return `Last updated: ${dateStr}\nSource: ${freshnessInfo.value.source}`
})
</script>

<template>
  <span
    v-if="!loading && freshnessInfo"
    class="freshness-badge"
    role="status"
    :aria-label="`Data updated ${timeText}`"
    :title="tooltipText"
  >
    <span class="freshness-badge__dot" :class="colorClass" aria-hidden="true"></span>
    <span class="freshness-badge__text"> Data: {{ timeText }} </span>
  </span>
</template>

<style scoped>
.freshness-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: var(--wl-mono);
  font-size: 11px;
  color: var(--wl-ink-muted);
  letter-spacing: 0.04em;
  cursor: default;
}

.freshness-badge__dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.freshness-badge__dot--green {
  background-color: var(--wl-teal);
}

.freshness-badge__dot--amber {
  background-color: var(--wl-gold);
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--wl-gold) 70%, black);
}

.freshness-badge__dot--grey {
  background-color: var(--wl-ink-faint);
}

.freshness-badge__text {
  white-space: nowrap;
}
</style>
