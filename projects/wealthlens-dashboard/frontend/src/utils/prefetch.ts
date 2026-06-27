type DynamicImportFn = () => Promise<unknown>

const prefetched = new Set<DynamicImportFn>()

export function prefetchRouteComponent(importFn: DynamicImportFn, timeout = 4000): void {
  if (prefetched.has(importFn)) return
  prefetched.add(importFn)

  const load = () => {
    importFn().catch(() => {})
  }

  if (typeof window === "undefined") return

  if ("requestIdleCallback" in window) {
    ;(
      window as Window & {
        requestIdleCallback: (cb: () => void, opts?: { timeout: number }) => number
      }
    ).requestIdleCallback(load, { timeout })
  } else {
    setTimeout(load, timeout)
  }
}

export function prefetchRouteComponents(
  importFns: DynamicImportFn[],
  timeout = 4000,
  stagger = 500,
): void {
  for (let i = 0; i < importFns.length; i++) {
    prefetchRouteComponent(importFns[i], timeout + i * stagger)
  }
}
