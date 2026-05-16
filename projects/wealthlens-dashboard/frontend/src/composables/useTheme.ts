import { ref, computed, onMounted, onUnmounted } from 'vue'

export type Theme = 'light' | 'dark'
export type ThemePreference = 'light' | 'dark' | 'system'

const STORAGE_KEY = 'wealthlens-theme'

const preference = ref<ThemePreference>('system')
const systemScheme = ref<Theme>('light')

let mql: MediaQueryList | null = null
let listenerAttached = false

function onMediaChange() {
  systemScheme.value = mql?.matches ? 'dark' : 'light'
}

export function _resetForTesting() {
  preference.value = 'system'
  systemScheme.value = 'light'
  if (mql && listenerAttached) {
    mql.removeEventListener('change', onMediaChange)
  }
  mql = null
  listenerAttached = false
}

export function useTheme() {
  const resolved = computed<Theme>(() =>
    preference.value === 'system' ? systemScheme.value : preference.value,
  )

  function setPreference(pref: ThemePreference) {
    preference.value = pref
    if (pref === 'system') {
      localStorage.removeItem(STORAGE_KEY)
    } else {
      localStorage.setItem(STORAGE_KEY, pref)
    }
    applyClass(resolved.value)
  }

  function applyClass(theme: Theme) {
    document.documentElement.classList.toggle('dark', theme === 'dark')
  }

  onMounted(() => {
    if (typeof window === 'undefined') return

    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored === 'light' || stored === 'dark') {
      preference.value = stored
    }

    if (!listenerAttached) {
      mql = window.matchMedia('(prefers-color-scheme: dark)')
      systemScheme.value = mql.matches ? 'dark' : 'light'
      mql.addEventListener('change', onMediaChange)
      listenerAttached = true
    }

    applyClass(resolved.value)
  })

  onUnmounted(() => {
    if (listenerAttached && mql) {
      mql.removeEventListener('change', onMediaChange)
      listenerAttached = false
    }
  })

  return { preference, resolved, setPreference }
}
