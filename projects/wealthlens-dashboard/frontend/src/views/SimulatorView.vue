<script setup lang="ts">
/**
 * SimulatorView — the live scenario explorer.
 *
 * Lists the WealthLens-Sim scenarios from `GET /api/simulator/`, lets the user
 * pick one, and renders its headline revenue band with ConfidenceFanChart. The
 * data is an illustrative estimate over a synthetic v0.1 population, surfaced
 * honestly via the chart's caveats banner + interval-method label.
 */
import { computed, ref, watch } from 'vue'
import ConfidenceFanChart from '@/components/ConfidenceFanChart.vue'
import RevenueBreakdown from '@/components/RevenueBreakdown.vue'
import ProvenancePanel from '@/components/ProvenancePanel.vue'
import {
  useSimulatorDashboard,
  useSimulatorScenarios,
} from '@/composables/useSimulatorDashboard'
import { usePageMeta } from '@/composables/usePageMeta'
import { DASHBOARD_SCHEMA_VERSION } from '@/types/simulator'

usePageMeta({
  title: 'Policy scenario explorer',
  description:
    'Illustrative revenue estimates for wealth-tax policy scenarios from the open WealthLens microsimulator.',
})

const {
  data: scenarioList,
  loading: scenariosLoading,
  error: scenariosError,
} = useSimulatorScenarios()

const selectedId = ref('')

// Default to the first scenario once the list arrives, and recover if a refetch
// drops the currently-selected id (otherwise we'd fetch a now-missing scenario).
watch(
  scenarioList,
  (list) => {
    if (!list?.scenarios.length) return
    const ids = list.scenarios.map((s) => s.id)
    if (!selectedId.value || !ids.includes(selectedId.value)) {
      selectedId.value = list.scenarios[0].id
    }
  },
  { immediate: true },
)

const selectedScenario = computed(() =>
  scenarioList.value?.scenarios.find((s) => s.id === selectedId.value),
)

const { data: dashboard, loading, error } = useSimulatorDashboard(selectedId)

// Fail loud on a contract-version mismatch rather than silently mis-rendering a
// stale-shaped payload (the field exists for exactly this guard).
const schemaMismatch = computed(
  () =>
    !!dashboard.value &&
    dashboard.value.schema_version !== DASHBOARD_SCHEMA_VERSION,
)

// A visually-hidden, polite live summary so a screen-reader user hears the new
// headline when they change scenario (the chart itself is a static role="img").
const liveSummary = computed(() => {
  if (loading.value) return 'Loading scenario…'
  if (error.value || schemaMismatch.value)
    return 'This scenario could not be displayed.'
  if (dashboard.value && selectedScenario.value) {
    const { low, central, high } = dashboard.value.total_revenue_gbp_bn
    return `Now showing ${selectedScenario.value.name}: estimated annual revenue £${central.toFixed(1)}bn (range £${low.toFixed(1)}bn to £${high.toFixed(1)}bn).`
  }
  return ''
})
</script>

<template>
  <main class="mx-auto max-w-3xl px-4 py-8">
    <h1 class="text-2xl font-bold text-wl-ink">Policy scenario explorer</h1>
    <p class="mt-2 text-sm text-wl-ink-muted">
      Headline revenue estimates for wealth-tax policy scenarios, from the open
      WealthLens microsimulator. Figures are illustrative estimates over a
      synthetic population (not official forecasts), and every band shows its
      uncertainty and provenance.
    </p>

    <div
      v-if="scenariosLoading"
      role="status"
      class="mt-6 text-sm text-wl-ink-muted"
    >
      Loading scenarios…
    </div>
    <div
      v-else-if="scenariosError"
      role="alert"
      class="mt-6 text-sm text-wl-red"
    >
      Could not load scenarios: {{ scenariosError }}
    </div>

    <template v-else-if="scenarioList?.scenarios.length">
      <div class="mt-6">
        <label
          for="scenario-select"
          class="mb-1 block text-sm font-medium text-wl-ink"
        >
          Scenario
        </label>
        <select
          id="scenario-select"
          v-model="selectedId"
          class="w-full rounded-md border border-wl-rule bg-wl-card px-3 py-2 text-wl-ink"
        >
          <option
            v-for="scenario in scenarioList.scenarios"
            :key="scenario.id"
            :value="scenario.id"
          >
            {{ scenario.name }}
          </option>
        </select>
      </div>

      <p v-if="selectedScenario" class="mt-3 text-sm text-wl-ink-muted">
        {{ selectedScenario.description }}
      </p>

      <!-- The dynamic region announces the updated headline to screen readers when
           the scenario changes (the chart itself is a static role="img"). -->
      <div aria-live="polite" :aria-busy="loading">
        <span class="sr-only">{{ liveSummary }}</span>

        <div
          v-if="loading"
          role="status"
          class="mt-6 text-sm text-wl-ink-muted"
        >
          Loading scenario…
        </div>
        <div v-else-if="error" role="alert" class="mt-6 text-sm text-wl-red">
          Could not load this scenario: {{ error }}
        </div>
        <div
          v-else-if="schemaMismatch"
          role="alert"
          class="mt-6 text-sm text-wl-red"
        >
          This scenario uses a newer data format than the app supports —
          refusing to display it rather than risk showing wrong figures. Please
          refresh.
        </div>
        <div v-else-if="dashboard" class="mt-6">
          <ConfidenceFanChart
            :interval="dashboard.total_revenue_gbp_bn"
            label="Estimated annual revenue"
            :interval-method="dashboard.interval_method"
            :caveats="dashboard.caveats"
            :provenance-complete="dashboard.provenance_complete"
          />
          <p
            v-if="Number.isFinite(dashboard.households_scored)"
            class="mt-2 text-xs text-wl-ink-muted"
          >
            Scored over
            {{ dashboard.households_scored.toLocaleString() }} synthetic
            households.
          </p>
          <RevenueBreakdown
            :by-decile="dashboard.revenue_by_decile ?? []"
            :by-nation="dashboard.revenue_by_nation"
          />
          <ProvenancePanel
            :assumptions="dashboard.provenance?.assumptions_consumed ?? []"
            :population-sources="dashboard.population_provenance ?? []"
          />
        </div>
      </div>
    </template>

    <!-- Loaded but empty: never a silent blank page. -->
    <div
      v-else-if="scenarioList"
      role="status"
      class="mt-6 text-sm text-wl-ink-muted"
    >
      No scenarios are available yet.
    </div>
  </main>
</template>
