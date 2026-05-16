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
})
