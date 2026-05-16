import { ref, shallowRef, watch, type Ref } from 'vue'

export interface UseFetchOptions {
  immediate?: boolean
}

export interface UseFetchReturn<T> {
  data: Ref<T | null>
  error: Ref<string | null>
  loading: Ref<boolean>
  execute: () => Promise<void>
}

export function useFetch<T = unknown>(
  url: Ref<string> | string,
  options: UseFetchOptions = {},
): UseFetchReturn<T> {
  const { immediate = true } = options

  const data = shallowRef<T | null>(null)
  const error = ref<string | null>(null)
  const loading = ref(false)

  let abortController: AbortController | null = null

  async function execute() {
    if (abortController) {
      abortController.abort()
    }
    abortController = new AbortController()

    loading.value = true
    error.value = null

    const resolvedUrl = typeof url === 'string' ? url : url.value

    try {
      const response = await fetch(resolvedUrl, { signal: abortController.signal })
      if (!response.ok) {
        error.value = `HTTP ${response.status}: ${response.statusText}`
        data.value = null
      } else {
        data.value = (await response.json()) as T
      }
    } catch (e) {
      if (e instanceof DOMException && e.name === 'AbortError') return
      error.value = e instanceof Error ? e.message : 'Unknown error'
      data.value = null
    } finally {
      loading.value = false
    }
  }

  if (typeof url !== 'string') {
    watch(url, () => {
      execute()
    })
  }

  if (immediate) {
    execute()
  }

  return { data, error, loading, execute }
}
