<script setup lang="ts">
import { computed } from 'vue'
import AlertBanner from '@/components/AlertBanner.vue'
import type { ConfidenceFanChartProps, IntervalMethod } from '@/types/simulator'

const props = withDefaults(defineProps<ConfidenceFanChartProps>(), {
  currency: '£',
  unit: 'bn',
  decimals: 2,
  caveats: () => [],
  intervalMethod: undefined,
  provenanceComplete: true,
})

/** Plot geometry in the SVG's own (unstretched) user units. */
const PLOT_LEFT = 10
const PLOT_RIGHT = 90
const PLOT_WIDTH = PLOT_RIGHT - PLOT_LEFT

function fmt(value: number): string {
  return `${props.currency}${value.toFixed(props.decimals)}${props.unit}`
}

const span = computed(() => props.interval.high - props.interval.low)

/** A point estimate (no quantified band) — low == central == high, or unsourced. */
const isDegenerate = computed(() => span.value <= 0)

/** Map a value in [low, high] to the plot's x coordinate. */
function x(value: number): number {
  if (span.value <= 0) return PLOT_LEFT + PLOT_WIDTH / 2
  const t = (value - props.interval.low) / span.value
  return PLOT_LEFT + Math.min(1, Math.max(0, t)) * PLOT_WIDTH
}

const xLow = computed(() => x(props.interval.low))
const xCentral = computed(() => x(props.interval.central))
const xHigh = computed(() => x(props.interval.high))

const methodLabel = computed<string>(() => {
  const map: Record<IntervalMethod, string> = {
    monte_carlo: 'Monte-Carlo credible interval',
    alpha_sweep: 'Pareto-α range',
  }
  return props.intervalMethod ? map[props.intervalMethod] : ''
})

const ariaLabel = computed(() => {
  if (isDegenerate.value || !props.provenanceComplete) {
    return `${props.label}: ${fmt(props.interval.central)} (point estimate; uncertainty unquantified).`
  }
  const method = methodLabel.value ? `${methodLabel.value} ` : ''
  return (
    `${props.label}: central ${fmt(props.interval.central)}, ` +
    `${method}range from ${fmt(props.interval.low)} to ${fmt(props.interval.high)}.`
  )
})

/** Unsourced / degenerate bands render in a muted, dashed style. */
const unsourced = computed(
  () => isDegenerate.value || !props.provenanceComplete,
)
</script>

<template>
  <figure
    class="rounded-lg border bg-white p-4 dark:border-gray-700 dark:bg-gray-800"
  >
    <AlertBanner v-if="caveats.length > 0" variant="warning" class="mb-3">
      <ul class="list-disc space-y-1 pl-4">
        <li v-for="(caveat, i) in caveats" :key="i">{{ caveat }}</li>
      </ul>
    </AlertBanner>

    <figcaption
      class="mb-2 text-sm font-medium text-gray-700 dark:text-gray-200"
    >
      {{ label }}
    </figcaption>

    <!-- The SVG is static (no animation), so it needs no reduced-motion handling.
         All information is carried in the role="img" aria-label for screen readers;
         the numeric labels below are also visible to sighted users. -->
    <svg
      role="img"
      :aria-label="ariaLabel"
      viewBox="0 0 100 16"
      preserveAspectRatio="none"
      class="h-8 w-full"
    >
      <!-- Whisker (the low–high band) + end caps; hidden when degenerate. -->
      <g
        v-if="!isDegenerate"
        :class="
          unsourced
            ? 'stroke-gray-400 dark:stroke-gray-500'
            : 'stroke-blue-400 dark:stroke-blue-500'
        "
        stroke-width="1.2"
        :stroke-dasharray="unsourced ? '2 2' : undefined"
      >
        <line :x1="xLow" y1="8" :x2="xHigh" y2="8" />
        <line :x1="xLow" y1="4" :x2="xLow" y2="12" />
        <line :x1="xHigh" y1="4" :x2="xHigh" y2="12" />
      </g>

      <!-- Central marker (the point estimate). -->
      <line
        :x1="xCentral"
        y1="1"
        :x2="xCentral"
        y2="15"
        stroke-width="2"
        :class="
          unsourced
            ? 'stroke-gray-600 dark:stroke-gray-300'
            : 'stroke-blue-700 dark:stroke-blue-300'
        "
      />
    </svg>

    <!-- Visible numeric labels (redundant with the aria-label, for sighted users). -->
    <div
      class="mt-2 flex items-baseline justify-between gap-2 text-xs text-gray-600 dark:text-gray-300"
    >
      <span v-if="!isDegenerate"
        >{{ fmt(interval.low) }}<span class="sr-only"> (low)</span></span
      >
      <span class="text-base font-semibold text-gray-900 dark:text-gray-50">
        {{ fmt(interval.central) }}<span class="sr-only"> (central)</span>
      </span>
      <span v-if="!isDegenerate"
        >{{ fmt(interval.high) }}<span class="sr-only"> (high)</span></span
      >
    </div>

    <p
      v-if="methodLabel || unsourced"
      class="mt-1 text-xs text-gray-500 dark:text-gray-400"
    >
      <template v-if="unsourced"
        >Point estimate — uncertainty unquantified.</template
      >
      <template v-else>Band: {{ methodLabel }}.</template>
    </p>
  </figure>
</template>
