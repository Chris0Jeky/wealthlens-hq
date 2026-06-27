/**
 * Composables for the WealthLens-Sim scenario dashboard API (`/api/simulator`).
 *
 * Thin wrappers over {@link useFetch} that resolve the API-vs-static URL the same
 * way the data store does, so the scenario page works against the live FastAPI
 * backend in dev and (once the JSON is published statically) on the deployed site.
 */
import { computed, type Ref } from "vue"
import { useFetch, type UseFetchReturn } from "@/composables/useFetch"
import type { SimulatorDashboardData, SimulatorScenarioList } from "@/types/simulator"

const STATIC_MODE = import.meta.env.VITE_STATIC_DATA === "true"
const API_BASE = "/api/simulator"
const STATIC_BASE = `${import.meta.env.BASE_URL}data/simulator`

/** The listing URL: live API, or a static `scenarios.json` index on the built site. */
function scenariosUrl(): string {
  return STATIC_MODE ? `${STATIC_BASE}/scenarios.json` : `${API_BASE}/`
}

/** A single scenario's dashboard URL. */
function scenarioUrl(id: string): string {
  return STATIC_MODE ? `${STATIC_BASE}/${id}.json` : `${API_BASE}/scenarios/${id}`
}

/** Fetch the list of available scenarios. */
export function useSimulatorScenarios(): UseFetchReturn<SimulatorScenarioList> {
  return useFetch<SimulatorScenarioList>(scenariosUrl())
}

/**
 * Fetch the dashboard data for the scenario named by ``scenarioId``. The URL is
 * reactive, so changing the selected scenario re-fetches; an empty id holds off.
 */
export function useSimulatorDashboard(
  scenarioId: Ref<string>,
): UseFetchReturn<SimulatorDashboardData> {
  const url = computed(() => (scenarioId.value ? scenarioUrl(scenarioId.value) : ""))
  return useFetch<SimulatorDashboardData>(url, {
    immediate: Boolean(scenarioId.value),
  })
}
