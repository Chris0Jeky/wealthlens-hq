<script setup lang="ts">
/**
 * RelatedCharts — 3-column grid of related chart card links.
 *
 * Each card shows a domain label, chart title, key finding, and a mini
 * sparkline SVG. On mobile, stacks to a single column.
 *
 * @example
 * <RelatedCharts :charts="[
 *   { domain: 'Wealth', title: 'Household wealth composition', finding: '...', to: '/charts/...' },
 * ]" />
 */

export interface RelatedChartItem {
  domain: string
  title: string
  finding: string
  /** Router path, e.g. '/charts/housing-affordability' */
  to: string
  /** Optional sparkline: 'line' or 'bar'. Defaults to 'line'. */
  sparkType?: "line" | "bar"
}

defineProps<{
  charts: RelatedChartItem[]
}>()
</script>

<template>
  <section class="related" aria-labelledby="related-heading">
    <h3 id="related-heading" class="related__heading">&darr; More from the wealth pillar</h3>
    <div class="related__grid">
      <router-link v-for="(chart, i) in charts" :key="i" :to="chart.to" class="related__card">
        <div class="related__domain">{{ chart.domain }}</div>
        <div class="related__title">{{ chart.title }}</div>
        <!-- eslint-disable-next-line vue/no-v-html -- trusted hardcoded config, not user input -->
        <div class="related__finding" v-html="chart.finding"></div>
        <!-- Mini sparkline placeholder -->
        <svg
          class="related__mini"
          viewBox="0 0 220 60"
          preserveAspectRatio="none"
          aria-hidden="true"
        >
          <template v-if="chart.sparkType === 'bar'">
            <rect x="10" y="52" width="18" height="4" fill="var(--wl-ink-faint)" />
            <rect x="32" y="50" width="18" height="6" fill="var(--wl-ink-faint)" />
            <rect x="54" y="48" width="18" height="8" fill="var(--wl-ink-faint)" />
            <rect x="76" y="44" width="18" height="12" fill="var(--wl-ink-faint)" />
            <rect x="98" y="40" width="18" height="16" fill="var(--wl-ink)" />
            <rect x="120" y="34" width="18" height="22" fill="var(--wl-ink)" />
            <rect x="142" y="26" width="18" height="30" fill="var(--wl-ink)" />
            <rect x="164" y="18" width="18" height="38" fill="var(--wl-ink)" />
            <rect x="186" y="8" width="18" height="48" fill="var(--wl-red)" />
          </template>
          <template v-else>
            <path
              d="M 0 48 L 30 46 L 60 40 L 90 32 L 120 26 L 150 22 L 180 18 L 220 14"
              stroke="var(--wl-red)"
              stroke-width="2.5"
              fill="none"
            />
          </template>
        </svg>
      </router-link>
    </div>
  </section>
</template>

<style scoped>
.related {
  max-width: 1320px;
  margin: 96px auto 0;
  padding: 0 32px;
}

.related__heading {
  font-size: 12px;
  font-family: var(--wl-mono);
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--wl-red);
  margin: 0 0 24px;
  font-weight: 600;
}

.related__grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1px;
  background: var(--wl-ink);
  border: 1px solid var(--wl-ink);
}

.related__card {
  background: var(--wl-card);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  text-decoration: none;
  color: inherit;
  transition: background 0.15s ease;
  min-height: 220px;
}
.related__card:hover {
  background: var(--wl-paper-tint);
}
.related__card:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: -2px;
}

.related__domain {
  font-family: var(--wl-mono);
  font-size: 10px;
  color: var(--wl-red);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-weight: 600;
}

.related__title {
  font-family: var(--wl-serif);
  font-weight: 600;
  font-size: 20px;
  color: var(--wl-ink);
  line-height: 1.2;
  letter-spacing: -0.012em;
}

.related__finding {
  font-size: 13px;
  color: var(--wl-ink-muted);
  line-height: 1.5;
}
.related__finding :deep(b) {
  color: var(--wl-ink);
  font-weight: 600;
}

.related__mini {
  height: 60px;
  margin-top: auto;
  width: 100%;
}

/* Responsive: stack to single column on mobile */
@media (max-width: 768px) {
  .related {
    padding: 0 16px;
  }
  .related__grid {
    grid-template-columns: 1fr;
  }
}
</style>
