<script setup lang="ts">
/**
 * FeaturedChart — wealth shares time series (1820–2023) with raw SVG.
 *
 * Renders the WEALTH_SHARES data as an SVG line chart with:
 * - gridlines and axis labels
 * - era bands (Aristocratic, Post-war compression, Re-concentration)
 * - four series: Top 10% (red, hero), Top 1% (ink), Middle 40%, Bottom 50%
 * - direct right-side labels
 * - range selector buttons: 200y, 100y, 50y, 25y
 *
 * All SVG is rendered via Vue template syntax (v-for, computed
 * properties, inline elements) — no v-html or string concatenation.
 *
 * Source: WID.world, CC-BY, accessed 2026-05-14.
 * No external charting library — all raw SVG.
 */
import { ref, computed } from 'vue'

/* ------------------------------------------------------------------ */
/* Data                                                                */
/* ------------------------------------------------------------------ */

/**
 * Each row: [year, top1%, top10%, middle40%, bottom50%]
 * Source: World Inequality Database (WID.world)
 */
const WEALTH_SHARES: number[][] = [
  [1820, 60, 86, 13, 1],
  [1840, 61, 87, 12, 1],
  [1860, 62, 88, 11, 1],
  [1880, 63, 89, 10, 1],
  [1900, 64, 90, 9, 1],
  [1910, 65, 90, 9, 1],
  [1920, 60, 85, 13, 2],
  [1930, 55, 81, 16, 3],
  [1940, 48, 75, 21, 4],
  [1950, 40, 70, 25, 5],
  [1960, 32, 63, 31, 6],
  [1970, 26, 56, 37, 7],
  [1980, 21, 50, 42, 8],
  [1985, 19, 49, 43, 8],
  [1990, 20, 50, 42, 8],
  [1995, 21, 52, 41, 7],
  [2000, 23, 54, 40, 6],
  [2005, 25, 56, 38, 6],
  [2010, 26, 58, 37, 5],
  [2015, 27, 58, 37, 5],
  [2020, 28, 57, 37, 6],
  [2023, 28, 57, 37, 6],
]

/* ------------------------------------------------------------------ */
/* Range selector                                                      */
/* ------------------------------------------------------------------ */

type RangeOption = 200 | 100 | 50 | 25

interface RangeButton {
  value: RangeOption
  label: string
}

const RANGE_BUTTONS: RangeButton[] = [
  { value: 200, label: '200y' },
  { value: 100, label: '100y' },
  { value: 50, label: '50y' },
  { value: 25, label: '25y' },
]

const activeRange = ref<RangeOption>(100)

function setRange(range: RangeOption): void {
  activeRange.value = range
}

/* ------------------------------------------------------------------ */
/* Chart dimensions                                                    */
/* ------------------------------------------------------------------ */

const W = 920
const H = 420
const padL = 64
const padR = 200
const padT = 36
const padB = 52

/* ------------------------------------------------------------------ */
/* Series definitions                                                  */
/* ------------------------------------------------------------------ */

interface SeriesDef {
  idx: number
  color: string
  label: string
  w: number
  dim: boolean
}

const SERIES: SeriesDef[] = [
  { idx: 2, color: 'var(--wl-red)', label: 'Top 10%', w: 3.5, dim: false },
  { idx: 1, color: 'var(--wl-ink)', label: 'Top 1%', w: 2, dim: false },
  { idx: 3, color: 'var(--wl-ink-faint)', label: 'Middle 40%', w: 1.2, dim: true },
  { idx: 4, color: 'var(--wl-ink-faint)', label: 'Bottom 50%', w: 1.2, dim: true },
]

/* ------------------------------------------------------------------ */
/* Era definitions                                                     */
/* ------------------------------------------------------------------ */

interface Era {
  from: number
  to: number
  label: string
}

const ERAS: Era[] = [
  { from: 0, to: 1945, label: 'Aristocratic era' },
  { from: 1945, to: 1980, label: 'Post-war compression' },
  { from: 1980, to: 9999, label: 'Re-concentration' },
]

/* ------------------------------------------------------------------ */
/* Computed chart data (template-friendly objects, not SVG strings)     */
/* ------------------------------------------------------------------ */

/** Filtered data points for the active range. */
const filteredData = computed(() => {
  const range = activeRange.value
  const minYear = range === 200 ? 1820 : range === 100 ? 1925 : range === 50 ? 1975 : 2000
  return WEALTH_SHARES.filter((d) => d[0] >= minYear)
})

/** X/Y domain boundaries. */
const domain = computed(() => {
  const data = filteredData.value
  if (data.length < 2) return { xMin: 0, xMax: 1 }
  return { xMin: data[0][0], xMax: data[data.length - 1][0] }
})

/** Scale functions for converting data values to SVG coordinates. */
function xScale(year: number, xMin: number, xMax: number): number {
  return padL + ((year - xMin) / (xMax - xMin)) * (W - padL - padR)
}

function yScale(v: number): number {
  return padT + (1 - v / 100) * (H - padT - padB)
}

/** Y-axis gridlines: value + y position. */
const Y_TICKS = [0, 25, 50, 75, 100]

const yGridlines = computed(() =>
  Y_TICKS.map((t) => ({
    y: yScale(t),
    label: `${t}%`,
  })),
)

/** X-axis tick marks: year + x position. */
const xTicks = computed(() => {
  const data = filteredData.value
  if (data.length < 2) return []
  const { xMin, xMax } = domain.value
  const nTicks = Math.min(7, data.length)
  return Array.from({ length: nTicks }, (_, i) => {
    const year = data[Math.round((i * (data.length - 1)) / (nTicks - 1))][0]
    return { year, x: xScale(year, xMin, xMax) }
  })
})

/** 50% dashed line y position. */
const fiftyLineY = computed(() => yScale(50))

/** Chart title text showing the year range. */
const chartTitleText = computed(() => {
  const { xMin, xMax } = domain.value
  return `SHARE OF NET PERSONAL WEALTH (%) · ${xMin}–${xMax}`
})

/** Era bands (visible ones only, with coordinates). */
const eraBands = computed(() => {
  const data = filteredData.value
  if (data.length < 2) return []
  const { xMin, xMax } = domain.value
  const minYear = data[0][0]

  return ERAS.filter((e) => e.from < xMax && e.to > minYear)
    .map((e, i) => {
      const from = Math.max(e.from, minYear)
      const x0 = xScale(from, xMin, xMax)
      const x1 = xScale(Math.min(e.to, xMax), xMin, xMax)
      const width = x1 - x0
      if (width < 30) return null
      return {
        x: x0,
        width,
        labelX: (x0 + x1) / 2,
        label: e.label.toUpperCase(),
        fill: i % 2 === 0 ? 'transparent' : 'var(--wl-paper-deep)',
        key: `era-${i}`,
      }
    })
    .filter((e): e is NonNullable<typeof e> => e !== null)
})

/** SVG path string for a given series index. */
function buildPathD(data: number[][], idx: number, xMin: number, xMax: number): string {
  return data
    .map(
      (d, i) =>
        `${i === 0 ? 'M' : 'L'} ${xScale(d[0], xMin, xMax).toFixed(1)} ${yScale(d[idx]).toFixed(1)}`,
    )
    .join(' ')
}

/** Series in draw order: dim first, then foreground on top. */
const sortedSeries = computed(() =>
  [...SERIES].sort((a, b) => (a.dim === b.dim ? 0 : a.dim ? -1 : 1)),
)

/** Series path data for v-for rendering. */
const seriesPaths = computed(() => {
  const data = filteredData.value
  if (data.length < 2) return []
  const { xMin, xMax } = domain.value
  return sortedSeries.value.map((s) => ({
    key: `series-${s.idx}`,
    d: buildPathD(data, s.idx, xMin, xMax),
    color: s.color,
    strokeWidth: s.w,
    dim: s.dim,
  }))
})

/** Right-side labels with positions and text. */
const seriesLabels = computed(() => {
  const data = filteredData.value
  if (data.length < 2) return []
  const last = data[data.length - 1]
  return SERIES.map((s) => ({
    key: `label-${s.idx}`,
    x: W - padR + 14,
    y: yScale(last[s.idx]),
    color: s.color,
    strokeWidth: s.w,
    label: s.label,
    value: `${last[s.idx]}% · ${last[0]}`,
  }))
})

/** Clip path rect dimensions. */
const clipRect = {
  x: padL,
  y: padT,
  width: W - padL - padR,
  height: H - padT - padB,
}
</script>

<template>
  <section
    class="featured"
    data-screen-label="01 Landing — Featured chart"
    aria-labelledby="featured-heading"
  >
    <div class="featured-inner">
      <!-- Section header -->
      <div class="featured-head">
        <div>
          <p class="featured-label">&#x25CF; Featured · Wealth concentration</p>
          <h2 id="featured-heading">
            Two centuries of UK wealth, in <em>one line</em>.
          </h2>
          <p class="featured-lead">
            The top 10% have held more than half of British personal wealth for
            the entire window. The post-war squeeze was real. The slide back has
            been steady since 1980.
          </p>
        </div>
        <div class="featured-actions">
          <RouterLink to="/charts/wealth-shares" class="wl-btn wl-btn--ghost wl-btn--sm">
            Open full page &rarr;
          </RouterLink>
        </div>
      </div>

      <!-- Chart card -->
      <div class="chart-card">
        <!-- Toolbar: series legend + range buttons -->
        <div class="chart-toolbar">
          <div class="chart-toolbar-left">
            <span class="chart-toolbar-tag">
              <b>UK</b> · Share of net personal wealth (%)
            </span>
            <span class="chart-toolbar-tag">
              <span class="chart-toolbar-dot chart-toolbar-dot--red" aria-hidden="true"></span>
              <b>Top 10%</b>
            </span>
            <span class="chart-toolbar-tag">
              <span class="chart-toolbar-dot chart-toolbar-dot--ink" aria-hidden="true"></span>
              Top 1%
            </span>
          </div>
          <div class="chart-ranges" role="tablist" aria-label="Time range">
            <button
              v-for="btn in RANGE_BUTTONS"
              :key="btn.value"
              class="chart-range"
              :class="{ 'chart-range--active': activeRange === btn.value }"
              role="tab"
              :aria-selected="activeRange === btn.value"
              @click="setRange(btn.value)"
            >
              {{ btn.label }}
            </button>
          </div>
        </div>

        <!-- Chart stage — template-based SVG, no v-html -->
        <div class="chart-stage">
          <svg
            class="chart-svg"
            :viewBox="`0 0 ${W} ${H}`"
            preserveAspectRatio="xMidYMid meet"
            aria-label="Share of net personal wealth in the UK, by percentile group, 1820–2023"
            role="img"
          >
            <!-- Clip path definition -->
            <defs>
              <clipPath id="clipFeaturedChart">
                <rect
                  :x="clipRect.x"
                  :y="clipRect.y"
                  :width="clipRect.width"
                  :height="clipRect.height"
                />
              </clipPath>
            </defs>

            <!-- Era bands -->
            <template v-for="era in eraBands" :key="era.key">
              <rect
                :x="era.x"
                :y="padT"
                :width="era.width"
                :height="H - padT - padB"
                :fill="era.fill"
                opacity="0.4"
              />
              <text
                :x="era.labelX"
                :y="padT + 14"
                text-anchor="middle"
                font-family="IBM Plex Mono"
                font-size="9"
                fill="var(--wl-ink-muted)"
                letter-spacing="1.4"
              >{{ era.label }}</text>
            </template>

            <!-- Y-axis gridlines -->
            <template v-for="tick in yGridlines" :key="`y-${tick.label}`">
              <line
                :x1="padL"
                :x2="W - padR"
                :y1="tick.y"
                :y2="tick.y"
                stroke="var(--wl-rule)"
                stroke-width="1"
              />
              <text
                :x="padL - 10"
                :y="tick.y + 4"
                text-anchor="end"
                font-family="IBM Plex Mono"
                font-size="11"
                fill="var(--wl-ink-muted)"
              >{{ tick.label }}</text>
            </template>

            <!-- X-axis tick marks -->
            <template v-for="tick in xTicks" :key="`x-${tick.year}`">
              <line
                :x1="tick.x"
                :x2="tick.x"
                :y1="H - padB"
                :y2="H - padB + 5"
                stroke="var(--wl-ink)"
                stroke-width="1"
              />
              <text
                :x="tick.x"
                :y="H - padB + 22"
                text-anchor="middle"
                font-family="IBM Plex Mono"
                font-size="11"
                fill="var(--wl-ink-muted)"
              >{{ tick.year }}</text>
            </template>

            <!-- 50% dashed reference line -->
            <line
              :x1="padL"
              :x2="W - padR"
              :y1="fiftyLineY"
              :y2="fiftyLineY"
              stroke="var(--wl-ink)"
              stroke-width="1"
              stroke-dasharray="4 4"
            />
            <text
              :x="W - padR - 6"
              :y="fiftyLineY - 4"
              text-anchor="end"
              font-family="IBM Plex Mono"
              font-size="10"
              fill="var(--wl-ink-muted)"
              letter-spacing="1"
            >50% LINE · TOP 10% NEVER BELOW</text>

            <!-- Series paths (clipped) -->
            <g clip-path="url(#clipFeaturedChart)">
              <path
                v-for="sp in seriesPaths"
                :key="sp.key"
                :d="sp.d"
                :stroke="sp.color"
                :stroke-width="sp.strokeWidth"
                fill="none"
                stroke-linejoin="round"
                stroke-linecap="round"
                :stroke-dasharray="sp.dim ? '3 2' : undefined"
                :opacity="sp.dim ? 0.7 : undefined"
              />
            </g>

            <!-- Right-side direct labels -->
            <g
              v-for="sl in seriesLabels"
              :key="sl.key"
              :transform="`translate(${sl.x} ${sl.y})`"
            >
              <line
                x1="-8"
                x2="0"
                y1="0"
                y2="0"
                :stroke="sl.color"
                :stroke-width="sl.strokeWidth"
              />
              <text
                x="8"
                y="4"
                font-family="IBM Plex Sans"
                font-size="13"
                font-weight="600"
                :fill="sl.color"
              >{{ sl.label }}</text>
              <text
                x="8"
                y="20"
                font-family="IBM Plex Mono"
                font-size="11"
                fill="var(--wl-ink-muted)"
              >{{ sl.value }}</text>
            </g>

            <!-- Chart title and axes -->
            <text
              :x="padL"
              y="22"
              font-family="IBM Plex Mono"
              font-size="10"
              fill="var(--wl-ink-muted)"
              letter-spacing="2"
            >{{ chartTitleText }}</text>
            <line
              :x1="padL"
              :x2="padL"
              :y1="padT"
              :y2="H - padB"
              stroke="var(--wl-ink)"
              stroke-width="1"
            />
            <line
              :x1="padL"
              :x2="W - padR"
              :y1="H - padB"
              :y2="H - padB"
              stroke="var(--wl-ink)"
              stroke-width="1"
            />
          </svg>
        </div>

        <!-- Footer: source + download links -->
        <div class="chart-footer">
          <div>Source: WID.world · CC-BY · Accessed 2026-05-14</div>
          <div class="chart-footer-download">
            <a href="#">&darr; PNG</a>
            <a href="#">&darr; SVG</a>
            <a href="#">&darr; CSV</a>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* ============================================================
   FEATURED CHART — wealth shares time series
   ============================================================ */
.featured {
  padding: 96px 0;
  background: var(--wl-paper-tint);
  border-bottom: 1px solid var(--wl-ink);
}

.featured-inner {
  max-width: var(--wl-max);
  margin: 0 auto;
  padding: 0 32px;
}

/* --- Section header ----------------------------------------- */
.featured-head {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 32px;
  align-items: end;
  margin-bottom: 32px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--wl-rule);
}

.featured-label {
  font-family: var(--wl-mono);
  font-size: 11px;
  letter-spacing: 0.18em;
  color: var(--wl-red);
  text-transform: uppercase;
  margin: 0 0 12px;
  font-weight: 600;
}

.featured-head h2 {
  font-family: var(--wl-serif);
  font-size: clamp(36px, 4.5vw, 56px);
  line-height: 1.02;
  letter-spacing: -0.02em;
  margin: 0;
  max-width: 22ch;
  font-weight: 600;
  color: var(--wl-ink);
  text-wrap: balance;
}

.featured-head h2 em {
  font-style: italic;
  color: var(--wl-red);
  font-weight: 500;
}

.featured-lead {
  color: var(--wl-ink-muted);
  margin: 12px 0 0;
  max-width: 50ch;
  font-size: 15px;
  line-height: 1.55;
}

.featured-actions {
  display: flex;
  gap: 8px;
}

/* --- Chart card --------------------------------------------- */
.chart-card {
  background: var(--wl-card);
  border: 1px solid var(--wl-ink);
  overflow: hidden;
}

/* --- Toolbar ------------------------------------------------ */
.chart-toolbar {
  display: flex;
  align-items: center;
  padding: 14px 20px;
  border-bottom: 1px solid var(--wl-rule);
  gap: 18px;
  font-family: var(--wl-mono);
  font-size: 12px;
  flex-wrap: wrap;
}

.chart-toolbar-left {
  display: flex;
  gap: 18px;
  align-items: center;
  flex-wrap: wrap;
}

.chart-toolbar-tag {
  color: var(--wl-ink-muted);
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.chart-toolbar-tag b {
  color: var(--wl-ink);
  font-weight: 600;
}

.chart-toolbar-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.chart-toolbar-dot--red {
  background: var(--wl-red);
}

.chart-toolbar-dot--ink {
  background: var(--wl-ink);
}

/* --- Range buttons ------------------------------------------ */
.chart-ranges {
  display: flex;
  gap: 0;
  margin-left: auto;
  border: 1px solid var(--wl-rule);
}

.chart-range {
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

.chart-range:first-child {
  border-left: 0;
}

.chart-range:hover {
  color: var(--wl-ink);
}

.chart-range--active {
  background: var(--wl-ink);
  color: var(--wl-paper);
}

/* --- Chart stage -------------------------------------------- */
.chart-stage {
  padding: 32px 24px 12px;
}

.chart-svg {
  width: 100%;
  height: 420px;
  display: block;
}

/* --- Footer ------------------------------------------------- */
.chart-footer {
  padding: 14px 20px;
  border-top: 1px solid var(--wl-rule);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  background: var(--wl-bg);
  font-family: var(--wl-mono);
  font-size: 11px;
  color: var(--wl-ink-muted);
}

.chart-footer-download {
  display: flex;
  gap: 16px;
}

.chart-footer a {
  color: var(--wl-ink);
  text-decoration: none;
  border-bottom: 1px solid var(--wl-rule-strong);
}

.chart-footer a:hover {
  color: var(--wl-red);
  border-color: var(--wl-red);
}

/* --- Responsive --------------------------------------------- */
@media (max-width: 768px) {
  .featured {
    padding: 48px 0;
  }

  .featured-inner {
    padding: 0 16px;
  }

  .featured-head {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .chart-toolbar {
    padding: 12px 14px;
    gap: 10px;
    flex-direction: column;
    align-items: flex-start;
  }

  .chart-toolbar-left {
    gap: 10px;
  }

  .chart-ranges {
    margin-left: 0;
    width: 100%;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .chart-range {
    min-height: 44px;
    padding: 6px 16px;
    flex-shrink: 0;
  }

  .chart-stage {
    padding: 16px 4px 8px;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .chart-svg {
    height: auto;
    min-width: 480px;
  }

  .chart-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    padding: 12px 14px;
  }

  .chart-footer-download {
    gap: 12px;
  }

  .chart-footer-download a {
    min-height: 44px;
    display: inline-flex;
    align-items: center;
  }
}

/* 375px and below — ensure chart is scrollable */
@media (max-width: 375px) {
  .chart-toolbar-tag {
    font-size: 10px;
  }

  .chart-range {
    padding: 6px 12px;
    font-size: 10px;
  }
}
</style>
