<script setup lang="ts">
/**
 * StatStrip — 4-column headline stat display in broadsheet style.
 *
 * The first stat is highlighted with a red background (the "headline" number).
 * Remaining stats are standard card cells. On mobile, stacks to 2x2 grid.
 *
 * @example
 * <StatStrip :stats="[
 *   { label: 'The headline', value: '57', unit: '%', description: '...', headline: true },
 *   { label: 'Top 1% alone', value: '21', unit: '%', description: '...' },
 *   ...
 * ]" />
 */

export interface StatItem {
  label: string;
  value: string;
  unit?: string;
  description: string;
  headline?: boolean;
}

defineProps<{
  stats: StatItem[];
}>();
</script>

<template>
  <section
    class="stat-strip"
    aria-label="Key statistics"
  >
    <div
      v-for="(stat, i) in stats"
      :key="i"
      :class="['stat-strip__cell', { 'stat-strip__cell--headline': stat.headline }]"
    >
      <span class="stat-strip__label">
        <template v-if="stat.headline">&uarr; </template>{{ stat.label }}
      </span>
      <span class="stat-strip__value">
        {{ stat.value }}<sup v-if="stat.unit">{{ stat.unit }}</sup>
      </span>
      <span class="stat-strip__desc">{{ stat.description }}</span>
    </div>
  </section>
</template>

<style scoped>
.stat-strip {
  max-width: 1320px;
  margin: 0 auto 32px;
  padding: 0 32px;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1px;
  background: var(--wl-ink);
  border: 1px solid var(--wl-ink);
}

.stat-strip__cell {
  background: var(--wl-card);
  padding: 28px 24px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-strip__cell--headline {
  background: var(--wl-red);
  color: #fff;
}
.stat-strip__cell--headline .stat-strip__label {
  color: rgba(255, 255, 255, 0.75);
}
.stat-strip__cell--headline .stat-strip__value {
  color: #fff;
}
.stat-strip__cell--headline .stat-strip__desc {
  color: rgba(255, 255, 255, 0.8);
}

.stat-strip__label {
  font-family: var(--wl-mono);
  font-size: 10px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--wl-ink-muted);
  font-weight: 500;
}

.stat-strip__value {
  font-family: var(--wl-serif);
  font-size: clamp(36px, 4vw, 56px);
  font-weight: 600;
  line-height: 1;
  letter-spacing: -0.022em;
  color: var(--wl-ink);
  font-variant-numeric: tabular-nums;
}

.stat-strip__value sup {
  font-family: var(--wl-mono);
  font-size: 14px;
  font-weight: 500;
  vertical-align: top;
  position: relative;
  top: 6px;
  margin-left: 2px;
  opacity: 0.6;
}

.stat-strip__desc {
  font-size: 12px;
  color: var(--wl-ink-muted);
  line-height: 1.5;
  margin-top: 4px;
}

/* Responsive: stack to 2x2 on narrow screens */
@media (max-width: 768px) {
  .stat-strip {
    grid-template-columns: repeat(2, 1fr);
    padding: 0 16px;
  }
}

@media (max-width: 480px) {
  .stat-strip {
    grid-template-columns: 1fr;
  }
}
</style>
