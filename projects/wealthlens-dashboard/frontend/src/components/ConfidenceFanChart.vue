<script setup lang="ts">
import { computed } from 'vue'
import AlertBanner from '@/components/AlertBanner.vue'
import type { ConfidenceFanChartProps, IntervalMethod } from '@/types/simulator'

const props = withDefaults(defineProps<ConfidenceFanChartProps>(), {
  currency: '£',
  unit: 'bn',
  decimals: 2,
  caveats: () => [],
  provenanceComplete: true,
})

/** Plot geometry in the SVG's own (unstretched) user units. */
const PLOT_LEFT = 10
const PLOT_RIGHT = 90
const PLOT_WIDTH = PLOT_RIGHT - PLOT_LEFT

function fmt(value: number): string {
  return `${props.currency}${value.toFixed(props.decimals)}${props.unit}`
}

/**
 * The component is typed (`interval: Interval`), but a real payload from the
 * future API bridge could still carry a missing or non-finite value (NaN/Infinity
 * — e.g. a model that emitted an undefined revenue figure). Rather than render a
 * silent "NaN" or a broken SVG, we detect that loudly and show an "unavailable"
 * state — consistent with the project's fail-loud data-integrity stance.
 */
const isValid = computed(() => {
  const iv = props.interval
  return (
    iv != null &&
    Number.isFinite(iv.low) &&
    Number.isFinite(iv.central) &&
    Number.isFinite(iv.high)
  )
})

const span = computed(() => props.interval.high - props.interval.low)
const isDegenerate = computed(() => span.value <= 0)

/**
 * Render (and describe) as a bare point estimate when the band is degenerate OR
 * the run is unsourced. Both the visual band and the accessible name gate on this
 * single flag so they can never disagree (a drawn band with a "point estimate"
 * caption would be a data-integrity contradiction).
 */
const unsourced = computed(
  () => isDegenerate.value || !props.provenanceComplete,
)

/** Map a value in [low, high] to the plot's x coordinate (clamped to the band). */
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
  return map[props.intervalMethod]
})

const ariaLabel = computed(() => {
  if (unsourced.value) {
    return `${props.label}: ${fmt(props.interval.central)} (point estimate; uncertainty unquantified).`
  }
  return (
    `${props.label}: central ${fmt(props.interval.central)}, ` +
    `${methodLabel.value} range from ${fmt(props.interval.low)} to ${fmt(props.interval.high)}.`
  )
})
</script>

<template>
  <div>
    <!-- The caveat banner is a sibling ABOVE the figure (not a figure child) so the
         figcaption stays the first child of <figure>, per the HTML spec. -->
    <AlertBanner v-if="caveats.length > 0" variant="warning" class="mb-3">
      <ul class="list-disc space-y-1 pl-4">
        <li v-for="(caveat, i) in caveats" :key="i">{{ caveat }}</li>
      </ul>
    </AlertBanner>

    <figure
      v-if="isValid"
      class="rounded-lg border border-wl-rule bg-wl-card p-4"
    >
      <figcaption class="mb-2 text-sm font-medium text-wl-ink">
        {{ label }}
      </figcaption>

      <!-- Static SVG (no animation) → reduced-motion-safe by construction. All data
           is carried in the role="img" aria-label; the numbers below are the visible
           equivalent. vector-effect="non-scaling-stroke" keeps stroke widths in
           device pixels despite the non-uniform preserveAspectRatio="none" stretch. -->
      <svg
        role="img"
        :aria-label="ariaLabel"
        viewBox="0 0 100 16"
        preserveAspectRatio="none"
        class="h-8 w-full"
      >
        <!-- Whisker (the low–high band) + end caps. Drawn ONLY for a sourced,
             non-degenerate band so the visual never contradicts the "point estimate"
             accessible name. Non-text contrast (WCAG 1.4.11, 3:1 floor): blue-600 on
             white = 5.2:1; blue-400 on the dark card = ~4:1. -->
        <g
          v-if="!unsourced"
          class="stroke-blue-600 dark:stroke-blue-400"
          stroke-width="1.2"
          vector-effect="non-scaling-stroke"
        >
          <line :x1="xLow" y1="8" :x2="xHigh" y2="8" />
          <line :x1="xLow" y1="4" :x2="xLow" y2="12" />
          <line :x1="xHigh" y1="4" :x2="xHigh" y2="12" />
        </g>

        <!-- Central point-estimate marker. blue-700/300 (sourced) and gray-600/300
             (unsourced) both exceed 6.7:1 against their backgrounds. -->
        <line
          :x1="xCentral"
          y1="1"
          :x2="xCentral"
          y2="15"
          stroke-width="2"
          vector-effect="non-scaling-stroke"
          :class="
            unsourced
              ? 'stroke-gray-600 dark:stroke-gray-300'
              : 'stroke-blue-700 dark:stroke-blue-300'
          "
        />
      </svg>

      <!-- Visible numeric labels (the sighted equivalent of the aria-label). The
           low/high bounds gate on the same `unsourced` flag as the whisker. -->
      <div
        class="mt-2 flex items-baseline justify-between gap-2 text-xs text-wl-ink-muted"
      >
        <span v-if="!unsourced"
          >{{ fmt(interval.low) }}<span class="sr-only"> (low)</span></span
        >
        <span class="text-base font-semibold text-wl-ink">
          {{ fmt(interval.central) }}<span class="sr-only"> (central)</span>
        </span>
        <span v-if="!unsourced"
          >{{ fmt(interval.high) }}<span class="sr-only"> (high)</span></span
        >
      </div>

      <p class="mt-1 text-xs text-wl-ink-faint">
        <template v-if="unsourced"
          >Point estimate — uncertainty unquantified.</template
        >
        <template v-else>Band: {{ methodLabel }}.</template>
      </p>
    </figure>

    <!-- Fail loud on malformed/non-finite data rather than rendering a silent NaN. -->
    <figure
      v-else
      role="status"
      class="rounded-lg border border-wl-rule bg-wl-card p-4 text-sm text-wl-ink-muted"
    >
      <figcaption class="mb-1 font-medium text-wl-ink">{{ label }}</figcaption>
      Interval data unavailable.
    </figure>
  </div>
</template>
