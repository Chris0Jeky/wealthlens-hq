import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import HealthStatus from '@/components/HealthStatus.vue'

describe('HealthStatus', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.restoreAllMocks()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('shows checking state initially', () => {
    vi.spyOn(globalThis, 'fetch').mockReturnValueOnce(new Promise(() => {}))
    const wrapper = mount(HealthStatus)
    expect(wrapper.text()).toContain('Checking API')
  })

  it('shows connected state with version and dataset count', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        version: '0.2.0',
        datasets_available: 10,
        status: 'ok',
      }),
    } as Response)

    const wrapper = mount(HealthStatus)
    await flushPromises()

    expect(wrapper.text()).toBe('v0.2.0 · 10 datasets')
    expect(wrapper.find('.health-dot').classes()).toContain('bg-green-500')
  })

  it('shows disconnected state on fetch failure', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValueOnce(new Error('Network error'))

    const wrapper = mount(HealthStatus)
    await flushPromises()

    expect(wrapper.text()).toBe('API offline')
    expect(wrapper.find('.health-dot').classes()).toContain('bg-red-500')
  })

  it('shows disconnected state on non-ok response', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: false,
      status: 500,
    } as Response)

    const wrapper = mount(HealthStatus)
    await flushPromises()

    expect(wrapper.text()).toBe('API offline')
    expect(wrapper.find('.health-dot').classes()).toContain('bg-red-500')
  })

  it('has accessible role and aria-label', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        version: '0.2.0',
        datasets_available: 10,
        status: 'ok',
      }),
    } as Response)

    const wrapper = mount(HealthStatus)
    await flushPromises()

    const status = wrapper.find('[role="status"]')
    expect(status.exists()).toBe(true)
    expect(status.attributes('aria-label')).toBe('Backend status: connected')
  })

  it('polls every 60 seconds', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({
        version: '0.2.0',
        datasets_available: 10,
        status: 'ok',
      }),
    } as Response)

    mount(HealthStatus)
    await flushPromises()

    // Initial fetch on mount
    expect(fetchSpy).toHaveBeenCalledTimes(1)

    // Advance 60 seconds
    vi.advanceTimersByTime(60_000)
    await flushPromises()

    expect(fetchSpy).toHaveBeenCalledTimes(2)
  })

  it('checks health on visibility change to visible', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({
        version: '0.2.0',
        datasets_available: 10,
        status: 'ok',
      }),
    } as Response)

    mount(HealthStatus)
    await flushPromises()

    const callsAfterMount = fetchSpy.mock.calls.length

    // Simulate visibility change to visible
    Object.defineProperty(document, 'visibilityState', {
      value: 'visible',
      writable: true,
    })
    document.dispatchEvent(new Event('visibilitychange'))
    await flushPromises()

    // Should have made at least one additional call after the visibility change
    expect(fetchSpy.mock.calls.length).toBeGreaterThan(callsAfterMount)
  })

  it('cleans up timer and listener on unmount', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({
        version: '0.2.0',
        datasets_available: 10,
        status: 'ok',
      }),
    } as Response)

    const wrapper = mount(HealthStatus)
    await flushPromises()

    const clearIntervalSpy = vi.spyOn(globalThis, 'clearInterval')
    const removeListenerSpy = vi.spyOn(document, 'removeEventListener')

    wrapper.unmount()

    expect(clearIntervalSpy).toHaveBeenCalled()
    expect(removeListenerSpy).toHaveBeenCalledWith(
      'visibilitychange',
      expect.any(Function),
    )
  })

  it('passes AbortController signal to fetch', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({
        version: '0.2.0',
        datasets_available: 10,
        status: 'ok',
      }),
    } as Response)

    mount(HealthStatus)
    await flushPromises()

    // Verify fetch was called with a signal option
    expect(fetchSpy).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({ signal: expect.any(AbortSignal) }),
    )
  })

  it('does not update state on aborted request after unmount', async () => {
    // Simulate an abort error being thrown on fetch
    const abortError = new DOMException('The operation was aborted.', 'AbortError')
    vi.spyOn(globalThis, 'fetch').mockRejectedValueOnce(abortError)

    const wrapper = mount(HealthStatus)
    await flushPromises()

    // State should still be 'checking' — abort errors are ignored
    // (In practice, the component would have been unmounted, but this
    // tests that the catch handler properly ignores AbortError)
    expect(wrapper.text()).toContain('Checking API')
  })
})
