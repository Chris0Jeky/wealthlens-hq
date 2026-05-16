<script setup lang="ts">
/**
 * DataFreshnessBadge — Small badge indicating when a dataset was last updated.
 *
 * Displays a coloured dot and relative time since last data update.
 * Color coding:
 *   - Green (--wl-teal): updated within 7 days
 *   - Amber (--wl-gold): updated 7–30 days ago
 *   - Red (--wl-red): updated more than 30 days ago
 *
 * Shows a tooltip on hover with the full date and source name.
 * Gracefully handles missing/unavailable freshness data by rendering nothing.
 */
import { computed } from "vue";
import {
  useDataFreshness,
  daysAgo,
  relativeTime,
} from "@/composables/useDataFreshness";

const props = defineProps<{
  /** The dataset slug (e.g. "wealth-shares") */
  dataset: string;
}>();

const { freshnessInfo, loading } = useDataFreshness(props.dataset);

/** Number of days since last update. */
const age = computed(() => {
  if (!freshnessInfo.value) return 0;
  return daysAgo(freshnessInfo.value.lastUpdated);
});

/** CSS class for color coding based on data age. */
const colorClass = computed(() => {
  if (age.value > 30) return "freshness-badge__dot--red";
  if (age.value >= 7) return "freshness-badge__dot--amber";
  return "freshness-badge__dot--green";
});

/** Relative time display text. */
const timeText = computed(() => {
  if (!freshnessInfo.value) return "";
  return relativeTime(freshnessInfo.value.lastUpdated);
});

/** Full tooltip text with date and source. */
const tooltipText = computed(() => {
  if (!freshnessInfo.value) return "";
  const dateStr = freshnessInfo.value.lastUpdated.toLocaleDateString("en-GB", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
  return `Last updated: ${dateStr}\nSource: ${freshnessInfo.value.source}`;
});
</script>

<template>
  <span
    v-if="!loading && freshnessInfo"
    class="freshness-badge"
    role="status"
    :aria-label="`Data updated ${timeText}`"
    :title="tooltipText"
  >
    <span
      class="freshness-badge__dot"
      :class="colorClass"
      aria-hidden="true"
    ></span>
    <span class="freshness-badge__text">
      Data: {{ timeText }}
    </span>
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
}

.freshness-badge__dot--red {
  background-color: var(--wl-red);
}

.freshness-badge__text {
  white-space: nowrap;
}
</style>
