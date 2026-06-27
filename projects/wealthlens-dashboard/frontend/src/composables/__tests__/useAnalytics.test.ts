import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

/**
 * Unit tests for the Plausible analytics composable.
 *
 * Two things make this composable awkward to test, both handled here:
 *  - `isEnabled`/`domain` are read from import.meta.env.VITE_PLAUSIBLE_DOMAIN at
 *    call time -> stub it with vi.stubEnv before calling useAnalytics().
 *  - `initialized` is module-level singleton state -> vi.resetModules() + a fresh
 *    dynamic import per test so init-once behaviour is tested cleanly.
 */
type UseAnalytics = typeof import("../useAnalytics").useAnalytics

interface PlausibleWindow {
  plausible?: ((...args: unknown[]) => void) & { q?: unknown[][] }
}

function plausibleScripts(): HTMLScriptElement[] {
  return Array.from(document.head.querySelectorAll<HTMLScriptElement>('script[src*="plausible"]'))
}

async function loadFresh(domain: string): Promise<ReturnType<UseAnalytics>> {
  vi.stubEnv("VITE_PLAUSIBLE_DOMAIN", domain)
  vi.resetModules()
  const { useAnalytics } = await import("../useAnalytics")
  return useAnalytics()
}

describe("useAnalytics", () => {
  function resetGlobals() {
    delete (window as unknown as PlausibleWindow).plausible
    plausibleScripts().forEach((s) => s.remove())
  }

  beforeEach(resetGlobals)

  afterEach(() => {
    vi.unstubAllEnvs()
    vi.resetModules()
    // Mirror the global/DOM cleanup in afterEach too, so the document + window
    // are left pristine regardless of vitest isolation settings (defensive: if
    // isolate:false is ever set, the final test's injected script/global would
    // otherwise leak into another file).
    resetGlobals()
  })

  it("is disabled and trackEvent is a no-op when the domain is unset", async () => {
    const a = await loadFresh("")
    expect(a.isEnabled).toBe(false)

    a.trackEvent("chart_view", { chart: "wealth-shares" })

    // No script injected, no global created — fully inert without a domain.
    expect((window as unknown as PlausibleWindow).plausible).toBeUndefined()
    expect(plausibleScripts()).toHaveLength(0)
  })

  it("is enabled and init() injects one deferred Plausible script for the domain", async () => {
    const a = await loadFresh("wealthlens.uk")
    expect(a.isEnabled).toBe(true)

    a.init()

    const scripts = plausibleScripts()
    expect(scripts).toHaveLength(1)
    expect(scripts[0].dataset.domain).toBe("wealthlens.uk")
    expect(scripts[0].defer).toBe(true)
  })

  it("init() is idempotent — calling it twice injects only one script", async () => {
    const a = await loadFresh("wealthlens.uk")
    a.init()
    a.init()
    expect(plausibleScripts()).toHaveLength(1)
  })

  it("trackEvent queues the event (name + props) via window.plausible when enabled", async () => {
    const a = await loadFresh("wealthlens.uk")

    a.trackEvent("chart_view", { chart: "wealth-shares" })

    const w = window as unknown as PlausibleWindow
    expect(typeof w.plausible).toBe("function")
    // Before the real script loads, the stub queues calls onto `.q`.
    expect(w.plausible?.q).toEqual([["chart_view", { props: { chart: "wealth-shares" } }]])
  })
})
