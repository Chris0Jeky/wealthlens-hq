import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref } from 'vue'
import { mount } from '@vue/test-utils'
import type {
  SimulatorDashboardData,
  SimulatorScenarioList,
} from '@/types/simulator'

const scenarioList = ref<SimulatorScenarioList | null>(null)
const scenariosLoading = ref(false)
const scenariosError = ref<string | null>(null)
const dashboard = ref<SimulatorDashboardData | null>(null)
const dashLoading = ref(false)
const dashError = ref<string | null>(null)

vi.mock('@/composables/useSimulatorDashboard', () => ({
  useSimulatorScenarios: () => ({
    data: scenarioList,
    loading: scenariosLoading,
    error: scenariosError,
  }),
  useSimulatorDashboard: () => ({
    data: dashboard,
    loading: dashLoading,
    error: dashError,
  }),
}))
vi.mock('@/composables/usePageMeta', () => ({ usePageMeta: () => {} }))

import SimulatorView from '@/views/SimulatorView.vue'
import ConfidenceFanChart from '@/components/ConfidenceFanChart.vue'

const SCENARIOS: SimulatorScenarioList = {
  scenarios: [
    {
      id: 'one-percent-wealth-tax',
      name: '1% wealth tax',
      description: 'Illustrative synthetic estimate.',
    },
    {
      id: 'two-percent-wealth-tax',
      name: '2% wealth tax',
      description: 'Illustrative.',
    },
  ],
}

const DASHBOARD: SimulatorDashboardData = {
  schema_version: '1.3',
  scenario_name: '1% wealth tax',
  provenance_complete: true,
  caveats: [],
  interval_method: 'alpha_sweep',
  total_revenue_gbp_bn: { low: 14, central: 19, high: 27 },
  households_scored: 2000,
  revenue_by_decile: [],
}

describe('SimulatorView', () => {
  beforeEach(() => {
    scenarioList.value = null
    scenariosLoading.value = false
    scenariosError.value = null
    dashboard.value = null
    dashLoading.value = false
    dashError.value = null
  })

  it('shows a loading state while scenarios load', () => {
    scenariosLoading.value = true
    const wrapper = mount(SimulatorView)
    expect(wrapper.find('[role="status"]').exists()).toBe(true)
  })

  it('shows an error when the scenario list fails', () => {
    scenariosError.value = 'network down'
    const wrapper = mount(SimulatorView)
    expect(wrapper.find('[role="alert"]').text()).toContain('network down')
  })

  it('renders a scenario selector and the chart when data is present', () => {
    scenarioList.value = SCENARIOS
    dashboard.value = DASHBOARD
    const wrapper = mount(SimulatorView)
    const options = wrapper.findAll('#scenario-select option')
    expect(options).toHaveLength(2)
    expect(options[0].text()).toContain('1% wealth tax')
    const chart = wrapper.findComponent(ConfidenceFanChart)
    expect(chart.exists()).toBe(true)
    expect(chart.props('interval')).toEqual(DASHBOARD.total_revenue_gbp_bn)
    expect(chart.props('intervalMethod')).toBe('alpha_sweep')
    expect(wrapper.text()).toContain('synthetic households')
  })

  it('passes the contract caveats through to the chart', () => {
    scenarioList.value = SCENARIOS
    dashboard.value = { ...DASHBOARD, caveats: ['Provenance incomplete'] }
    const wrapper = mount(SimulatorView)
    expect(wrapper.findComponent(ConfidenceFanChart).props('caveats')).toEqual([
      'Provenance incomplete',
    ])
  })

  it('shows an error when the selected scenario fails to load', () => {
    scenarioList.value = SCENARIOS
    dashError.value = 'scenario 503'
    const wrapper = mount(SimulatorView)
    expect(wrapper.find('[role="alert"]').text()).toContain('scenario 503')
  })
})
