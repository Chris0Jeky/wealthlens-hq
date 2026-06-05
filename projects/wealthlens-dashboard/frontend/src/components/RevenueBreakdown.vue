<script setup lang="ts">
/**
 * RevenueBreakdown — shows where a scenario's headline revenue comes from: the
 * split by GB nation and across the 10 wealth deciles.
 *
 * The dashboard JSON already carries `revenue_by_nation` and `revenue_by_decile`;
 * the scenario page previously discarded both. They are rendered here as accessible
 * tables (a decorative proportional bar accompanies each decile's figure — the
 * number is the source of truth, the bar is aria-hidden). Both inputs are optional
 * so a partial payload degrades gracefully.
 */
import { computed, useId } from 'vue'
import type { Interval } from '@/types/simulator'

const props = defineProps<{
  byDecile?: Interval[]
  byNation?: Record<string, Interval>
  currency?: string
  unit?: string
}>()

const cur = computed(() => props.currency ?? '£')
const unit = computed(() => props.unit ?? 'bn')

function fmt(n: number): string {
  return `${cur.value}${n.toFixed(2)}${unit.value}`
}

const headingId = useId()

const NATION_NAMES: Record<string, string> = {
  england: 'England',
  scotland: 'Scotland',
  wales: 'Wales',
  'northern-ireland': 'Northern Ireland',
}

// Nations sorted by central revenue, largest first.
const nations = computed(() =>
  Object.entries(props.byNation ?? {})
    .map(([key, iv]) => ({ key, name: NATION_NAMES[key] ?? key, iv }))
    .sort((a, b) => b.iv.central - a.iv.central),
)

// Deciles labelled least→most wealthy, each with a decorative bar width (% of the
// largest decile's central value) so the concentration in the top deciles is visible.
const deciles = computed(() => {
  const arr = props.byDecile ?? []
  const max = Math.max(0, ...arr.map((d) => d.central))
  return arr.map((iv, i) => ({
    key: i,
    label:
      i === 0
        ? 'Decile 1 (least wealthy)'
        : i === arr.length - 1
          ? `Decile ${arr.length} (wealthiest)`
          : `Decile ${i + 1}`,
    iv,
    pct: max > 0 ? Math.round((iv.central / max) * 100) : 0,
  }))
})
</script>

<template>
  <section
    v-if="nations.length || deciles.length"
    :aria-labelledby="headingId"
    class="mt-8 border-t border-wl-rule pt-6"
  >
    <h2 :id="headingId" class="text-base font-semibold text-wl-ink">
      Where the revenue comes from
    </h2>

    <template v-if="nations.length">
      <h3 class="mt-4 text-sm font-semibold text-wl-ink">By nation</h3>
      <table class="mt-2 w-full text-sm">
        <caption class="sr-only">
          Estimated annual revenue by GB nation, central estimate and low–high range.
        </caption>
        <thead>
          <tr class="text-left text-wl-ink-muted">
            <th scope="col" class="py-1 font-medium">Nation</th>
            <th scope="col" class="py-1 text-right font-medium">Central</th>
            <th scope="col" class="py-1 text-right font-medium">Range (low–high)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="n in nations" :key="n.key" class="border-t border-wl-rule">
            <th scope="row" class="py-1 font-normal text-wl-ink">{{ n.name }}</th>
            <td class="py-1 text-right tabular-nums text-wl-ink">{{ fmt(n.iv.central) }}</td>
            <td class="py-1 text-right tabular-nums text-wl-ink-muted">
              {{ fmt(n.iv.low) }}–{{ fmt(n.iv.high) }}
            </td>
          </tr>
        </tbody>
      </table>
    </template>

    <template v-if="deciles.length">
      <h3 class="mt-5 text-sm font-semibold text-wl-ink">By wealth decile</h3>
      <p class="mt-1 text-sm text-wl-ink-muted">
        How the revenue falls across the population, from the least to the most
        wealthy tenth.
      </p>
      <table class="mt-2 w-full text-sm">
        <caption class="sr-only">
          Estimated annual revenue by wealth decile, central estimate.
        </caption>
        <thead>
          <tr class="text-left text-wl-ink-muted">
            <th scope="col" class="py-1 font-medium">Wealth decile</th>
            <th scope="col" class="py-1 text-right font-medium">Central revenue</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="d in deciles" :key="d.key" class="border-t border-wl-rule">
            <th scope="row" class="py-1 font-normal text-wl-ink">{{ d.label }}</th>
            <td class="py-1 text-right">
              <div class="flex items-center justify-end gap-2">
                <span
                  aria-hidden="true"
                  class="h-2 rounded-sm bg-wl-red/70"
                  :style="{ width: `${d.pct}%`, minWidth: d.pct > 0 ? '2px' : '0' }"
                ></span>
                <span class="tabular-nums text-wl-ink">{{ fmt(d.iv.central) }}</span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </template>
  </section>
</template>
