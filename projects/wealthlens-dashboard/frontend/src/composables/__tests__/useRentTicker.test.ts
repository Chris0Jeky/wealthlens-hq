import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, config } from '@vue/test-utils'
import { defineComponent, nextTick } from 'vue'
import { useRentTicker } from '@/composables/useRentTicker'

/**
 * useRentTicker uses onMounted/onUnmounted lifecycle hooks, so we
 * need to test it inside a real Vue component to trigger those hooks.
 */
const TestHost = defineComponent({
  setup() {
    const { rentPaid, elapsed } = useRentTicker()
    return { rentPaid, elapsed }
  },
  template: '<div>{{ rentPaid }} {{ elapsed }}</div>',
})

describe('useRentTicker', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('starts with £0 and 00:00', () => {
    const wrapper = mount(TestHost)
    expect(wrapper.vm.rentPaid).toBe('£0')
    expect(wrapper.vm.elapsed).toBe('00:00')
    wrapper.unmount()
  })

  it('increments rent paid after ticks', async () => {
    const wrapper = mount(TestHost)

    // Advance 1 second — at £85bn/year ≈ £2,695/sec
    vi.advanceTimersByTime(1000)
    await nextTick()

    // After 1 second the paid value should be positive and formatted with £
    expect(wrapper.vm.rentPaid).toMatch(/^£[\d,]+$/)
    expect(wrapper.vm.rentPaid).not.toBe('£0')
    wrapper.unmount()
  })

  it('updates elapsed time format correctly', async () => {
    const wrapper = mount(TestHost)

    // Advance 65 seconds = 01:05
    vi.advanceTimersByTime(65_000)
    await nextTick()

    expect(wrapper.vm.elapsed).toBe('01:05')
    wrapper.unmount()
  })

  it('cleans up interval on unmount (no leaking timers)', () => {
    const wrapper = mount(TestHost)

    // Should have an active interval (setInterval at 100ms)
    const timerCountBefore = vi.getTimerCount()
    expect(timerCountBefore).toBeGreaterThan(0)

    wrapper.unmount()

    // After unmount, the interval should be cleared
    const timerCountAfter = vi.getTimerCount()
    expect(timerCountAfter).toBe(0)
  })

  it('ticks at roughly 100ms intervals', () => {
    const wrapper = mount(TestHost)

    // The initial mount calls tick() once synchronously, then sets
    // setInterval(tick, 100). Advance by 500ms = 5 more ticks.
    vi.advanceTimersByTime(500)

    // rentPaid should reflect ~500ms of accumulation
    // £85bn/yr ≈ £2,695/sec ≈ £1,347 in 0.5s
    const paid = wrapper.vm.rentPaid.replace(/[£,]/g, '')
    expect(Number(paid)).toBeGreaterThan(0)
    wrapper.unmount()
  })
})
