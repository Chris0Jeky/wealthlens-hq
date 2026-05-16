<script setup lang="ts">
/**
 * WealthFlowSankey — "If Britain were 100 households" SVG visualisation.
 *
 * Renders a Sankey-style flow diagram showing the distribution of UK
 * household wealth. 100 people on the left, £100 on the right, with
 * cubic-bezier ribbons connecting the proportional bars.
 *
 * Data: ONS Wealth & Assets Survey · WID UK · 2023
 *
 * Three groups:
 *   Top 10% — 10 people, £57 of wealth (red)
 *   Middle 40% — 40 people, £37 (ink)
 *   Bottom 50% — 50 people, £6 (faint)
 *
 * Ribbons animate in on mount with staggered scaleX transitions.
 */
import { ref, onMounted } from 'vue'

/* ------------------------------------------------------------------ */
/* Flow data                                                           */
/* ------------------------------------------------------------------ */

interface FlowGroup {
  /** Number of people (out of 100) */
  people: number
  /** Amount of money (out of £100) */
  money: number
  /** CSS custom property for the group's colour */
  colorVar: string
  /** Display name */
  name: string
  /** Per-person share label */
  perPerson: string
}

const FLOW_GROUPS: FlowGroup[] = [
  { people: 10, money: 57, colorVar: '--wl-red', name: 'Top 10%', perPerson: '£5.70 each' },
  { people: 40, money: 37, colorVar: '--wl-ink', name: 'Middle 40%', perPerson: '£0.93 each' },
  { people: 50, money: 6, colorVar: '--wl-ink-faint', name: 'Bottom 50%', perPerson: '£0.12 each' },
]

/* ------------------------------------------------------------------ */
/* SVG geometry constants                                              */
/* ------------------------------------------------------------------ */

const W = 480
const H = 600
const TOP = 110
const BOT = 540
const BAR_H = BOT - TOP

const PEOPLE_X = 132
const PEOPLE_W = 16
const MONEY_X = 332
const MONEY_W = 16

/* ------------------------------------------------------------------ */
/* Computed SVG geometry per group                                     */
/* ------------------------------------------------------------------ */

interface GroupGeometry {
  group: FlowGroup
  index: number
  color: string
  /** People bar */
  pY0: number
  pY1: number
  /** Money bar */
  mY0: number
  mY1: number
  /** Ribbon path d attribute */
  ribbonPath: string
  /** Fill opacity for the ribbon */
  ribbonOpacity: number
  /** Centre Y for label positioning */
  pMidY: number
  mMidY: number
}

function computeGeometry(): GroupGeometry[] {
  let pY = TOP
  let mY = TOP
  return FLOW_GROUPS.map((g, i) => {
    const pY0 = pY
    const pY1 = pY + BAR_H * g.people / 100
    const mY0 = mY
    const mY1 = mY + BAR_H * g.money / 100
    const color = `var(${g.colorVar})`

    // Cubic bezier ribbon connecting people bar to money bar
    const x0 = PEOPLE_X + PEOPLE_W
    const x1 = MONEY_X
    const cx0 = x0 + (x1 - x0) * 0.55
    const cx1 = x0 + (x1 - x0) * 0.45

    const ribbonPath = [
      `M ${x0} ${pY0}`,
      `C ${cx0} ${pY0}, ${cx1} ${mY0}, ${x1} ${mY0}`,
      `L ${x1} ${mY1}`,
      `C ${cx1} ${mY1}, ${cx0} ${pY1}, ${x0} ${pY1}`,
      'Z',
    ].join(' ')

    const ribbonOpacity = i === 0 ? 0.55 : i === 1 ? 0.32 : 0.18

    const result: GroupGeometry = {
      group: g,
      index: i,
      color,
      pY0,
      pY1,
      mY0,
      mY1,
      ribbonPath,
      ribbonOpacity,
      pMidY: (pY0 + pY1) / 2,
      mMidY: (mY0 + mY1) / 2,
    }

    pY = pY1
    mY = mY1
    return result
  })
}

const groups = computeGeometry()

/* ------------------------------------------------------------------ */
/* Ribbon entrance animation                                           */
/* ------------------------------------------------------------------ */

const ribbonRefs = ref<(SVGPathElement | null)[]>([])

function setRibbonRef(el: SVGPathElement | null, index: number) {
  ribbonRefs.value[index] = el
}

onMounted(() => {
  ribbonRefs.value.forEach((ribbon, i) => {
    if (!ribbon) return
    ribbon.style.transformOrigin = 'left center'
    ribbon.style.transform = 'scaleX(0)'
    ribbon.style.transition = `transform 0.9s cubic-bezier(0.22, 0.7, 0.18, 1) ${0.15 + i * 0.18}s`
    requestAnimationFrame(() => {
      ribbon.style.transform = 'scaleX(1)'
    })
  })
})

/* ------------------------------------------------------------------ */
/* Footer positioning                                                  */
/* ------------------------------------------------------------------ */

const footerLineY = H - 60
const footerTextY = H - 38
const footerSrcY = H - 16
</script>

<template>
  <div
    class="hero-lens-stage"
    aria-label="Wealth flow: of every £100 of UK household wealth, £57 goes to 10 households, £6 goes to 50."
  >
    <svg
      :viewBox="`0 0 ${W} ${H}`"
      class="flow-svg"
      preserveAspectRatio="xMidYMid meet"
      role="img"
      aria-label="Of every £100 of UK wealth, £57 goes to the top 10 households, £6 to the bottom 50."
    >
      <!-- Headers -->
      <text
        :x="PEOPLE_X + PEOPLE_W / 2"
        y="56"
        text-anchor="middle"
        class="flow-h"
      >
        100 PEOPLE
      </text>
      <text
        :x="PEOPLE_X + PEOPLE_W / 2"
        y="76"
        text-anchor="middle"
        class="flow-sub"
      >
        UK households, sorted by wealth
      </text>
      <text
        :x="MONEY_X + MONEY_W / 2"
        y="56"
        text-anchor="middle"
        class="flow-h"
      >
        £100 OF WEALTH
      </text>
      <text
        :x="MONEY_X + MONEY_W / 2"
        y="76"
        text-anchor="middle"
        class="flow-sub"
      >
        every pound the UK owns
      </text>

      <!-- Top/bottom bracket lines -->
      <line
        :x1="PEOPLE_X - 6" :y1="TOP"
        :x2="PEOPLE_X + PEOPLE_W + 6" :y2="TOP"
        stroke="var(--wl-ink)" stroke-width="1"
      />
      <line
        :x1="PEOPLE_X - 6" :y1="BOT"
        :x2="PEOPLE_X + PEOPLE_W + 6" :y2="BOT"
        stroke="var(--wl-ink)" stroke-width="1"
      />
      <line
        :x1="MONEY_X - 6" :y1="TOP"
        :x2="MONEY_X + MONEY_W + 6" :y2="TOP"
        stroke="var(--wl-ink)" stroke-width="1"
      />
      <line
        :x1="MONEY_X - 6" :y1="BOT"
        :x2="MONEY_X + MONEY_W + 6" :y2="BOT"
        stroke="var(--wl-ink)" stroke-width="1"
      />

      <!-- Flow groups: bars, ribbons, labels -->
      <template v-for="g in groups" :key="g.index">
        <!-- People bar segment -->
        <rect
          class="flow-bar"
          :x="PEOPLE_X"
          :y="g.pY0"
          :width="PEOPLE_W"
          :height="g.pY1 - g.pY0"
          :fill="g.color"
        />
        <!-- Money bar segment -->
        <rect
          class="flow-bar"
          :x="MONEY_X"
          :y="g.mY0"
          :width="MONEY_W"
          :height="g.mY1 - g.mY0"
          :fill="g.color"
        />
        <!-- Sankey ribbon -->
        <path
          :ref="(el) => setRibbonRef(el as SVGPathElement | null, g.index)"
          class="flow-ribbon"
          :d="g.ribbonPath"
          :fill="g.color"
          :fill-opacity="g.ribbonOpacity"
        />
        <!-- People side label -->
        <text
          :x="PEOPLE_X - 16"
          :y="g.pMidY - 4"
          text-anchor="end"
          class="flow-pcount"
          :fill="g.color"
        >
          {{ g.group.people }}
        </text>
        <text
          :x="PEOPLE_X - 16"
          :y="g.pMidY + 12"
          text-anchor="end"
          class="flow-plabel"
        >
          people
        </text>
        <!-- Money side label -->
        <text
          :x="MONEY_X + MONEY_W + 16"
          :y="g.mMidY - 4"
          text-anchor="start"
          class="flow-mvalue"
          :fill="g.color"
        >
          £{{ g.group.money }}
        </text>
        <text
          :x="MONEY_X + MONEY_W + 16"
          :y="g.mMidY + 12"
          text-anchor="start"
          class="flow-mlabel"
        >
          {{ g.group.name }}
        </text>
        <text
          :x="MONEY_X + MONEY_W + 16"
          :y="g.mMidY + 26"
          text-anchor="start"
          class="flow-mfine"
        >
          {{ g.group.perPerson }}
        </text>
      </template>

      <!-- Footer punchline -->
      <line
        x1="40"
        :y1="footerLineY"
        :x2="W - 40"
        :y2="footerLineY"
        stroke="var(--wl-rule)"
        stroke-width="1"
      />
      <text
        :x="W / 2"
        :y="footerTextY"
        text-anchor="middle"
        class="flow-punch"
      >
        <tspan class="flow-punch-red">10 households</tspan>
        <tspan> own more than the other</tspan>
        <tspan class="flow-punch-bold"> 90</tspan>
        <tspan> combined.</tspan>
      </text>
      <text
        :x="W / 2"
        :y="footerSrcY"
        text-anchor="middle"
        class="flow-src"
      >
        Source: ONS Wealth &amp; Assets Survey · WID UK · 2023
      </text>
    </svg>

    <!-- Corner tag -->
    <div class="flow-corner-tag">
      <span class="flow-corner-dot" aria-hidden="true"></span>
      If Britain were 100 households
    </div>
  </div>
</template>

<style scoped>
/* ============================================================
   Wealth Flow Sankey — "If Britain were 100 households"
   ============================================================ */
.hero-lens-stage {
  position: relative;
  aspect-ratio: 4 / 5;
  background: var(--wl-paper-tint);
  border: 1px solid var(--wl-ink);
  overflow: hidden;
}

.flow-svg {
  width: 100%;
  height: 100%;
  display: block;
}

/* --- SVG text classes --------------------------------------- */
.flow-svg .flow-h {
  font-family: var(--wl-mono);
  font-size: 13px;
  letter-spacing: 0.18em;
  fill: var(--wl-ink);
  font-weight: 600;
  text-transform: uppercase;
}

.flow-svg .flow-sub {
  font-family: var(--wl-sans);
  font-size: 11px;
  fill: var(--wl-ink-muted);
  letter-spacing: 0.04em;
}

.flow-svg .flow-pcount {
  font-family: var(--wl-serif);
  font-size: 28px;
  font-weight: 600;
  letter-spacing: -0.02em;
  font-variant-numeric: tabular-nums;
}

.flow-svg .flow-plabel {
  font-family: var(--wl-mono);
  font-size: 10px;
  fill: var(--wl-ink-muted);
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.flow-svg .flow-mvalue {
  font-family: var(--wl-serif);
  font-size: 30px;
  font-weight: 600;
  letter-spacing: -0.02em;
  font-variant-numeric: tabular-nums;
}

.flow-svg .flow-mlabel {
  font-family: var(--wl-sans);
  font-size: 13px;
  fill: var(--wl-ink);
  font-weight: 600;
  letter-spacing: -0.005em;
}

.flow-svg .flow-mfine {
  font-family: var(--wl-mono);
  font-size: 10px;
  fill: var(--wl-ink-muted);
  letter-spacing: 0.04em;
}

.flow-svg .flow-punch {
  font-family: var(--wl-serif);
  font-size: 15px;
  fill: var(--wl-ink);
  font-style: italic;
}

.flow-svg .flow-punch-red {
  fill: var(--wl-red);
  font-weight: 600;
  font-style: normal;
}

.flow-svg .flow-punch-bold {
  fill: var(--wl-ink);
  font-weight: 700;
  font-style: normal;
}

.flow-svg .flow-src {
  font-family: var(--wl-mono);
  font-size: 9px;
  fill: var(--wl-ink-muted);
  letter-spacing: 0.1em;
}

/* --- Corner tag --------------------------------------------- */
.flow-corner-tag {
  position: absolute;
  top: 14px;
  right: 14px;
  font-family: var(--wl-mono);
  font-size: 10px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--wl-ink-muted);
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.flow-corner-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--wl-red);
  animation: flow-pulse 2s infinite;
}

@keyframes flow-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.35; }
}

/* --- Responsive --------------------------------------------- */
@media (max-width: 768px) {
  .hero-lens-stage {
    aspect-ratio: 3 / 4;
    max-width: 400px;
    margin: 0 auto;
  }
}
</style>
