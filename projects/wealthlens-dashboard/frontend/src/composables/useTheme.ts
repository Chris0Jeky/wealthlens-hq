import { ref, computed } from 'vue'

export type Theme = 'light' | 'dark'
export type ThemePreference = 'light' | 'dark' | 'system'

const STORAGE_KEY = 'wealthlens-theme'

const preference = ref<ThemePreference>('system')
const systemScheme = ref<Theme>('light')

let mql: MediaQueryList | null = null
let initialised = false

function onMediaChange() {
  systemScheme.value = mql?.matches ? 'dark' : 'light'
  applyClass()
}

function applyClass() {
  if (typeof document === 'undefined') return
  const theme: Theme = preference.value === 'system' ? systemScheme.value : preference.value
  document.documentElement.classList.toggle('dark', theme === 'dark')
}

function safeStorage(action: 'get'): string | null
function safeStorage(action: 'set', value: string): void
function safeStorage(action: 'remove'): void
function safeStorage(action: 'get' | 'set' | 'remove', value?: string): string | null | void {
  try {
    if (action === 'get') return localStorage.getItem(STORAGE_KEY)
    if (action === 'set' && value != null) localStorage.setItem(STORAGE_KEY, value)
    if (action === 'remove') localStorage.removeItem(STORAGE_KEY)
  } catch {
    return null
  }
}

function init() {
  if (initialised || typeof window === 'undefined' || typeof window.matchMedia !== 'function') return
  initialised = true

  const stored = safeStorage('get')
  if (stored === 'light' || stored === 'dark') {
    preference.value = stored
  }

  mql = window.matchMedia('(prefers-color-scheme: dark)')
  systemScheme.value = mql.matches ? 'dark' : 'light'
  mql.addEventListener('change', onMediaChange)
  applyClass()
}

init()

export function _resetForTesting() {
  if (mql) mql.removeEventListener('change', onMediaChange)
  mql = null
  initialised = false
  preference.value = 'system'
  systemScheme.value = 'light'
}

export function useTheme() {
  init()

  const resolved = computed<Theme>(() =>
    preference.value === 'system' ? systemScheme.value : preference.value,
  )

  function setPreference(pref: ThemePreference) {
    preference.value = pref
    if (pref === 'system') {
      safeStorage('remove')
    } else {
      safeStorage('set', pref)
    }
    applyClass()
  }

  return { preference, resolved, setPreference }
}
