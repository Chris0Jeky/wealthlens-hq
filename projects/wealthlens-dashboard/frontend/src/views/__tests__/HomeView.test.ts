import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { createRouter, createMemoryHistory } from 'vue-router'
import HomeView from '../HomeView.vue'
import { useDataStore } from '@/stores/data'

function createMountOptions(storeOverrides = {}) {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: HomeView },
      { path: '/charts/:name', component: { template: '<div />' } },
    ],
  })

  return {
    global: {
      plugins: [
        router,
        createTestingPinia({
          createSpy: vi.fn,
          initialState: { data: { datasets: [], loading: false, error: null, ...storeOverrides } },
        }),
      ],
    },
  }
}

describe('HomeView', () => {
  it('renders main heading', () => {
    const wrapper = mount(HomeView, createMountOptions())
    expect(wrapper.find('h1').text()).toBe('UK Wealth Inequality Dashboard')
  })

  it('renders description paragraph', () => {
    const wrapper = mount(HomeView, createMountOptions())
    expect(wrapper.text()).toContain('Open-source, source-backed data')
  })

  it('shows loading state', () => {
    const wrapper = mount(HomeView, createMountOptions({ loading: true }))
    expect(wrapper.text()).toContain('Loading datasets')
  })

  it('shows error state', () => {
    const wrapper = mount(HomeView, createMountOptions({ error: 'Network error' }))
    expect(wrapper.text()).toContain('Network error')
  })

  it('renders dataset cards when loaded', () => {
    const wrapper = mount(
      HomeView,
      createMountOptions({ datasets: ['wealth-shares', 'housing-affordability'] }),
    )
    const items = wrapper.findAll('[role="listitem"]')
    expect(items.length).toBe(2)
  })

  it('filters dataset cards when search is active', async () => {
    const wrapper = mount(
      HomeView,
      createMountOptions({
        datasets: ['wealth-shares', 'housing-affordability', 'cgt-concentration'],
      }),
    )

    await wrapper.find('input[type="search"]').setValue('housing')
    await new Promise((resolve) => window.setTimeout(resolve, 250))
    await flushPromises()

    const items = wrapper.findAll('[role="listitem"]')
    expect(items).toHaveLength(1)
    expect(items[0].text()).toContain('housing-affordability')
  })

  it('calls fetchDatasets on mount', () => {
    mount(HomeView, createMountOptions())
    const store = useDataStore()
    expect(store.fetchDatasets).toHaveBeenCalledOnce()
  })
})
