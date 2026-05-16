import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia, defineStore } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'
import { ref } from 'vue'
import HomeView from '../HomeView.vue'

const mockFetchDatasets = vi.fn()
const mockFetchFreshness = vi.fn()

vi.mock('@/stores/data', () => ({
  useDataStore: () => ({
    datasets: mockDatasets.value,
    loading: mockLoading.value,
    error: mockError.value,
    freshness: mockFreshness.value,
    fetchDatasets: mockFetchDatasets,
    fetchFreshness: mockFetchFreshness,
  }),
}))

const mockDatasets = ref<string[]>([])
const mockLoading = ref(false)
const mockError = ref<string | null>(null)
const mockFreshness = ref<Record<string, unknown>>({})

function createMountOptions() {
  const pinia = createPinia()
  setActivePinia(pinia)

  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: HomeView },
      { path: '/charts/:name', component: { template: '<div />' } },
    ],
  })

  return {
    global: {
      plugins: [router, pinia],
    },
  }
}

describe('HomeView', () => {
  beforeEach(() => {
    mockDatasets.value = []
    mockLoading.value = false
    mockError.value = null
    mockFreshness.value = {}
    mockFetchDatasets.mockClear()
    mockFetchFreshness.mockClear()
  })

  it('renders main heading', async () => {
    const wrapper = mount(HomeView, createMountOptions())
    await flushPromises()
    expect(wrapper.find('h1').text()).toBe('UK Wealth Inequality Dashboard')
  })

  it('renders description paragraph', async () => {
    const wrapper = mount(HomeView, createMountOptions())
    await flushPromises()
    expect(wrapper.text()).toContain('Open-source, source-backed data')
  })

  it('shows loading state', async () => {
    mockLoading.value = true
    const wrapper = mount(HomeView, createMountOptions())
    await flushPromises()
    expect(wrapper.text()).toContain('Loading datasets')
  })

  it('shows error state', async () => {
    mockError.value = 'Network error'
    const wrapper = mount(HomeView, createMountOptions())
    await flushPromises()
    expect(wrapper.text()).toContain('Network error')
  })

  it('renders dataset cards when loaded', async () => {
    mockDatasets.value = ['wealth-shares', 'housing-affordability']
    const wrapper = mount(HomeView, createMountOptions())
    await flushPromises()
    const items = wrapper.findAll('[role="listitem"]')
    expect(items.length).toBe(2)
  })

  it('calls fetchDatasets on mount', async () => {
    mount(HomeView, createMountOptions())
    await flushPromises()
    expect(mockFetchDatasets).toHaveBeenCalledOnce()
  })

  it('calls fetchFreshness on mount', async () => {
    mount(HomeView, createMountOptions())
    await flushPromises()
    expect(mockFetchFreshness).toHaveBeenCalledOnce()
  })
})
