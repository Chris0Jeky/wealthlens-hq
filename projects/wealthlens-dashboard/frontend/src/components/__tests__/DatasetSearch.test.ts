import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { ref } from 'vue'
import DatasetSearch from '@/components/DatasetSearch.vue'

// Mock vue-router
const pushMock = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: pushMock }),
}))

// Mock useDebounce to pass through immediately in tests
vi.mock('@/composables/useDebounce', () => ({
  useDebounce: (source: ReturnType<typeof ref>) => source,
}))

describe('DatasetSearch', () => {
  beforeEach(() => {
    pushMock.mockClear()
  })

  function factory() {
    return mount(DatasetSearch, {
      global: {
        stubs: {
          'router-link': { template: '<a><slot /></a>' },
        },
      },
    })
  }

  it('renders the search input', () => {
    const wrapper = factory()
    const input = wrapper.find('input[type="search"]')
    expect(input.exists()).toBe(true)
    expect(input.attributes('placeholder')).toBe('Search datasets...')
  })

  it('has accessible label for search input', () => {
    const wrapper = factory()
    const label = wrapper.find('label[for="dataset-search-input"]')
    expect(label.exists()).toBe(true)
    expect(label.text()).toContain('Search datasets')
  })

  it('renders category filter buttons', () => {
    const wrapper = factory()
    const buttons = wrapper.findAll('button[aria-pressed]')
    expect(buttons.length).toBeGreaterThanOrEqual(5)
    const labels = buttons.map((b) => b.text())
    expect(labels).toContain('Wealth')
    expect(labels).toContain('Housing')
    expect(labels).toContain('Tax')
    expect(labels).toContain('Income')
    expect(labels).toContain('Regional')
  })

  it('does not show results when search is inactive', () => {
    const wrapper = factory()
    const results = wrapper.find('#dataset-search-results')
    expect(results.exists()).toBe(false)
  })

  it('shows results when user types a query', async () => {
    const wrapper = factory()
    const input = wrapper.find('input[type="search"]')
    await input.setValue('wealth')
    await flushPromises()
    const results = wrapper.find('#dataset-search-results')
    expect(results.exists()).toBe(true)
  })

  it('indexes all public datasets', async () => {
    const wrapper = factory()
    const input = wrapper.find('input[type="search"]')
    await input.setValue('boe')
    await flushPromises()

    expect(wrapper.text()).toContain('Bank of England Rates')
  })

  it('filters datasets by search query', async () => {
    const wrapper = factory()
    const input = wrapper.find('input[type="search"]')
    await input.setValue('housing')
    await flushPromises()
    const resultCards = wrapper.findAll('[role="option"]')
    expect(resultCards.length).toBeGreaterThanOrEqual(1)
    // All results should contain housing-related text
    resultCards.forEach((card) => {
      expect(card.text().toLowerCase()).toContain('housing')
    })
  })

  it('shows empty state when no datasets match', async () => {
    const wrapper = factory()
    const input = wrapper.find('input[type="search"]')
    await input.setValue('xyznonexistent')
    await flushPromises()
    expect(wrapper.text()).toContain('No datasets match your search')
  })

  it('filters by category when chip is clicked', async () => {
    const wrapper = factory()
    const taxButton = wrapper.findAll('button[aria-pressed]').find((b) => b.text() === 'Tax')
    expect(taxButton).toBeDefined()
    await taxButton!.trigger('click')
    await flushPromises()
    const results = wrapper.find('#dataset-search-results')
    expect(results.exists()).toBe(true)
    const resultCards = wrapper.findAll('[role="option"]')
    expect(resultCards.length).toBeGreaterThanOrEqual(1)
  })

  it('emits filtered dataset names for the parent grid', async () => {
    const wrapper = factory()
    const input = wrapper.find('input[type="search"]')
    await input.setValue('housing')
    await flushPromises()

    const emitted = wrapper.emitted('filtered-change') ?? []
    const latest = emitted.at(-1)?.[0] as { active: boolean; names: string[] }
    expect(latest.active).toBe(true)
    expect(latest.names).toContain('housing-affordability')
    expect(latest.names).not.toContain('wealth-shares')
  })

  it('marks selected category chip with aria-pressed=true', async () => {
    const wrapper = factory()
    const wealthButton = wrapper.findAll('button[aria-pressed]').find((b) => b.text() === 'Wealth')
    expect(wealthButton!.attributes('aria-pressed')).toBe('false')
    await wealthButton!.trigger('click')
    await flushPromises()
    expect(wealthButton!.attributes('aria-pressed')).toBe('true')
  })

  it('navigates to chart on result click', async () => {
    const wrapper = factory()
    const input = wrapper.find('input[type="search"]')
    await input.setValue('wealth')
    await flushPromises()
    const firstResult = wrapper.find('[role="option"]')
    expect(firstResult.exists()).toBe(true)
    await firstResult.trigger('click')
    expect(pushMock).toHaveBeenCalled()
    expect(pushMock.mock.calls[0][0]).toMatch(/^\/charts\//)
  })

  it('falls back to dataset detail route when a result has no chart route', async () => {
    const wrapper = factory()
    const input = wrapper.find('input[type="search"]')
    await input.setValue('manual-only')
    await flushPromises()

    const vm = wrapper.vm as unknown as {
      navigateToDataset: (entry: { name: string }) => void
    }
    vm.navigateToDataset({ name: 'manual-only' })

    expect(pushMock).toHaveBeenCalledWith('/datasets/manual-only')
  })

  it('supports keyboard navigation with ArrowDown', async () => {
    const wrapper = factory()
    const input = wrapper.find('input[type="search"]')
    await input.setValue('wealth')
    await flushPromises()
    await input.trigger('keydown', { key: 'ArrowDown' })
    await flushPromises()
    const activeResult = wrapper.find('[data-active="true"]')
    expect(activeResult.exists()).toBe(true)
    expect(activeResult.attributes('aria-selected')).toBe('true')
  })

  it('supports keyboard navigation with ArrowUp', async () => {
    const wrapper = factory()
    const input = wrapper.find('input[type="search"]')
    await input.setValue('wealth')
    await flushPromises()
    // Move down twice then up once
    await input.trigger('keydown', { key: 'ArrowDown' })
    await input.trigger('keydown', { key: 'ArrowDown' })
    await input.trigger('keydown', { key: 'ArrowUp' })
    await flushPromises()
    const activeResult = wrapper.find('[data-active="true"]')
    expect(activeResult.exists()).toBe(true)
    expect(activeResult.attributes('id')).toBe('search-result-0')
  })

  it('navigates on Enter key', async () => {
    const wrapper = factory()
    const input = wrapper.find('input[type="search"]')
    await input.setValue('wealth')
    await flushPromises()
    await input.trigger('keydown', { key: 'ArrowDown' })
    await input.trigger('keydown', { key: 'Enter' })
    expect(pushMock).toHaveBeenCalled()
    expect(pushMock.mock.calls[0][0]).toMatch(/^\/charts\//)
  })

  it('clears search on Escape key', async () => {
    const wrapper = factory()
    const input = wrapper.find('input[type="search"]')
    await input.setValue('wealth')
    await flushPromises()
    expect(wrapper.find('#dataset-search-results').exists()).toBe(true)
    await input.trigger('keydown', { key: 'Escape' })
    await flushPromises()
    expect(wrapper.find('#dataset-search-results').exists()).toBe(false)
  })

  it('clears a zero-result search on Escape key', async () => {
    const wrapper = factory()
    const input = wrapper.find('input[type="search"]')
    await input.setValue('xyznonexistent')
    await flushPromises()
    expect(wrapper.text()).toContain('No datasets match your search')
    await input.trigger('keydown', { key: 'Escape' })
    await flushPromises()
    expect(wrapper.find('#dataset-search-results').exists()).toBe(false)
    expect((input.element as HTMLInputElement).value).toBe('')
  })

  it('has aria-live region for result count', () => {
    const wrapper = factory()
    const liveRegion = wrapper.find('[aria-live="polite"]')
    expect(liveRegion.exists()).toBe(true)
  })

  it('search input has combobox role', async () => {
    const wrapper = factory()
    const input = wrapper.find('input[type="search"]')
    expect(input.attributes('role')).toBe('combobox')
    // aria-controls is only set when search is active
    expect(input.attributes('aria-controls')).toBeUndefined()
    await input.setValue('wealth')
    await flushPromises()
    expect(input.attributes('aria-controls')).toBe('dataset-search-results')
  })

  it('results list has listbox role', async () => {
    const wrapper = factory()
    const input = wrapper.find('input[type="search"]')
    await input.setValue('wealth')
    await flushPromises()
    const results = wrapper.find('#dataset-search-results')
    expect(results.attributes('role')).toBe('listbox')
  })

  it('result cards have option role', async () => {
    const wrapper = factory()
    const input = wrapper.find('input[type="search"]')
    await input.setValue('wealth')
    await flushPromises()
    const options = wrapper.findAll('[role="option"]')
    expect(options.length).toBeGreaterThanOrEqual(1)
  })

  it('clear button removes query text', async () => {
    const wrapper = factory()
    const input = wrapper.find('input[type="search"]')
    await input.setValue('housing')
    await flushPromises()
    const clearButton = wrapper.find('button[aria-label="Clear search"]')
    expect(clearButton.exists()).toBe(true)
    await clearButton.trigger('click')
    await flushPromises()
    expect((input.element as HTMLInputElement).value).toBe('')
  })

  it('displays category badge on result cards', async () => {
    const wrapper = factory()
    const input = wrapper.find('input[type="search"]')
    await input.setValue('housing')
    await flushPromises()
    const resultCards = wrapper.findAll('[role="option"]')
    expect(resultCards.length).toBeGreaterThanOrEqual(1)
    // Each result card should have a category badge
    expect(resultCards[0].text().toLowerCase()).toMatch(/wealth|housing|tax|income|regional/)
  })
})
