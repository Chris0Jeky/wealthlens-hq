import { ref, shallowRef, watch, type Ref } from "vue"

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

    const resolvedUrl = typeof url === "string" ? url : url.value
    if (!resolvedUrl) {
      // No URL (e.g. a reactive id was cleared) — hold off rather than fetch('')
      // against the page origin, which returns the app's HTML with ok=true and then
      // throws on response.json(), leaving a spurious "Unexpected token <" error.
      //
      // Also INVALIDATE any in-flight request: we aborted it above, but a request
      // already parsing response.json() may still resolve. Nulling abortController
      // makes its isCurrent() check false so it cannot write data for the cleared
      // URL. Clear stale data/error to match the "no URL → no data" state.
      abortController = null
      data.value = null
      error.value = null
      loading.value = false
      return
    }

    const controller = new AbortController()
    abortController = controller
    // Only the latest call may mutate state: a superseded (aborted) call that
    // resolves later must not clear the new call's loading flag or overwrite its
    // data (rapid scenario switching A -> B -> C).
    const isCurrent = () => abortController === controller

    loading.value = true
    error.value = null

    try {
      const response = await fetch(resolvedUrl, { signal: controller.signal })
      if (!isCurrent()) return
      if (!response.ok) {
        error.value = `HTTP ${response.status}: ${response.statusText}`
        data.value = null
      } else {
        // Parsing the body is a SECOND async boundary after the headers-level
        // isCurrent() check above. Buffer the result and re-check freshness
        // before assigning, so a superseded request (A) whose json() resolves
        // after the user switched to B cannot overwrite B's data.
        const parsed = (await response.json()) as T
        if (!isCurrent()) return
        data.value = parsed
      }
    } catch (e) {
      if (e instanceof DOMException && e.name === "AbortError") return
      if (!isCurrent()) return
      error.value = e instanceof Error ? e.message : "Unknown error"
      data.value = null
    } finally {
      if (isCurrent()) loading.value = false
    }
  }

  if (typeof url !== "string") {
    watch(url, () => {
      execute()
    })
  }

  if (immediate) {
    execute()
  }

  return { data, error, loading, execute }
}
