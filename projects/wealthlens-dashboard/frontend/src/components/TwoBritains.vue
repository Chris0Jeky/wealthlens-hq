<script setup lang="ts">
/**
 * TwoBritains — side-by-side perspective comparison of two UK households.
 *
 * Left panel: "Born to it" (top decile) with ink colour scheme.
 * Right panel: "Pays for it" (bottom half) with red accents.
 * Both panels have 3D perspective tilt that reduces on hover.
 *
 * All statistics are sourced from ONS WAS R7, IFS 2024, and
 * Resolution Foundation 2024.
 */

/* ------------------------------------------------------------------ */
/* Data types                                                          */
/* ------------------------------------------------------------------ */

interface StatBlock {
  big: string
  label: string
}

interface DayItem {
  question: string
  answer: string
}

interface SideData {
  pip: 'ink' | 'red'
  label: string
  heading: string
  stats: StatBlock[]
  dayList: DayItem[]
  quote: string
  quoteSource: string
}

/* ------------------------------------------------------------------ */
/* Static content — matches design reference exactly                   */
/* ------------------------------------------------------------------ */

const LEFT_SIDE: SideData = {
  pip: 'ink',
  label: 'Born to it · top decile household',
  heading: 'Owns the home. Owns the time. Owns the choice.',
  stats: [
    { big: '£1.3M', label: 'Median net wealth — mostly property & pension' },
    { big: '26%', label: 'Effective tax rate — most income from capital, not work' },
    { big: '£250k', label: 'Median inheritance — typically untaxed under threshold' },
  ],
  dayList: [
    { question: 'Decides this morning:', answer: 'which year to retire.' },
    { question: 'Worries about:', answer: 'the boiler. The dog.' },
    { question: 'Kids will inherit:', answer: 'a flat. A network. A floor.' },
  ],
  quote: 'Inheritance was never <em>if</em>. Only <em>when, and how much.</em>',
  quoteSource: '— Composite. Source: ONS WAS R7, IFS 2024',
}

const RIGHT_SIDE: SideData = {
  pip: 'red',
  label: 'Pays for it · bottom‑half household',
  heading: 'Rents the home. Rents the time. Rents the choice.',
  stats: [
    { big: '£12k', label: 'Median net wealth — about one bad month from zero' },
    { big: '33%', label: 'Effective tax rate on £40k PAYE — work is taxed harder than wealth' },
    { big: '£3k', label: 'Median inheritance — if any arrives at all' },
  ],
  dayList: [
    { question: 'Decides this morning:', answer: 'which bill to delay.' },
    { question: 'Worries about:', answer: 'the next rent rise. The next text.' },
    { question: 'Kids will inherit:', answer: 'the same rent rise. Earlier.' },
  ],
  quote: 'Saving for a deposit feels the way <em>going to the moon</em> felt to my grandparents.',
  quoteSource: '— Composite. Source: ONS, Resolution Foundation 2024',
}
</script>

<template>
  <section
    class="two-b"
    data-screen-label="01 Landing — Two Britains"
    aria-labelledby="two-b-heading"
  >
    <div class="two-b-inner">
      <!-- Section header -->
      <div class="two-b-head">
        <p class="two-b-eyebrow">&#x25CF; Two Britains, one passport</p>
        <h2 id="two-b-heading">Same Tuesday. Two completely different days.</h2>
        <p>
          Both are real households, both pay taxes here, both watch the same
          news. The decisions they make over coffee are not the same decisions
          at all.
        </p>
      </div>

      <!-- Perspective split -->
      <div class="two-b-split">
        <!-- Left panel: top decile -->
        <div class="two-b-side two-b-side--left">
          <p class="two-b-label">
            <span class="two-b-pip two-b-pip--ink" aria-hidden="true"></span>
            {{ LEFT_SIDE.label }}
          </p>
          <h3>{{ LEFT_SIDE.heading }}</h3>

          <div
            v-for="(stat, i) in LEFT_SIDE.stats"
            :key="i"
            class="two-b-stat"
          >
            <div class="two-b-stat-big">{{ stat.big }}</div>
            <div class="two-b-stat-label">{{ stat.label }}</div>
          </div>

          <ul class="two-b-day-list">
            <li v-for="(item, i) in LEFT_SIDE.dayList" :key="i">
              <span class="two-b-day-q">{{ item.question }}</span>
              {{ item.answer }}
            </li>
          </ul>

          <!-- eslint-disable-next-line vue/no-v-html -- trusted static content -->
          <div class="two-b-quote" v-html="LEFT_SIDE.quote"></div>
          <span class="two-b-quote-who">{{ LEFT_SIDE.quoteSource }}</span>
        </div>

        <!-- Right panel: bottom half -->
        <div class="two-b-side two-b-side--right">
          <p class="two-b-label">
            <span class="two-b-pip two-b-pip--red" aria-hidden="true"></span>
            {{ RIGHT_SIDE.label }}
          </p>
          <h3>{{ RIGHT_SIDE.heading }}</h3>

          <div
            v-for="(stat, i) in RIGHT_SIDE.stats"
            :key="i"
            class="two-b-stat"
          >
            <div class="two-b-stat-big">{{ stat.big }}</div>
            <div class="two-b-stat-label">{{ stat.label }}</div>
          </div>

          <ul class="two-b-day-list">
            <li v-for="(item, i) in RIGHT_SIDE.dayList" :key="i">
              <span class="two-b-day-q">{{ item.question }}</span>
              {{ item.answer }}
            </li>
          </ul>

          <!-- eslint-disable-next-line vue/no-v-html -- trusted static content -->
          <div class="two-b-quote" v-html="RIGHT_SIDE.quote"></div>
          <span class="two-b-quote-who">{{ RIGHT_SIDE.quoteSource }}</span>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* ============================================================
   TWO BRITAINS — perspective split comparison
   ============================================================ */
.two-b {
  padding: 96px 0;
  background: var(--wl-paper-tint);
  border-bottom: 1px solid var(--wl-ink);
  overflow: hidden;
}

.two-b-inner {
  max-width: var(--wl-max);
  margin: 0 auto;
  padding: 0 32px;
}

/* --- Section header ----------------------------------------- */
.two-b-head {
  margin-bottom: 48px;
  max-width: 60ch;
}

.two-b-eyebrow {
  font-family: var(--wl-mono);
  font-size: 11px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--wl-red);
  font-weight: 600;
  margin: 0 0 12px;
}

.two-b-head h2 {
  font-family: var(--wl-serif);
  font-size: clamp(36px, 4.5vw, 56px);
  line-height: 1.02;
  letter-spacing: -0.02em;
  font-weight: 600;
  color: var(--wl-ink);
  margin: 0 0 16px;
  text-wrap: balance;
}

.two-b-head p {
  font-size: 17px;
  color: var(--wl-ink-muted);
  margin: 0;
  line-height: 1.55;
}

/* --- Split container with perspective ----------------------- */
.two-b-split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  border: 1px solid var(--wl-ink);
  background: var(--wl-ink);
  gap: 1px;
  perspective: 1400px;
}

/* --- Side panels -------------------------------------------- */
.two-b-side {
  background: var(--wl-card);
  padding: 40px;
  position: relative;
  transform-style: preserve-3d;
  transition: transform 0.6s cubic-bezier(0.2, 0.7, 0.2, 1);
}

.two-b-side--left {
  transform: rotateY(8deg);
  transform-origin: right center;
}

.two-b-side--right {
  transform: rotateY(-8deg);
  transform-origin: left center;
}

.two-b-split:hover .two-b-side--left {
  transform: rotateY(2deg);
}

.two-b-split:hover .two-b-side--right {
  transform: rotateY(-2deg);
}

/* --- Label with pip ----------------------------------------- */
.two-b-label {
  font-family: var(--wl-mono);
  font-size: 10px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--wl-ink-muted);
  margin: 0 0 12px;
}

.two-b-pip {
  display: inline-block;
  width: 8px;
  height: 8px;
  margin-right: 8px;
  vertical-align: middle;
}

.two-b-pip--ink {
  background: var(--wl-ink);
}

.two-b-pip--red {
  background: var(--wl-red);
}

/* --- Headings ----------------------------------------------- */
.two-b-side h3 {
  font-family: var(--wl-serif);
  font-size: 28px;
  line-height: 1.15;
  letter-spacing: -0.015em;
  font-weight: 600;
  color: var(--wl-ink);
  margin: 0 0 28px;
  max-width: 18ch;
}

.two-b-side--right h3 {
  color: var(--wl-red);
}

/* --- Stat blocks -------------------------------------------- */
.two-b-stat {
  margin-bottom: 24px;
}

.two-b-stat-big {
  font-family: var(--wl-mono);
  font-size: 44px;
  font-weight: 600;
  letter-spacing: -0.02em;
  line-height: 1;
  color: var(--wl-ink);
  margin: 0 0 4px;
  font-variant-numeric: tabular-nums;
}

.two-b-side--right .two-b-stat-big {
  color: var(--wl-red);
}

.two-b-stat-label {
  font-size: 13px;
  color: var(--wl-ink-muted);
  line-height: 1.4;
}

/* --- Day list ----------------------------------------------- */
.two-b-day-list {
  list-style: none;
  padding: 0;
  margin: 28px 0 0;
  border-top: 1px solid var(--wl-rule);
  display: flex;
  flex-direction: column;
}

.two-b-day-list li {
  padding: 12px 0;
  border-bottom: 1px dashed var(--wl-rule);
  font-size: 15px;
  color: var(--wl-ink-body);
  line-height: 1.4;
}

.two-b-day-list li:last-child {
  border-bottom: 0;
}

.two-b-day-q {
  font-family: var(--wl-mono);
  font-size: 10px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--wl-ink-muted);
  display: block;
  margin-bottom: 2px;
}

/* --- Quote -------------------------------------------------- */
.two-b-quote {
  margin-top: 32px;
  padding: 18px 0 0;
  border-top: 1px solid var(--wl-rule);
  font-family: var(--wl-serif);
  font-style: italic;
  font-size: 17px;
  line-height: 1.5;
  color: var(--wl-ink-body);
  max-width: 32ch;
}

.two-b-quote::before {
  content: "\201C";
  font-size: 32px;
  line-height: 0;
  vertical-align: -8px;
  color: var(--wl-red);
  margin-right: 4px;
}

.two-b-quote::after {
  content: "\201D";
  font-size: 32px;
  line-height: 0;
  vertical-align: -16px;
  color: var(--wl-red);
  margin-left: 4px;
}

.two-b-quote-who {
  display: block;
  margin-top: 10px;
  font-style: normal;
  font-family: var(--wl-mono);
  font-size: 11px;
  letter-spacing: 0.04em;
  color: var(--wl-ink-muted);
}

/* --- Responsive --------------------------------------------- */
@media (max-width: 768px) {
  .two-b {
    padding: 48px 0;
  }

  .two-b-inner {
    padding: 0 16px;
  }

  .two-b-split {
    grid-template-columns: 1fr;
    perspective: none;
  }

  .two-b-side--left,
  .two-b-side--right {
    transform: none;
    transform-origin: center;
  }

  .two-b-split:hover .two-b-side--left,
  .two-b-split:hover .two-b-side--right {
    transform: none;
  }

  .two-b-side {
    padding: 28px;
  }

  .two-b-stat-big {
    font-size: 32px;
  }

  .two-b-side h3 {
    font-size: 22px;
    max-width: none;
  }
}
</style>
