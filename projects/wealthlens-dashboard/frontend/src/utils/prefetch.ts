/**
 * Route prefetch utility.
 *
 * Prefetches route components after the browser is idle, so navigations
 * feel instant without blocking the initial page load.
 *
 * Usage:
 *   import { prefetchRouteComponent } from '@/utils/prefetch'
 *   prefetchRouteComponent(() => import('@/views/ChartView.vue'))
 */

type DynamicImportFn = () => Promise<unknown>

/**
 * Prefetch a route component using requestIdleCallback (with setTimeout fallback).
 * Accepts the same dynamic import function used in vue-router route definitions.
 *
 * @param importFn - A function returning a dynamic import promise
 * @param timeout - Maximum wait before forcing prefetch (ms, default 4000)
 */
export function prefetchRouteComponent(
  importFn: DynamicImportFn,
  timeout = 4000,
): void {
  const load = () => {
    // Fire the import; we don't need the result — the browser caches the chunk
    importFn().catch(() => {
      // Silently ignore prefetch failures — the route will load on demand
    })
  }

  if (typeof window === 'undefined') return

  if ('requestIdleCallback' in window) {
    ;(window as Window & { requestIdleCallback: (cb: () => void, opts?: { timeout: number }) => number })
      .requestIdleCallback(load, { timeout })
  } else {
    // Fallback for browsers without requestIdleCallback (Safari < 16.4)
    setTimeout(load, timeout)
  }
}

/**
 * Prefetch multiple route components in sequence after idle.
 *
 * @param importFns - Array of dynamic import functions to prefetch
 * @param timeout - Maximum wait before forcing each prefetch (ms)
 */
export function prefetchRouteComponents(
  importFns: DynamicImportFn[],
  timeout = 4000,
): void {
  for (const fn of importFns) {
    prefetchRouteComponent(fn, timeout)
  }
}
