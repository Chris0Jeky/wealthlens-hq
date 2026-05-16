<script setup lang="ts">
/**
 * FivePillars — five-column grid showing the structural pillars
 * of UK wealth inequality: Wealth, Housing, Tax, Inheritance, Place.
 *
 * Each pillar card shows a number, name, key finding (with bold text),
 * and a mini inline SVG chart (sparkline, donut, bar, or column).
 * Cards are clickable and link to their respective chart views.
 *
 * Mini charts are rendered as raw SVG — no external charting library.
 */
import { computed } from 'vue'

/* ------------------------------------------------------------------ */
/* Data types                                                          */
/* ------------------------------------------------------------------ */

interface ColumnEntry {
  v: number
  label: string
}

interface Pillar {
  n: string
  name: string
  find: string
  /** Sparkline series data — rendered as line chart. */
  series?: number[]
  /** Whether the sparkline uses the red colour. */
  red?: boolean
  /** Donut chart: [mainSlice, remainder]. */
  donut?: [number, number]
  /** Horizontal bar chart: [yes%, no%]. */
  bars?: [number, number]
  /** Vertical column chart entries. */
  columns?: ColumnEntry[]
}

/* ------------------------------------------------------------------ */
/* PILLARS data — all 5 entries with exact text from design reference  */
/* ------------------------------------------------------------------ */

const PILLARS: Pillar[] = [
  {
    n: '01',
    name: 'Wealth',
    find: 'The <b>top 10%</b> own <b>57%</b> of everything — same as 1910, before the welfare state existed.',
    series: [42, 44, 47, 51, 53, 55, 56, 57],
    red: true,
  },
  {
    n: '02',
    name: 'Housing',
    find: 'A house now costs <b>8.6×</b> average earnings. Your parents paid 3×. Same job. Same house.',
    series: [3.2, 3.5, 4.1, 4.8, 5.6, 6.9, 7.8, 8.6],
    red: true,
  },
  {
    n: '03',
    name: 'Tax',
    find: '<b>92%</b> of capital gains flow to the top 1% — taxed lower than your salary.',
    donut: [92, 8],
  },
  {
    n: '04',
    name: 'Inheritance',
    find: 'Only <b>4–5%</b> of estates pay any tax. The threshold hasn\'t moved since 2009 — the year of the iPhone 3GS.',
    bars: [5, 95],
  },
  {
    n: '05',
    name: 'Place',
    find: 'Westminster: <b>£79.5k</b> per head. Blackpool: <b>£14.2k</b>. Same country. Same NHS, in theory.',
    columns: [
      { v: 79.5, label: 'WSM' },
      { v: 24.8, label: 'UK' },
      { v: 14.2, label: 'BLA' },
    ],
  },
]

/* ------------------------------------------------------------------ */
/* SVG chart builders — port of buildPillarCard() from landing.jsx     */
/* ------------------------------------------------------------------ */

/** Build a sparkline SVG path + end dot. */
function buildSparkline(series: number[], red: boolean): string {
  const W = 220
  const H = 60
  const pad = 4
  const max = Math.max(...series)
  const xs = series.map((_, i) => pad + (i * (W - pad * 2)) / (series.length - 1))
  const ys = series.map((v) => H - pad - (v / max) * (H - pad * 2 - 6))
  const d = xs.map((x, i) => `${i === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${ys[i].toFixed(1)}`).join(' ')
  const color = red ? 'var(--wl-red)' : 'var(--wl-ink)'
  return `<svg class="pillar-chart" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" aria-hidden="true">
    <path d="${d}" stroke="${color}" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
    <circle cx="${xs[xs.length - 1]}" cy="${ys[ys.length - 1]}" r="3.5" fill="${color}"/>
  </svg>`
}

/** Build a donut chart SVG. */
function buildDonut(values: [number, number]): string {
  const [a] = values
  const total = a + values[1]
  const C = 2 * Math.PI * 22
  const aLen = (a / total) * C
  return `<svg class="pillar-chart" viewBox="0 0 220 60" aria-hidden="true">
    <g transform="translate(30 30)">
      <circle r="22" cx="0" cy="0" fill="none" stroke="var(--wl-rule)" stroke-width="8"/>
      <circle r="22" cx="0" cy="0" fill="none" stroke="var(--wl-red)" stroke-width="8"
        stroke-dasharray="${aLen.toFixed(1)} ${(C - aLen).toFixed(1)}" transform="rotate(-90)"/>
    </g>
    <text x="68" y="34" font-family="IBM Plex Mono" font-size="16" font-weight="600" fill="var(--wl-red)">${a}%</text>
    <text x="68" y="50" font-family="IBM Plex Mono" font-size="9" fill="var(--wl-ink-muted)">to top 1%</text>
  </svg>`
}

/** Build a horizontal bar chart SVG. */
function buildBars(values: [number, number]): string {
  const [yes, no] = values
  const yesW = (yes / 100) * 220
  return `<svg class="pillar-chart" viewBox="0 0 220 60" aria-hidden="true">
    <rect x="0" y="22" width="${yesW.toFixed(1)}" height="14" fill="var(--wl-red)"/>
    <rect x="${(yesW + 2).toFixed(1)}" y="22" width="${((no / 100) * 220 - 2).toFixed(1)}" height="14" fill="var(--wl-rule)"/>
    <text x="0" y="16" font-family="IBM Plex Mono" font-size="9" fill="var(--wl-ink-muted)" letter-spacing="1">PAY IHT  ·  DON'T</text>
    <text x="0" y="52" font-family="IBM Plex Mono" font-size="11" font-weight="600" fill="var(--wl-red)">${yes}%</text>
    <text x="${(yesW + 10).toFixed(1)}" y="52" font-family="IBM Plex Mono" font-size="11" fill="var(--wl-ink-muted)">${no}%</text>
  </svg>`
}

/** Build a vertical column chart SVG. */
function buildColumns(cols: ColumnEntry[]): string {
  const maxV = Math.max(...cols.map((c) => c.v))
  const bars = cols
    .map((c, i) => {
      const x = 18 + i * 70
      const h = (c.v / maxV) * 40
      const y = 50 - h
      const fill = i === 0 ? 'var(--wl-red)' : 'var(--wl-ink)'
      return `<rect x="${x}" y="${y.toFixed(1)}" width="40" height="${h.toFixed(1)}" fill="${fill}"/>
      <text x="${x + 20}" y="58" text-anchor="middle" font-family="IBM Plex Mono" font-size="9" fill="var(--wl-ink-muted)">${c.label}</text>
      <text x="${x + 20}" y="${(y - 4).toFixed(1)}" text-anchor="middle" font-family="IBM Plex Mono" font-size="10" font-weight="600" fill="${fill}">£${c.v}k</text>`
    })
    .join('\n')
  return `<svg class="pillar-chart" viewBox="0 0 220 60" aria-hidden="true">${bars}</svg>`
}

/** Compute the SVG markup for a given pillar's mini chart. */
const pillarCharts = computed(() =>
  PILLARS.map((p) => {
    if (p.series) return buildSparkline(p.series, p.red ?? false)
    if (p.donut) return buildDonut(p.donut)
    if (p.bars) return buildBars(p.bars)
    if (p.columns) return buildColumns(p.columns)
    return ''
  }),
)
</script>

<template>
  <section
    class="pillars"
    data-screen-label="01 Landing — Pillars"
    aria-labelledby="pillars-heading"
  >
    <!-- Section header -->
    <div class="pillars-head">
      <div class="pillars-head-top">
        <p class="pillars-eyebrow">&darr; Five pillars</p>
        <h2 id="pillars-heading">
          Five systems decide whose Britain you get to live in.
        </h2>
        <p class="pillars-lead">
          Click any pillar to open its chart library. All data downloadable
          as CSV, PNG, SVG, embeddable anywhere.
        </p>
      </div>
    </div>

    <!-- Five-column grid -->
    <div class="pillars-grid">
      <div
        v-for="(pillar, idx) in PILLARS"
        :key="pillar.n"
        class="pillar"
        role="link"
        :tabindex="0"
        :aria-label="`Pillar ${pillar.n}: ${pillar.name}`"
      >
        <div class="pillar-top">
          <span class="pillar-num">{{ pillar.n }}</span>
          <span class="pillar-link" aria-hidden="true">&rarr;</span>
        </div>
        <div class="pillar-name">{{ pillar.name }}</div>
        <!-- eslint-disable-next-line vue/no-v-html -- trusted static content with <b> tags -->
        <div class="pillar-find" v-html="pillar.find"></div>
        <!-- eslint-disable-next-line vue/no-v-html -- trusted SVG markup -->
        <div class="pillar-chart-wrap" v-html="pillarCharts[idx]"></div>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* ============================================================
   FIVE PILLARS — structural inequality grid
   ============================================================ */
.pillars {
  padding: 96px 0;
  background: var(--wl-bg);
  border-bottom: 1px solid var(--wl-ink);
}

/* --- Section header ----------------------------------------- */
.pillars-head {
  max-width: var(--wl-max);
  margin: 0 auto 48px;
  padding: 0 32px;
}

.pillars-head-top {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 24px;
  align-items: end;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--wl-rule);
}

.pillars-eyebrow {
  font-family: var(--wl-mono);
  font-size: 11px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--wl-red);
  font-weight: 600;
  margin: 0;
}

.pillars-head h2 {
  font-family: var(--wl-serif);
  font-size: clamp(36px, 4.5vw, 56px);
  line-height: 1.02;
  letter-spacing: -0.02em;
  font-weight: 600;
  color: var(--wl-ink);
  margin: 12px 0 0;
  max-width: 22ch;
  text-wrap: balance;
}

.pillars-head h2 :deep(em) {
  font-style: italic;
  color: var(--wl-red);
  font-weight: 500;
}

.pillars-lead {
  color: var(--wl-ink-muted);
  max-width: 36ch;
  font-size: 14px;
  margin: 0;
}

/* --- Five-column grid --------------------------------------- */
.pillars-grid {
  max-width: var(--wl-max);
  margin: 0 auto;
  padding: 0 32px;
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 1px;
  background: var(--wl-ink);
  border: 1px solid var(--wl-ink);
}

/* --- Individual pillar card --------------------------------- */
.pillar {
  background: var(--wl-card);
  padding: 24px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 14px;
  transition: background 0.18s ease;
  min-height: 280px;
}

.pillar:hover {
  background: var(--wl-paper-tint);
}

.pillar:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: -2px;
  z-index: 1;
}

.pillar-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.pillar-num {
  font-family: var(--wl-mono);
  font-size: 11px;
  color: var(--wl-ink-muted);
  letter-spacing: 0.1em;
}

.pillar-link {
  font-family: var(--wl-mono);
  font-size: 11px;
  color: var(--wl-red);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-weight: 500;
}

.pillar-name {
  font-family: var(--wl-serif);
  font-size: 24px;
  font-weight: 600;
  color: var(--wl-ink);
  letter-spacing: -0.012em;
  line-height: 1.1;
}

.pillar-find {
  font-size: 13px;
  color: var(--wl-ink-muted);
  line-height: 1.5;
  min-height: 60px;
}

.pillar-find :deep(b) {
  color: var(--wl-ink);
  font-weight: 600;
}

/* --- Mini chart --------------------------------------------- */
.pillar-chart-wrap {
  height: 60px;
  margin-top: auto;
}

.pillar-chart-wrap :deep(.pillar-chart) {
  width: 100%;
  height: 60px;
  display: block;
}

/* --- Responsive --------------------------------------------- */
@media (max-width: 1024px) {
  .pillars-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .pillars {
    padding: 48px 0;
  }

  .pillars-head {
    padding: 0 16px;
  }

  .pillars-head-top {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .pillars-grid {
    grid-template-columns: 1fr;
    padding: 0 16px;
  }

  .pillar {
    min-height: auto;
    padding: 20px;
  }
}
</style>
