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
/* Computed SVG                                                        */
/* ------------------------------------------------------------------ */

const chartSvg = computed(() => {
  const range = activeRange.value
  const minYear = range === 200 ? 1820 : range === 100 ? 1925 : range === 50 ? 1975 : 2000
  const data = WEALTH_SHARES.filter((d) => d[0] >= minYear)
  if (data.length < 2) return ''

  const xMin = data[0][0]
  const xMax = data[data.length - 1][0]

  const x = (year: number) => padL + ((year - xMin) / (xMax - xMin)) * (W - padL - padR)
  const yScale = (v: number) => padT + (1 - v / 100) * (H - padT - padB)

  // Gridlines
  const yTicks = [0, 25, 50, 75, 100]
  const grid = yTicks
    .map(
      (t) => `
    <line x1="${padL}" x2="${W - padR}" y1="${yScale(t)}" y2="${yScale(t)}"
      stroke="var(--wl-rule)" stroke-width="1"/>
    <text x="${padL - 10}" y="${yScale(t) + 4}" text-anchor="end"
      font-family="IBM Plex Mono" font-size="11" fill="var(--wl-ink-muted)">${t}%</text>`,
    )
    .join('')

  // X axis ticks
  const nTicks = Math.min(7, data.length)
  const xTicks = Array.from(
    { length: nTicks },
    (_, i) => data[Math.round((i * (data.length - 1)) / (nTicks - 1))][0],
  )
  const xAxis = xTicks
    .map(
      (t) => `
    <line x1="${x(t)}" x2="${x(t)}" y1="${H - padB}" y2="${H - padB + 5}"
      stroke="var(--wl-ink)" stroke-width="1"/>
    <text x="${x(t)}" y="${H - padB + 22}" text-anchor="middle"
      font-family="IBM Plex Mono" font-size="11" fill="var(--wl-ink-muted)">${t}</text>`,
    )
    .join('')

  // 50% dashed line
  const fifty = `
    <line x1="${padL}" x2="${W - padR}" y1="${yScale(50)}" y2="${yScale(50)}"
      stroke="var(--wl-ink)" stroke-width="1" stroke-dasharray="4 4"/>
    <text x="${W - padR - 6}" y="${yScale(50) - 4}" text-anchor="end"
      font-family="IBM Plex Mono" font-size="10" fill="var(--wl-ink-muted)"
      letter-spacing="1">50% LINE · TOP 10% NEVER BELOW</text>`

  // Era bands
  const eraBands = ERAS.filter((e) => e.from < xMax && e.to > minYear)
    .map((e, i) => {
      const from = Math.max(e.from, minYear)
      const x0 = x(from)
      const x1 = x(Math.min(e.to, xMax))
      if (x1 - x0 < 30) return ''
      return `
      <rect x="${x0}" y="${padT}" width="${x1 - x0}" height="${H - padT - padB}"
        fill="${i % 2 === 0 ? 'transparent' : 'var(--wl-paper-deep)'}" opacity="0.4"/>
      <text x="${(x0 + x1) / 2}" y="${padT + 14}" text-anchor="middle"
        font-family="IBM Plex Mono" font-size="9" fill="var(--wl-ink-muted)"
        letter-spacing="1.4">${e.label.toUpperCase()}</text>`
    })
    .join('')

  // Series paths — build path string for a series index
  function buildPath(idx: number): string {
    return data
      .map((d, i) => `${i === 0 ? 'M' : 'L'} ${x(d[0]).toFixed(1)} ${yScale(d[idx]).toFixed(1)}`)
      .join(' ')
  }

  // Draw dim series first, then foreground on top
  const drawOrder = [...SERIES].sort((a, b) => (a.dim === b.dim ? 0 : a.dim ? -1 : 1))
  const paths = drawOrder
    .map(
      (s) => `
    <path d="${buildPath(s.idx)}" stroke="${s.color}" stroke-width="${s.w}" fill="none"
      stroke-linejoin="round" stroke-linecap="round"
      ${s.dim ? 'stroke-dasharray="3 2" opacity="0.7"' : ''}/>`,
    )
    .join('')

  // Right-side direct labels
  const last = data[data.length - 1]
  const labels = SERIES.map(
    (s) => `
    <g transform="translate(${W - padR + 14} ${yScale(last[s.idx])})">
      <line x1="-8" x2="0" y1="0" y2="0" stroke="${s.color}" stroke-width="${s.w}"/>
      <text x="8" y="4" font-family="IBM Plex Sans" font-size="13" font-weight="600" fill="${s.color}">${s.label}</text>
      <text x="8" y="20" font-family="IBM Plex Mono" font-size="11" fill="var(--wl-ink-muted)">${last[s.idx]}% · ${last[0]}</text>
    </g>`,
  ).join('')

  // Chart title, axes
  const axes = `
    <text x="${padL}" y="22" font-family="IBM Plex Mono" font-size="10"
      fill="var(--wl-ink-muted)" letter-spacing="2">SHARE OF NET PERSONAL WEALTH (%) · ${xMin}–${xMax}</text>
    <line x1="${padL}" x2="${padL}" y1="${padT}" y2="${H - padB}" stroke="var(--wl-ink)" stroke-width="1"/>
    <line x1="${padL}" x2="${W - padR}" y1="${H - padB}" y2="${H - padB}" stroke="var(--wl-ink)" stroke-width="1"/>`

  return `
    <defs><clipPath id="clipFeaturedChart"><rect x="${padL}" y="${padT}" width="${W - padL - padR}" height="${H - padT - padB}"/></clipPath></defs>
    ${eraBands}
    ${grid}
    ${xAxis}
    ${fifty}
    <g clip-path="url(#clipFeaturedChart)">${paths}</g>
    ${labels}
    ${axes}
  `
})
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

        <!-- Chart stage -->
        <div class="chart-stage">
          <!-- eslint-disable-next-line vue/no-v-html -- trusted computed SVG -->
          <svg
            class="chart-svg"
            :viewBox="`0 0 ${W} ${H}`"
            preserveAspectRatio="xMidYMid meet"
            aria-label="Share of net personal wealth in the UK, by percentile group, 1820–2023"
            role="img"
            v-html="chartSvg"
          ></svg>
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
  }

  .chart-ranges {
    margin-left: 0;
  }

  .chart-stage {
    padding: 16px 8px 8px;
  }

  .chart-svg {
    height: 260px;
  }

  .chart-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    padding: 12px 14px;
  }
}
</style>
