import { ref } from 'vue'

const initialized = ref(false)

export function useAnalytics() {
  const domain = import.meta.env.VITE_PLAUSIBLE_DOMAIN as string | undefined

  function init() {
    if (initialized.value || !domain || typeof window === 'undefined') return
    initialized.value = true

    // Queue shim: buffer events sent before the async script loads.
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const w = window as any
    w.plausible =
      w.plausible ||
      function (...args: unknown[]) {
        ;(w.plausible.q = w.plausible.q || []).push(args)
      }

    const script = document.createElement('script')
    script.defer = true
    script.dataset.domain = domain
    script.src = 'https://plausible.io/js/script.js'
    document.head.appendChild(script)
  }

  function trackEvent(name: string, props?: Record<string, string | number>) {
    if (!domain) return
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const w = window as any
    if (w.plausible) {
      w.plausible(name, { props })
    }
  }

  return { init, trackEvent, isEnabled: !!domain }
}
