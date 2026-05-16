import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { createRouter, createMemoryHistory } from 'vue-router'
import ChartView from '../ChartView.vue'

vi.mock('@/composables/useAnalytics', () => ({
  useAnalytics: () => ({
    init: vi.fn(),
    trackEvent: vi.fn(),
    isEnabled: false,
  }),
}))

async function createWrapper(chartName: string) {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/charts/:name', name: 'chart', component: ChartView },
      { path: '/', component: { template: '<div />' } },
    ],
  })

  router.push(`/charts/${chartName}`)
  await router.isReady()

  return mount(ChartView, {
    global: {
      plugins: [
        router,
        createTestingPinia({ createSpy: vi.fn }),
      ],
      stubs: {
        WealthSharesChart: { template: '<div data-testid="wealth-shares-chart" />' },
        HousingAffordabilityChart: { template: '<div data-testid="housing-chart" />' },
        CgtConcentrationChart: { template: '<div data-testid="cgt-chart" />' },
        WealthByDecileChart: { template: '<div data-testid="decile-chart" />' },
        StatStrip: true,
        ChartToolbar: true,
        ShareBar: true,
        RelatedCharts: true,
      },
    },
  })
}

describe('ChartView', () => {
  it('renders back link to home', async () => {
    const wrapper = await createWrapper('wealth-shares')
    const link = wrapper.find('a[href="/"]')
    expect(link.exists()).toBe(true)
    expect(link.text()).toContain('Home')
  })

  it('renders chart title for known dataset', async () => {
    const wrapper = await createWrapper('wealth-shares')
    expect(wrapper.find('h1').text()).toContain('Who owns wealth in the UK?')
  })

  it('renders housing affordability title', async () => {
    const wrapper = await createWrapper('housing-affordability')
    expect(wrapper.find('h1').text()).toContain('Housing Affordability')
  })

  it('shows not-found message for unknown chart name', async () => {
    const wrapper = await createWrapper('nonexistent')
    expect(wrapper.text()).toContain('Chart not found')
  })

  it('shows the invalid chart name in the error', async () => {
    const wrapper = await createWrapper('nonexistent')
    expect(wrapper.text()).toContain('nonexistent')
  })

  it('shows return link when chart not found', async () => {
    const wrapper = await createWrapper('nonexistent')
    const links = wrapper.findAll('a')
    const returnLink = links.find((l) => l.text().includes('Return to dashboard'))
    expect(returnLink).toBeDefined()
  })
})
