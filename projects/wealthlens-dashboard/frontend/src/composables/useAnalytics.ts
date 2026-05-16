/**
 * Plausible analytics composable — privacy-respecting, opt-in tracking.
 *
 * Analytics is enabled only when VITE_PLAUSIBLE_DOMAIN is set.
 * Plausible is cookieless and GDPR-compliant; no consent banner needed.
 * The script loads lazily after page mount to avoid blocking render.
 */
import { ref } from 'vue'

interface PlausibleWindow {
  plausible?: ((...args: unknown[]) => void) & { q?: unknown[][] }
}

const initialized = ref(false)

export function useAnalytics() {
  const domain =
    ((import.meta.env.VITE_PLAUSIBLE_DOMAIN as string | undefined) ?? '').trim() || undefined

  function init() {
    if (initialized.value || !domain || typeof window === 'undefined') return
    initialized.value = true

    const w = window as unknown as PlausibleWindow
    w.plausible =
      w.plausible ||
      Object.assign(
        function (...args: unknown[]) {
          ;(w.plausible!.q = w.plausible!.q || []).push(args)
        },
        { q: [] as unknown[][] },
      )

    const script = document.createElement('script')
    script.defer = true
    script.dataset.domain = domain
    script.src = 'https://plausible.io/js/script.js'
    script.onerror = () => {
      console.warn(
        '[WealthLens] Plausible analytics script failed to load. ' +
          'This is expected if an ad-blocker is active.',
      )
      w.plausible = function () {}
    }
    document.head.appendChild(script)
  }

  function trackEvent(name: string, props?: Record<string, string | number>) {
    if (!domain) return
    if (!initialized.value) init()

    const w = window as unknown as PlausibleWindow
    if (w.plausible) {
      w.plausible(name, { props })
    }
  }

  return { init, trackEvent, isEnabled: !!domain }
}
