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
  })

  it('shows healthy state with dataset count', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: 'healthy', available_count: 4, total_count: 4 }),
    } as Response)

    const wrapper = mount(HealthBadge)
    await flushPromises()

    expect(wrapper.text()).toBe('4/4 datasets')
    expect(wrapper.find('span').classes()).toContain('bg-green-100')
  })

  it('shows degraded state', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: 'degraded', available_count: 2, total_count: 4 }),
    } as Response)

    const wrapper = mount(HealthBadge)
    await flushPromises()

    expect(wrapper.text()).toBe('2/4 datasets')
    expect(wrapper.find('span').classes()).toContain('bg-yellow-100')
  })

  it('shows error state on fetch failure', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValueOnce(new Error('fail'))

    const wrapper = mount(HealthBadge)
    await flushPromises()

    expect(wrapper.text()).toBe('Status unknown')
    expect(wrapper.find('span').classes()).toContain('bg-gray-100')
  })

  it('has accessible role and aria-label', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: 'healthy', available_count: 4, total_count: 4 }),
    } as Response)

    const wrapper = mount(HealthBadge)
    await flushPromises()

    const badge = wrapper.find('[role="status"]')
    expect(badge.exists()).toBe(true)
    expect(badge.attributes('aria-label')).toBe('Data status: healthy')
  })
})
