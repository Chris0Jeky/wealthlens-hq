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
  revenue_by_decile: Array.from({ length: 10 }, (_, i) =>
    i === 9 ? { low: 10, central: 14, high: 20 } : { low: 0, central: 0, high: 0 },
  ),
  revenue_by_nation: {
    england: { low: 12, central: 16, high: 24 },
    scotland: { low: 0.4, central: 0.6, high: 0.8 },
  },
  provenance: {
    complete: true,
    assumptions_consumed: [
      {
        assumption_id: 'toptail.pareto_alpha.overall.v1',
        domain: 'top-tail',
        source: 'Vermeulen (2018); calibrated to UK WAS',
        source_urls: ['https://doi.org/10.1111/roiw.12279'],
      },
    ],
  },
  population_provenance: [
    {
      id: 'ons-was-wealth',
      name: 'ONS Wealth and Assets Survey (WAS)',
      url: 'https://www.ons.gov.uk/file?uri=/x/totalwealthtables.xlsx',
      access_date: '2026-05-30',
      licence: 'OGL-3.0',
    },
    { id: 'synth.pareto_alpha' },
  ],
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

  it('surfaces the consumed assumptions and their citation links', () => {
    scenarioList.value = SCENARIOS
    dashboard.value = DASHBOARD
    const wrapper = mount(SimulatorView)
    expect(wrapper.text()).toContain('Sources')
    expect(wrapper.text()).toContain('Vermeulen (2018)')
    const cite = wrapper
      .findAll('a')
      .find((a) => a.attributes('href') === 'https://doi.org/10.1111/roiw.12279')
    expect(cite).toBeTruthy()
    expect(cite?.attributes('rel')).toContain('noopener')
    // The population data source is surfaced too.
    expect(wrapper.text()).toContain('Population data sources')
    expect(wrapper.text()).toContain('ONS Wealth and Assets Survey')
  })

  it('degrades gracefully (chart still renders, no sources panel) when all provenance is absent', () => {
    scenarioList.value = SCENARIOS
    dashboard.value = {
      ...DASHBOARD,
      provenance: undefined,
      population_provenance: undefined,
    }
    const wrapper = mount(SimulatorView)
    // The headline chart still renders; the whole sources panel is hidden.
    expect(wrapper.findComponent(ConfidenceFanChart).exists()).toBe(true)
    expect(wrapper.text()).not.toContain('Sources & assumptions')
  })

  it('surfaces the revenue breakdown (by nation + decile)', () => {
    scenarioList.value = SCENARIOS
    dashboard.value = DASHBOARD
    const wrapper = mount(SimulatorView)
    expect(wrapper.text()).toContain('Where the revenue comes from')
    expect(wrapper.text()).toContain('England')
    expect(wrapper.text()).toContain('Decile 10 (wealthiest)')
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

  it('shows an empty-state message when the list is loaded but empty', () => {
    scenarioList.value = { scenarios: [] }
    const wrapper = mount(SimulatorView)
    expect(wrapper.find('[role="status"]').text()).toContain(
      'No scenarios are available',
    )
    expect(wrapper.find('#scenario-select').exists()).toBe(false)
  })

  it('refuses to render the chart on a schema-version mismatch', () => {
    scenarioList.value = SCENARIOS
    dashboard.value = { ...DASHBOARD, schema_version: '99.0' }
    const wrapper = mount(SimulatorView)
    expect(wrapper.findComponent(ConfidenceFanChart).exists()).toBe(false)
    expect(wrapper.find('[role="alert"]').text()).toContain('newer data format')
  })

  it('announces the current scenario in a polite live region', () => {
    scenarioList.value = SCENARIOS
    dashboard.value = DASHBOARD
    const wrapper = mount(SimulatorView)
    const live = wrapper.find('[aria-live="polite"]')
    expect(live.exists()).toBe(true)
    expect(live.text()).toContain('Now showing 1% wealth tax')
  })

  it('the live summary says "unavailable" (never £NaNbn) for a non-finite interval', () => {
    scenarioList.value = SCENARIOS
    dashboard.value = {
      ...DASHBOARD,
      total_revenue_gbp_bn: { low: NaN, central: NaN, high: NaN },
    }
    const wrapper = mount(SimulatorView)
    const live = wrapper.find('[aria-live="polite"]')
    expect(live.text()).toContain('unavailable')
    expect(live.text()).not.toContain('NaN')
  })
})
