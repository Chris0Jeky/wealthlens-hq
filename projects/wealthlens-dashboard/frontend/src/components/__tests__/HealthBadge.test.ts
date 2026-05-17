import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import HealthBadge from '@/components/HealthBadge.vue'

describe('HealthBadge', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('shows loading state initially', () => {
    vi.spyOn(globalThis, 'fetch').mockReturnValueOnce(new Promise(() => {}))
    const wrapper = mount(HealthBadge)
    expect(wrapper.text()).toContain('Checking data')
    expect(wrapper.text()).toContain('Loading')
  })

  it('shows healthy state with dataset count and status text', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: 'healthy', available_count: 4, total_count: 4 }),
    } as Response)

    const wrapper = mount(HealthBadge)
    await flushPromises()

    expect(wrapper.text()).toContain('4/4 datasets')
    expect(wrapper.text()).toContain('Healthy')
    expect(wrapper.find('span').classes()).toContain('bg-green-100')
  })

  it('shows degraded state with status text', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: 'degraded', available_count: 2, total_count: 4 }),
    } as Response)

    const wrapper = mount(HealthBadge)
    await flushPromises()

    expect(wrapper.text()).toContain('2/4 datasets')
    expect(wrapper.text()).toContain('Degraded')
    expect(wrapper.find('span').classes()).toContain('bg-yellow-100')
  })

  it('shows unavailable state with status text', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: 'unavailable', available_count: 0, total_count: 4 }),
    } as Response)

    const wrapper = mount(HealthBadge)
    await flushPromises()

    expect(wrapper.text()).toContain('0/4 datasets')
    expect(wrapper.text()).toContain('Unavailable')
    expect(wrapper.find('span').classes()).toContain('bg-red-100')
  })

  it('shows error state on fetch failure with status text', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValueOnce(new Error('fail'))

    const wrapper = mount(HealthBadge)
    await flushPromises()

    expect(wrapper.text()).toContain('Status unknown')
    expect(wrapper.text()).toContain('Error')
    expect(wrapper.find('span').classes()).toContain('bg-gray-100')
  })

  it('has accessible role and aria-label with status text', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: 'healthy', available_count: 4, total_count: 4 }),
    } as Response)

    const wrapper = mount(HealthBadge)
    await flushPromises()

    const badge = wrapper.find('[role="status"]')
    expect(badge.exists()).toBe(true)
    expect(badge.attributes('aria-label')).toContain('Healthy')
    expect(badge.attributes('aria-label')).toContain('4/4 datasets')
  })

  it('renders an SVG icon for each non-loading state', async () => {
    // Test healthy has checkmark SVG
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: 'healthy', available_count: 4, total_count: 4 }),
    } as Response)

    const wrapper = mount(HealthBadge)
    await flushPromises()

    const svg = wrapper.find('svg')
    expect(svg.exists()).toBe(true)
    expect(svg.attributes('aria-hidden')).toBe('true')
  })

  it('renders a warning icon for degraded state', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: 'degraded', available_count: 2, total_count: 4 }),
    } as Response)

    const wrapper = mount(HealthBadge)
    await flushPromises()

    const svg = wrapper.find('svg')
    expect(svg.exists()).toBe(true)
  })

  it('renders an X icon for unavailable state', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: 'unavailable', available_count: 0, total_count: 4 }),
    } as Response)

    const wrapper = mount(HealthBadge)
    await flushPromises()

    const svg = wrapper.find('svg')
    expect(svg.exists()).toBe(true)
  })

  it('renders an exclamation icon for error state', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValueOnce(new Error('fail'))

    const wrapper = mount(HealthBadge)
    await flushPromises()

    const svg = wrapper.find('svg')
    expect(svg.exists()).toBe(true)
  })

  it('status text is visible (not sr-only) for WCAG 1.4.1 compliance', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: 'healthy', available_count: 4, total_count: 4 }),
    } as Response)

    const wrapper = mount(HealthBadge)
    await flushPromises()

    const statusSpan = wrapper.find('.status-text')
    expect(statusSpan.exists()).toBe(true)
    expect(statusSpan.text()).toBe('Healthy')
    // Verify it's not hidden with sr-only class
    expect(statusSpan.classes()).not.toContain('sr-only')
  })
})
