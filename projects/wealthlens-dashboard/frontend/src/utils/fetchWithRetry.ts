const DEFAULT_MAX_RETRIES = 3
const DEFAULT_BACKOFF_BASE = 300

/**
 * Fetch wrapper with exponential backoff retry.
 *
 * Retries on network errors and 5xx server errors.
 * Does NOT retry on 4xx client errors (e.g. 404).
 * Backoff schedule (default): 300ms, 600ms, 1200ms.
 */
export async function fetchWithRetry(
  url: string,
  options?: RequestInit,
  maxRetries = DEFAULT_MAX_RETRIES,
  backoffBase = DEFAULT_BACKOFF_BASE,
): Promise<Response> {
  let lastError: Error | null = null
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const res = await fetch(url, options)
      if (res.status < 500) return res
      lastError = new Error(`HTTP ${res.status}`)
    } catch (e) {
      lastError = e instanceof Error ? e : new Error(String(e))
    }
    if (attempt < maxRetries) {
      await new Promise((r) => setTimeout(r, backoffBase * 2 ** attempt))
    }
  }
  throw lastError
}
