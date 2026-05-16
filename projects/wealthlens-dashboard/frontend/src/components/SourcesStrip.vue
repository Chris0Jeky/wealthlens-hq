<script setup lang="ts">
/**
 * SourcesStrip — compact strip showing the 5 primary data sources.
 *
 * Left: label text ("Every number cites its source").
 * Right: grid of 5 source cards (ONS, HMRC, WID, LR, DWP) with
 * acronym and full name.
 */

interface Source {
  acro: string
  full: string
}

const SOURCES: Source[] = [
  { acro: 'ONS', full: 'Office for National Statistics' },
  { acro: 'HMRC', full: 'HM Revenue & Customs' },
  { acro: 'WID', full: 'World Inequality Database' },
  { acro: 'LR', full: 'HM Land Registry' },
  { acro: 'DWP', full: 'Department for Work & Pensions' },
]
</script>

<template>
  <section
    class="sources"
    data-screen-label="01 Landing — Sources"
    aria-labelledby="sources-heading"
  >
    <div class="sources-inner">
      <div class="sources-label">
        <b id="sources-heading">Every number cites its source.</b>
        Pulled directly from official UK statistics. No private surveys.
        No vibes.
      </div>
      <div class="sources-row" role="list">
        <div
          v-for="src in SOURCES"
          :key="src.acro"
          class="src-card"
          role="listitem"
        >
          <span class="src-card-acro">{{ src.acro }}</span>
          <span class="src-card-full">{{ src.full }}</span>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* ============================================================
   SOURCES STRIP — data provenance
   ============================================================ */
.sources {
  padding: 56px 0;
  border-bottom: 1px solid var(--wl-ink);
  background: var(--wl-bg);
}

.sources-inner {
  max-width: var(--wl-max);
  margin: 0 auto;
  padding: 0 32px;
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 56px;
  align-items: center;
}

/* --- Label -------------------------------------------------- */
.sources-label {
  font-family: var(--wl-mono);
  font-size: 11px;
  color: var(--wl-ink-muted);
  text-transform: uppercase;
  letter-spacing: 0.16em;
  line-height: 1.6;
}

.sources-label b {
  color: var(--wl-ink);
  font-weight: 600;
  display: block;
  margin-bottom: 6px;
}

/* --- Source cards grid --------------------------------------- */
.sources-row {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 1px;
  background: var(--wl-ink);
  border: 1px solid var(--wl-ink);
}

.src-card {
  background: var(--wl-card);
  padding: 20px 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.src-card-acro {
  font-family: var(--wl-serif);
  font-weight: 700;
  font-size: 22px;
  color: var(--wl-ink);
  letter-spacing: -0.01em;
}

.src-card-full {
  font-size: 11px;
  color: var(--wl-ink-muted);
  font-family: var(--wl-mono);
  line-height: 1.4;
}

/* --- Responsive --------------------------------------------- */
@media (max-width: 768px) {
  .sources {
    padding: 36px 0;
  }

  .sources-inner {
    grid-template-columns: 1fr;
    gap: 24px;
    padding: 0 16px;
  }

  .sources-row {
    grid-template-columns: repeat(3, 1fr);
  }

  .sources-label {
    text-align: center;
  }
}

@media (max-width: 600px) {
  .sources-row {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 375px) {
  .sources-row {
    grid-template-columns: 1fr;
  }

  .src-card {
    padding: 16px;
    min-height: 44px;
  }
}
</style>
