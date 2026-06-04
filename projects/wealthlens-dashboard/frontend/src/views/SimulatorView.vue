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
import {
  useSimulatorDashboard,
  useSimulatorScenarios,
} from '@/composables/useSimulatorDashboard'
import { usePageMeta } from '@/composables/usePageMeta'

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

// Default to the first scenario once the list arrives.
watch(
  scenarioList,
  (list) => {
    if (list?.scenarios.length && !selectedId.value) {
      selectedId.value = list.scenarios[0].id
    }
  },
  { immediate: true },
)

const selectedScenario = computed(() =>
  scenarioList.value?.scenarios.find((s) => s.id === selectedId.value),
)

const { data: dashboard, loading, error } = useSimulatorDashboard(selectedId)
</script>

<template>
  <main class="mx-auto max-w-3xl px-4 py-8">
    <h1 class="text-2xl font-bold text-wl-ink">Policy scenario explorer</h1>
    <p class="mt-2 text-sm text-wl-ink-muted">
      Headline revenue estimates for wealth-tax policy scenarios, from the open
      WealthLens microsimulator. Figures are illustrative estimates over a
      synthetic population — not official forecasts — and every band shows its
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

      <div v-if="loading" role="status" class="mt-6 text-sm text-wl-ink-muted">
        Loading scenario…
      </div>
      <div v-else-if="error" role="alert" class="mt-6 text-sm text-wl-red">
        Could not load this scenario: {{ error }}
      </div>
      <div v-else-if="dashboard" class="mt-6">
        <ConfidenceFanChart
          :interval="dashboard.total_revenue_gbp_bn"
          label="Estimated annual revenue"
          :interval-method="dashboard.interval_method"
          :caveats="dashboard.caveats"
          :provenance-complete="dashboard.provenance_complete"
        />
        <p class="mt-2 text-xs text-wl-ink-faint">
          Scored over
          {{ dashboard.households_scored.toLocaleString() }} synthetic
          households.
        </p>
      </div>
    </template>
  </main>
</template>
