import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ref, nextTick } from 'vue'
import { mount } from '@vue/test-utils'
import { defineComponent } from 'vue'
import { useFetch } from '@/composables/useFetch'

function withSetup<T>(composable: () => T): { result: T; unmount: () => void } {
  let result!: T
  const Wrapper = defineComponent({
    setup() {
      result = composable()
      return {}
    },
    template: '<div />',
  })
  const wrapper = mount(Wrapper)
  return { result, unmount: () => wrapper.unmount() }
}

describe('useFetch', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  function mockFetchResponse(body: unknown, status = 200, statusText = 'OK') {
    ;(fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
      ok: status >= 200 && status < 300,
      status,
      statusText,
      json: () => Promise.resolve(body),
    })
  }

  it('fetches data immediately by default', async () => {
    mockFetchResponse({ items: [1, 2] })
    const { result } = withSetup(() => useFetch<{ items: number[] }>('/api/data'))
    await vi.waitFor(() => {
      expect(result.data.value).toEqual({ items: [1, 2] })
    })
  })

  it('sets loading to true during fetch', () => {
    ;(fetch as ReturnType<typeof vi.fn>).mockReturnValue(new Promise(() => {}))
    const { result } = withSetup(() => useFetch('/api/data'))
    expect(result.loading.value).toBe(true)
  })

  it('sets loading to false after fetch completes', async () => {
    mockFetchResponse({ ok: true })
    const { result } = withSetup(() => useFetch('/api/data'))
    await vi.waitFor(() => {
      expect(result.loading.value).toBe(false)
    })
  })

  it('sets error on non-2xx response', async () => {
    mockFetchResponse(null, 404, 'Not Found')
    const { result } = withSetup(() => useFetch('/api/missing'))
    await vi.waitFor(() => {
      expect(result.error.value).toBe('HTTP 404: Not Found')
    })
    expect(result.data.value).toBeNull()
  })

  it('sets error on network failure', async () => {
    ;(fetch as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('Network error'))
    const { result } = withSetup(() => useFetch('/api/data'))
    await vi.waitFor(() => {
      expect(result.error.value).toBe('Network error')
    })
  })

  it('does not fetch immediately when immediate is false', () => {
    mockFetchResponse({ ok: true })
    withSetup(() => useFetch('/api/data', { immediate: false }))
    expect(fetch).not.toHaveBeenCalled()
  })

  it('execute() triggers fetch manually', async () => {
    mockFetchResponse({ value: 42 })
    const { result } = withSetup(() => useFetch<{ value: number }>('/api/data', { immediate: false }))
    expect(result.data.value).toBeNull()
    await result.execute()
    expect(result.data.value).toEqual({ value: 42 })
  })

  it('re-fetches when reactive URL changes', async () => {
    mockFetchResponse({ page: 1 })
    const url = ref('/api/data?page=1')
    const { result } = withSetup(() => useFetch<{ page: number }>(url))
    await vi.waitFor(() => {
      expect(result.data.value).toEqual({ page: 1 })
    })
    mockFetchResponse({ page: 2 })
    url.value = '/api/data?page=2'
    await nextTick()
    await vi.waitFor(() => {
      expect(result.data.value).toEqual({ page: 2 })
    })
  })

  it('a superseded (stale) fetch cannot clear loading or overwrite fresh data', async () => {
    // First request hangs; the second resolves. When the first finally resolves it
    // must not flip loading back on/off or clobber the second's data.
    let resolveFirst!: (v: unknown) => void
    const firstResponse = { ok: true, status: 200, json: () => Promise.resolve({ stale: true }) }
    ;(fetch as ReturnType<typeof vi.fn>)
      .mockReturnValueOnce(new Promise((r) => (resolveFirst = r)))
      .mockResolvedValue({ ok: true, status: 200, json: () => Promise.resolve({ fresh: true }) })

    const url = ref('/first')
    const { result } = withSetup(() => useFetch(url))
    await nextTick()
    url.value = '/second' // supersede the first (still pending) request
    await vi.waitFor(() => {
      expect(result.data.value).toEqual({ fresh: true })
      expect(result.loading.value).toBe(false)
    })

    resolveFirst(firstResponse) // the stale request finally resolves
    await nextTick()
    await nextTick()
    expect(result.data.value).toEqual({ fresh: true }) // not clobbered
    expect(result.loading.value).toBe(false) // not re-toggled
  })

  it('a superseded fetch cannot overwrite fresh data after its json() resolves late', async () => {
    // Regression for the second async boundary: the first request's HEADERS arrive
    // while it is still current (passing the post-fetch guard), then the user
    // switches before its BODY parses. The freshness check must run again after
    // json() resolves, or the stale body clobbers the fresh data.
    let resolveFirstJson!: (v: unknown) => void
    const firstResponse = {
      ok: true,
      status: 200,
      json: () => new Promise((r) => (resolveFirstJson = r)),
    }
    ;(fetch as ReturnType<typeof vi.fn>)
      .mockResolvedValueOnce(firstResponse)
      .mockResolvedValue({ ok: true, status: 200, json: () => Promise.resolve({ fresh: true }) })

    const url = ref('/first')
    const { result } = withSetup(() => useFetch(url))
    // Let the first request get past `await fetch()` and park on `await json()`.
    await nextTick()
    await nextTick()

    url.value = '/second' // supersede before the first body parses
    await vi.waitFor(() => {
      expect(result.data.value).toEqual({ fresh: true })
    })

    resolveFirstJson({ stale: true }) // the first body parses late
    await nextTick()
    await nextTick()
    expect(result.data.value).toEqual({ fresh: true }) // not clobbered by stale body
  })
})
