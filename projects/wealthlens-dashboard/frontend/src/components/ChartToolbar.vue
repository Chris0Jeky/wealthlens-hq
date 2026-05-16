<script setup lang="ts">
/**
 * ChartToolbar — Toolbar with series legend dots and time-range buttons.
 *
 * Sits at the top of a chart card, showing series names with coloured dots
 * on the left, and a bank of range-period buttons on the right.
 *
 * Emits 'range-change' when a range button is clicked.
 *
 * @example
 * <ChartToolbar
 *   title="Share of net personal wealth"
 *   unit="%"
 *   :series="[
 *     { label: 'Top 10%', color: 'var(--wl-red)', bold: true },
 *     { label: 'Top 1%', color: 'var(--wl-ink)' },
 *   ]"
 *   :ranges="['200y', '100y', '50y', '25y']"
 *   active-range="200y"
 *   @range-change="onRangeChange"
 * />
 */

export interface SeriesLegendItem {
  label: string;
  color: string;
  bold?: boolean;
}

const props = withDefaults(
  defineProps<{
    title?: string;
    unit?: string;
    series?: SeriesLegendItem[];
    ranges?: string[];
    activeRange?: string;
  }>(),
  {
    title: "",
    unit: "",
    series: () => [],
    ranges: () => [],
    activeRange: "",
  },
);

const emit = defineEmits<{
  (e: "range-change", range: string): void;
}>();

function selectRange(range: string) {
  emit("range-change", range);
}
</script>

<template>
  <div class="chart-toolbar">
    <div class="chart-toolbar__left">
      <span v-if="props.title" class="chart-toolbar__tag">
        <b>{{ props.title }}</b>
        <template v-if="props.unit"> ({{ props.unit }})</template>
      </span>
      <span
        v-for="s in props.series"
        :key="s.label"
        class="chart-toolbar__tag"
      >
        <span
          class="chart-toolbar__dot"
          :style="{ background: s.color }"
        ></span>
        <b v-if="s.bold">{{ s.label }}</b>
        <template v-else>{{ s.label }}</template>
      </span>
    </div>
    <div
      v-if="props.ranges.length > 0"
      class="chart-toolbar__ranges"
      role="tablist"
      aria-label="Time range"
    >
      <button
        v-for="r in props.ranges"
        :key="r"
        :class="['chart-toolbar__range', { active: r === props.activeRange }]"
        role="tab"
        :aria-selected="r === props.activeRange"
        @click="selectRange(r)"
      >
        {{ r }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.chart-toolbar {
  display: flex;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid var(--wl-rule);
  gap: 18px;
  font-family: var(--wl-mono);
  font-size: 12px;
  flex-wrap: wrap;
}

.chart-toolbar__left {
  display: flex;
  gap: 22px;
  align-items: center;
  flex-wrap: wrap;
}

.chart-toolbar__tag {
  color: var(--wl-ink-muted);
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.chart-toolbar__tag b {
  color: var(--wl-ink);
  font-weight: 600;
}

.chart-toolbar__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
  flex-shrink: 0;
}

.chart-toolbar__ranges {
  display: flex;
  gap: 0;
  margin-left: auto;
  border: 1px solid var(--wl-ink);
}

.chart-toolbar__range {
  padding: 6px 14px;
  border: 0;
  border-left: 1px solid var(--wl-rule);
  background: var(--wl-card);
  color: var(--wl-ink-muted);
  font-family: var(--wl-mono);
  font-size: 11px;
  cursor: pointer;
  letter-spacing: 0.04em;
}
.chart-toolbar__range:first-child {
  border-left: 0;
}
.chart-toolbar__range:hover {
  color: var(--wl-ink);
}
.chart-toolbar__range.active {
  background: var(--wl-ink);
  color: var(--wl-paper);
}
</style>
