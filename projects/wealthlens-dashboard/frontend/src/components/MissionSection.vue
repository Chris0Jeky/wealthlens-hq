<script setup lang="ts">
/**
 * MissionSection — dark background section with the project's mission.
 *
 * Left column: quote block, mission description, signature.
 * Right column: 4 stat boxes (42 charts, 5 sources, 1820 earliest year,
 * 100% source-cited).
 *
 * Dark ink background with cream/paper text.
 */

interface MissionStat {
  value: string
  label: string
}

const STATS: MissionStat[] = [
  { value: '42', label: 'Charts published' },
  { value: '5', label: 'Primary data sources' },
  { value: '1820', label: 'Earliest year covered' },
  { value: '100%', label: 'Source-cited' },
]
</script>

<template>
  <section
    class="mission"
    data-screen-label="01 Landing — Mission"
    aria-labelledby="mission-heading"
  >
    <div class="mission-inner">
      <!-- Left column: quote + description -->
      <div>
        <p class="mission-label">&#x25CF; The project</p>

        <div class="mission-quote">
          We let the <em>numbers</em> speak. Then we get out of the way.
        </div>

        <h2 id="mission-heading" class="sr-only">The WealthLens UK mission</h2>

        <p class="mission-body">
          WealthLens UK turns buried government spreadsheets into
          source-backed, accessible, embeddable public tools &mdash; so
          journalists, educators, and anyone with a phone can see the
          system clearly.
        </p>

        <p class="mission-body">
          An engineering project. Not a campaign, not a charity. Built in
          London by Chris, a software engineer and widening-participation
          practitioner who got tired of seeing the same misquoted
          statistics every Sunday.
        </p>

        <div class="mission-signature">
          &mdash; Independent · Non-partisan · MIT licensed
        </div>
      </div>

      <!-- Right column: stat boxes -->
      <div class="mission-stats">
        <div
          v-for="stat in STATS"
          :key="stat.label"
          class="mission-stat"
        >
          <div class="mission-stat-v">{{ stat.value }}</div>
          <div class="mission-stat-l">{{ stat.label }}</div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* ============================================================
   MISSION — dark section with project identity
   ============================================================ */
.mission {
  padding: 96px 0;
  background: var(--wl-ink);
  color: var(--wl-paper);
  border-bottom: 1px solid var(--wl-ink);
}

.mission-inner {
  max-width: var(--wl-max);
  margin: 0 auto;
  padding: 0 32px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 80px;
  align-items: start;
}

/* --- Label -------------------------------------------------- */
.mission-label {
  font-family: var(--wl-mono);
  font-size: 11px;
  letter-spacing: 0.18em;
  color: var(--wl-red);
  text-transform: uppercase;
  margin: 0 0 18px;
  font-weight: 600;
}

/* --- Quote -------------------------------------------------- */
.mission-quote {
  font-family: var(--wl-serif);
  font-style: italic;
  font-size: 28px;
  line-height: 1.25;
  font-weight: 500;
  color: var(--wl-paper);
  max-width: 22ch;
  border-left: 3px solid var(--wl-red);
  padding-left: 24px;
  margin: 0 0 32px;
  letter-spacing: -0.01em;
}

.mission-quote em {
  color: var(--wl-red);
  font-weight: 500;
}

/* --- Body text ---------------------------------------------- */
.mission-body {
  font-size: 17px;
  color: rgba(244, 239, 230, 0.78);
  margin: 0 0 18px;
  line-height: 1.6;
  max-width: 50ch;
}

/* --- Signature ---------------------------------------------- */
.mission-signature {
  font-family: var(--wl-mono);
  font-size: 11px;
  color: rgba(244, 239, 230, 0.5);
  margin-top: 28px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

/* --- Stat boxes --------------------------------------------- */
.mission-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 32px;
  padding-top: 8px;
}

.mission-stat {
  border-top: 2px solid var(--wl-red);
  padding-top: 16px;
}

.mission-stat-v {
  font-family: var(--wl-serif);
  font-size: 48px;
  font-weight: 600;
  color: var(--wl-paper);
  letter-spacing: -0.02em;
  line-height: 1;
  font-variant-numeric: tabular-nums;
}

.mission-stat-l {
  font-family: var(--wl-mono);
  font-size: 11px;
  color: rgba(244, 239, 230, 0.55);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-top: 10px;
}

/* --- Screen reader only ------------------------------------- */
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

/* --- Responsive --------------------------------------------- */
@media (max-width: 768px) {
  .mission {
    padding: 48px 0;
  }

  .mission-inner {
    grid-template-columns: 1fr;
    gap: 48px;
    padding: 0 16px;
  }

  .mission-quote {
    font-size: 22px;
    max-width: none;
  }

  .mission-stat-v {
    font-size: 36px;
  }
}
</style>
