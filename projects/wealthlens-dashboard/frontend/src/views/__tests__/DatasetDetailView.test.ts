import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { defineComponent, h } from 'vue'
import { createPinia, setActivePinia } from 'pinia'
import DatasetDetailView from '@/views/DatasetDetailView.vue'

const mockRoute = { params: { name: 'wealth-shares' } }

const mockMetadata = {
  name: 'wealth-shares',
  description: 'Top 1%/10% wealth shares in GB',
  source: 'World Inequality Database',
  source_url: 'https://wid.world/',
  access_date: '2026-05-14',
  row_count: 150,
  columns: ['year', 'percentile', 'value'],
}

const mockRows = [
  { year: 2020, percentile: 'p99p100', value: 21.3 },
  { year: 2020, percentile: 'p90p100', value: 52.1 },
]

const RouterLinkStub = defineComponent({
  name: 'RouterLink',
  props: { to: { type: String, required: true } },
  setup(props, { slots }) {
    return () => h('a', { href: props.to }, slots.default?.())
  },
})

vi.mock('vue-router', () => ({
  useRoute: () => mockRoute,
}))

function mountView() {
  return mount(DatasetDetailView, {
    global: {
      stubs: { RouterLink: RouterLinkStub },
      plugins: [createPinia()],
    },
  })
}

describe('DatasetDetailView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
  })

  it('shows loading state initially', () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation(() => new Promise(() => {})),
    )
    const wrapper = mountView()
    expect(wrapper.text()).toContain('Loading dataset...')
    vi.unstubAllGlobals()
  })

  it('shows error state when fetch fails', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockRejectedValue(new Error('Network error')),
    )
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.text()).toContain('Network error')
    vi.unstubAllGlobals()
  })

  it('renders metadata after successful fetch', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation((url: string) => {
        if (url.includes('/metadata')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockMetadata),
          })
        }
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ data: mockRows }),
        })
      }),
    )

    const wrapper = mountView()
    await flushPromises()

    expect(wrapper.text()).toContain('wealth-shares')
    expect(wrapper.text()).toContain('World Inequality Database')
    expect(wrapper.text()).toContain('2026-05-14')
    vi.unstubAllGlobals()
  })

  it('renders a data preview table with column headers', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation((url: string) => {
        if (url.includes('/metadata')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockMetadata),
          })
        }
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ data: mockRows }),
        })
      }),
    )

    const wrapper = mountView()
    await flushPromises()

    const headers = wrapper.findAll('th')
    const headerTexts = headers.map((h) => h.text())
    expect(headerTexts).toContain('year')
    expect(headerTexts).toContain('percentile')
    expect(headerTexts).toContain('value')
    vi.unstubAllGlobals()
  })

  it('shows a View Chart link for supported datasets', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation((url: string) => {
        if (url.includes('/metadata')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockMetadata),
          })
        }
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ data: mockRows }),
        })
      }),
    )

    const wrapper = mountView()
    await flushPromises()

    const chartLink = wrapper.find('a[href="/charts/wealth-shares"]')
    expect(chartLink.exists()).toBe(true)
    vi.unstubAllGlobals()
  })

  it('has a back link to the dashboard', () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation(() => new Promise(() => {})),
    )
    const wrapper = mountView()
    const backLink = wrapper.find('a[href="/"]')
    expect(backLink.exists()).toBe(true)
    expect(backLink.text()).toContain('Back to datasets')
    vi.unstubAllGlobals()
  })

  it('uses semantic sections with aria-labelledby', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation((url: string) => {
        if (url.includes('/metadata')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockMetadata),
          })
        }
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ data: mockRows }),
        })
      }),
    )

    const wrapper = mountView()
    await flushPromises()

    expect(wrapper.find('[aria-labelledby="source-heading"]').exists()).toBe(true)
    expect(wrapper.find('[aria-labelledby="preview-heading"]').exists()).toBe(true)
    vi.unstubAllGlobals()
  })
})
