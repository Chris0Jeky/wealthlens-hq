<script setup lang="ts">
/**
 * WealthScaleScroller — "1 pixel = £1,000" horizontal wealth visualisation.
 *
 * Renders a horizontally scrollable bar where each pixel represents £1,000
 * of household wealth. Users scroll (or swipe on mobile) to see how wealth
 * scales become incomprehensibly large at the top end.
 *
 * Data: ONS Wealth and Assets Survey, Round 7, April 2018 to March 2020
 * URL: https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/bulletins/totalwealthingreatbritain/april2018tomarch2020
 * Accessed: 2026-05-16
 */
import { ref, computed, onMounted, onBeforeUnmount } from "vue"
import { COMPARISON_STATS, DECILE_BOUNDARIES, DECILE_DATA } from "@/utils/wealthPosition"

// --- Data constants (ONS WAS Round 7, 2018-2020) ---
// Percentile markers are derived from the SAME ONS WAS Round 7 figures the
// "Where do you fit?" calculator uses (utils/wealthPosition), so the two
// surfaces cannot contradict each other (locked by WealthScaleScroller.test.ts).

/** Scale: 1 pixel = £1,000 */
const SCALE_FACTOR = 1_000

interface WealthMarker {
  /** Position in pixels (value / SCALE_FACTOR) */
  position: number
  /** Wealth value in GBP */
  value: number
  /** Human-readable label */
  label: string
  /** Short annotation shown below the marker */
  annotation: string
  /** CSS color for the marker */
  color: string
  /** Unique id for aria references */
  id: string
}

const MARKERS: WealthMarker[] = [
  {
    position: DECILE_BOUNDARIES[0] / SCALE_FACTOR,
    value: DECILE_BOUNDARIES[0],
    label: "Bottom 10%",
    annotation: "£15,400 — 1 in 10 households have less than this",
    color: "var(--wl-red)",
    id: "marker-p10",
  },
  {
    position: DECILE_DATA[2].median / SCALE_FACTOR,
    value: DECILE_DATA[2].median,
    label: "25th percentile",
    annotation: "£82,400 — a quarter of households below this",
    color: "var(--wl-teal)",
    id: "marker-p25",
  },
  {
    position: COMPARISON_STATS.medianUK / SCALE_FACTOR,
    value: COMPARISON_STATS.medianUK,
    label: "Median (50%)",
    annotation: "£302,500 — the typical UK household",
    color: "var(--wl-ink)",
    id: "marker-median",
  },
  {
    position: 564_300 / SCALE_FACTOR,
    value: 564_300,
    label: "Mean",
    annotation: "£564,300 — pulled up by the richest",
    color: "var(--wl-teal)",
    id: "marker-mean",
  },
  {
    position: DECILE_DATA[7].median / SCALE_FACTOR,
    value: DECILE_DATA[7].median,
    label: "75th percentile",
    annotation: "£829,950 — three quarters of households below this",
    color: "var(--wl-teal)",
    id: "marker-p75",
  },
  {
    position: COMPARISON_STATS.top10Threshold / SCALE_FACTOR,
    value: COMPARISON_STATS.top10Threshold,
    label: "Top 10%",
    annotation: "£1.48m — you're richer than 90% of households",
    color: "var(--wl-red)",
    id: "marker-p90",
  },
  {
    position: 3_600_000 / SCALE_FACTOR,
    value: 3_600_000,
    label: "Top 1%",
    annotation: "£3.6m — wealthier than 99% of households",
    color: "var(--wl-red)",
    id: "marker-p99",
  },
  {
    position: 15_000_000 / SCALE_FACTOR,
    value: 15_000_000,
    label: "Top 0.1%",
    annotation: "£15m — roughly 28,700 households",
    color: "var(--wl-red)",
    id: "marker-p999",
  },
]

/**
 * Total scrollable width. We cap at £20m (20,000px) to keep the scroller
 * physically usable while still conveying the exponential scale.
 * Beyond the top 0.1% marker we show an "infinity arrow" indicating
 * wealth extends far beyond what can be shown.
 */
const TOTAL_WIDTH_PX = 20_000

/** Median position used for the "you are here" marker */
const MEDIAN_PX = COMPARISON_STATS.medianUK / SCALE_FACTOR

// --- Segment boundaries for background color bands ---
interface Segment {
  start: number
  end: number
  label: string
  color: string
}

const MEDIAN_BOUNDARY_PX = COMPARISON_STATS.medianUK / SCALE_FACTOR // 302.5
const TOP10_BOUNDARY_PX = COMPARISON_STATS.top10Threshold / SCALE_FACTOR // 1480

const SEGMENTS: Segment[] = [
  { start: 0, end: MEDIAN_BOUNDARY_PX, label: "Bottom 50%", color: "var(--seg-bottom50)" },
  {
    start: MEDIAN_BOUNDARY_PX,
    end: TOP10_BOUNDARY_PX,
    label: "50th–90th",
    color: "var(--seg-50-90)",
  },
  { start: TOP10_BOUNDARY_PX, end: 3600, label: "Top 10%", color: "var(--seg-top10)" },
  { start: 3600, end: 15000, label: "Top 1%", color: "var(--seg-top1)" },
  { start: 15000, end: TOTAL_WIDTH_PX, label: "Top 0.1%", color: "var(--seg-top01)" },
]

// --- Reactive state ---
const scrollContainer = ref<HTMLElement | null>(null)
const scrollLeft = ref(0)
const containerWidth = ref(0)

/** Progress through total scrollable width, as a percentage */
const scrollProgress = computed(() => {
  if (!containerWidth.value) return 0
  const maxScroll = TOTAL_WIDTH_PX - containerWidth.value
  if (maxScroll <= 0) return 100
  return Math.min(100, (scrollLeft.value / maxScroll) * 100)
})

/** Current approximate wealth position based on scroll */
const currentWealthPosition = computed(() => {
  return Math.round(scrollLeft.value * SCALE_FACTOR)
})

/** Format a number as GBP with appropriate shorthand */
function formatGBP(value: number): string {
  if (value >= 1_000_000_000) return `£${(value / 1_000_000_000).toFixed(1)}bn`
  if (value >= 1_000_000) return `£${(value / 1_000_000).toFixed(1)}m`
  if (value >= 1_000) return `£${(value / 1_000).toFixed(0)}k`
  return `£${value.toLocaleString("en-GB")}`
}

// --- Scroll handling ---
function onScroll() {
  if (scrollContainer.value) {
    scrollLeft.value = scrollContainer.value.scrollLeft
  }
}

function updateContainerWidth() {
  if (scrollContainer.value) {
    containerWidth.value = scrollContainer.value.clientWidth
  }
}

/** Keyboard navigation: arrow keys scroll horizontally */
function onKeydown(event: KeyboardEvent) {
  if (!scrollContainer.value) return
  const step = event.shiftKey ? 500 : 100
  if (event.key === "ArrowRight") {
    event.preventDefault()
    scrollContainer.value.scrollLeft += step
  } else if (event.key === "ArrowLeft") {
    event.preventDefault()
    scrollContainer.value.scrollLeft -= step
  } else if (event.key === "Home") {
    event.preventDefault()
    scrollContainer.value.scrollLeft = 0
  } else if (event.key === "End") {
    event.preventDefault()
    scrollContainer.value.scrollLeft = TOTAL_WIDTH_PX
  }
}

/** Scroll to the median marker for initial orientation */
function scrollToMedian() {
  if (scrollContainer.value) {
    scrollContainer.value.scrollTo({
      left: Math.max(0, MEDIAN_PX - containerWidth.value / 2),
      behavior: "smooth",
    })
  }
}

// --- Lifecycle ---
let resizeObserver: ResizeObserver | null = null

onMounted(() => {
  updateContainerWidth()
  if (scrollContainer.value && typeof ResizeObserver !== "undefined") {
    resizeObserver = new ResizeObserver(updateContainerWidth)
    resizeObserver.observe(scrollContainer.value)
    return
  }

  window.addEventListener("resize", updateContainerWidth)
})

onBeforeUnmount(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
  }
  window.removeEventListener("resize", updateContainerWidth)
})
</script>

<template>
  <div class="wealth-scroller" role="region" aria-label="Wealth scale visualisation">
    <!-- Scale legend -->
    <div class="wealth-scroller__legend">
      <span class="wealth-scroller__scale-label" aria-hidden="true">
        &larr; 1 pixel = £1,000 &rarr;
      </span>
      <button
        class="wealth-scroller__reset-btn"
        type="button"
        @click="scrollToMedian"
        aria-label="Scroll to median household wealth"
      >
        Jump to median
      </button>
    </div>

    <!-- Progress indicator -->
    <div class="wealth-scroller__progress" aria-hidden="true">
      <div class="wealth-scroller__progress-bar" :style="{ width: `${scrollProgress}%` }" />
      <span class="wealth-scroller__progress-label">
        {{ formatGBP(currentWealthPosition) }} scrolled
      </span>
    </div>

    <!-- Main scrollable area -->
    <h3 id="wealth-scale-scroll-heading" class="sr-only">
      Scrollable UK household wealth distribution
    </h3>
    <p id="wealth-scale-scroll-instructions" class="sr-only">
      Use arrow keys, Home, End, or horizontal scrolling to explore the wealth scale. Marker labels
      remain visible as you move through the scale.
    </p>
    <div
      ref="scrollContainer"
      class="wealth-scroller__container"
      tabindex="0"
      role="region"
      aria-labelledby="wealth-scale-scroll-heading"
      aria-describedby="wealth-scale-scroll-instructions wealth-scale-current-position"
      @scroll.passive="onScroll"
      @keydown="onKeydown"
    >
      <!-- Inner track with full width -->
      <div class="wealth-scroller__track" :style="{ width: `${TOTAL_WIDTH_PX}px` }">
        <!-- Colored segments -->
        <div
          v-for="seg in SEGMENTS"
          :key="seg.label"
          class="wealth-scroller__segment"
          :style="{
            left: `${seg.start}px`,
            width: `${seg.end - seg.start}px`,
            backgroundColor: seg.color,
          }"
          :aria-label="`${seg.label} wealth band`"
        />

        <!-- "You are here" median indicator -->
        <div
          class="wealth-scroller__you-marker"
          :style="{ left: `${MEDIAN_PX}px` }"
          aria-hidden="true"
        >
          <div class="wealth-scroller__you-pin" />
          <span class="wealth-scroller__you-label">You are here (median)</span>
        </div>

        <!-- Wealth markers -->
        <div
          v-for="marker in MARKERS"
          :key="marker.id"
          :id="marker.id"
          class="wealth-scroller__marker"
          :style="{ left: `${marker.position}px` }"
          role="mark"
          :aria-label="`${marker.label}: ${marker.annotation}`"
        >
          <div class="wealth-scroller__marker-line" :style="{ backgroundColor: marker.color }" />
          <div class="wealth-scroller__marker-content">
            <span class="wealth-scroller__marker-label" :style="{ color: marker.color }">
              {{ marker.label }}
            </span>
            <span class="wealth-scroller__marker-value">
              {{ formatGBP(marker.value) }}
            </span>
          </div>
        </div>

        <!-- End indicator: wealth extends beyond -->
        <div
          class="wealth-scroller__end-indicator"
          :style="{ left: `${TOTAL_WIDTH_PX - 200}px` }"
          aria-label="Wealth continues far beyond this point. The richest individual has approximately £37 billion — that would be 37 million pixels wide."
        >
          <span class="wealth-scroller__end-text">
            &rarr; The wealthiest individual (~£37bn) would be 37,000,000px from here
          </span>
        </div>
      </div>
    </div>

    <!-- Segment legend below -->
    <div class="wealth-scroller__segment-legend" aria-label="Segment colour key">
      <div v-for="seg in SEGMENTS" :key="seg.label" class="wealth-scroller__segment-key">
        <span
          class="wealth-scroller__segment-swatch"
          :style="{ backgroundColor: seg.color }"
          aria-hidden="true"
        />
        <span class="wealth-scroller__segment-name">{{ seg.label }}</span>
      </div>
    </div>

    <!-- Screen reader summary -->
    <div id="wealth-scale-current-position" class="sr-only" aria-live="polite" aria-atomic="true">
      Currently viewing approximately {{ formatGBP(currentWealthPosition) }} on the wealth scale.
    </div>
  </div>
</template>

<style scoped>
/* -- CSS custom properties for segment colors -- */
.wealth-scroller {
  --seg-bottom50: #e8f4f8;
  --seg-50-90: #b2dfdb;
  --seg-top10: #ffcc02;
  --seg-top1: #ff8a65;
  --seg-top01: #ef5350;
}

/* Dark mode overrides */
:root[data-theme="dark"] .wealth-scroller,
.dark .wealth-scroller {
  --seg-bottom50: #1a3a4a;
  --seg-50-90: #1b4332;
  --seg-top10: #5c4b00;
  --seg-top1: #5c2a00;
  --seg-top01: #5c1a1a;
}

.wealth-scroller {
  width: 100%;
  font-family: var(--wl-mono);
}

/* Legend bar */
.wealth-scroller__legend {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
  margin-bottom: 8px;
}

.wealth-scroller__scale-label {
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--wl-ink-muted);
}

.wealth-scroller__reset-btn {
  font-family: var(--wl-mono);
  font-size: 11px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  padding: 4px 12px;
  border: 1px solid var(--wl-rule-strong);
  border-radius: 3px;
  background: transparent;
  color: var(--wl-ink);
  cursor: pointer;
  transition:
    border-color 0.15s,
    color 0.15s;
}
.wealth-scroller__reset-btn:hover {
  border-color: var(--wl-red);
  color: var(--wl-red);
}
.wealth-scroller__reset-btn:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: 2px;
}

/* Progress bar */
.wealth-scroller__progress {
  position: relative;
  height: 4px;
  background: var(--wl-rule);
  border-radius: 2px;
  margin-bottom: 12px;
  overflow: hidden;
}
.wealth-scroller__progress-bar {
  height: 100%;
  background: var(--wl-red);
  transition: width 0.1s linear;
  border-radius: 2px;
}
.wealth-scroller__progress-label {
  position: absolute;
  top: 8px;
  right: 0;
  font-size: 10px;
  color: var(--wl-ink-muted);
}

/* Scrollable container */
.wealth-scroller__container {
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
  scroll-behavior: smooth;
  cursor: grab;
  border: 1px solid var(--wl-rule);
  border-radius: 4px;
  position: relative;
  height: 160px;
}
.wealth-scroller__container:active {
  cursor: grabbing;
}
.wealth-scroller__container:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: 2px;
}

/* Inner track */
.wealth-scroller__track {
  position: relative;
  height: 100%;
}

/* Colored background segments */
.wealth-scroller__segment {
  position: absolute;
  top: 0;
  height: 100%;
  opacity: 0.6;
}

/* "You are here" median marker */
.wealth-scroller__you-marker {
  position: absolute;
  top: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 10;
  pointer-events: none;
}
.wealth-scroller__you-pin {
  width: 3px;
  height: 100%;
  background: var(--wl-ink);
  opacity: 0.9;
}
.wealth-scroller__you-label {
  position: absolute;
  bottom: 8px;
  white-space: nowrap;
  font-size: 10px;
  font-weight: 700;
  color: var(--wl-ink);
  background: var(--wl-paper);
  padding: 2px 6px;
  border-radius: 2px;
  border: 1px solid var(--wl-rule-strong);
}

/* Wealth markers */
.wealth-scroller__marker {
  position: absolute;
  top: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 5;
}
.wealth-scroller__marker-line {
  width: 2px;
  height: 60%;
  opacity: 0.7;
}
.wealth-scroller__marker-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  white-space: nowrap;
  padding-top: 4px;
}
.wealth-scroller__marker-label {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.wealth-scroller__marker-value {
  font-size: 11px;
  color: var(--wl-ink-muted);
}

/* End indicator */
.wealth-scroller__end-indicator {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 5;
}
.wealth-scroller__end-text {
  font-size: 11px;
  color: var(--wl-ink-muted);
  font-style: italic;
  white-space: nowrap;
}

/* Segment legend */
.wealth-scroller__segment-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 12px;
  padding: 8px 0;
}
.wealth-scroller__segment-key {
  display: flex;
  align-items: center;
  gap: 6px;
}
.wealth-scroller__segment-swatch {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 2px;
  border: 1px solid var(--wl-rule);
}
.wealth-scroller__segment-name {
  font-size: 11px;
  color: var(--wl-ink-muted);
}

/* Screen-reader-only utility */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .wealth-scroller__container {
    height: 140px;
  }
  .wealth-scroller__legend {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  .wealth-scroller__segment-legend {
    gap: 8px;
  }
}
</style>
