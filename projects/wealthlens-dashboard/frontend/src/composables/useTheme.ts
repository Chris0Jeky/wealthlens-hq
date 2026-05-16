import { ref, watchEffect } from 'vue'

export type Theme = 'light' | 'dark'

const STORAGE_KEY = 'wl-theme'

function getInitialTheme(): Theme {
  if (typeof window === 'undefined') return 'light'

  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored === 'light' || stored === 'dark') return stored
  } catch {
    // localStorage unavailable
  }

  if (typeof window.matchMedia === 'function') {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  }

  return 'light'
}

const theme = ref<Theme>(getInitialTheme())

function applyTheme() {
  if (typeof document === 'undefined') return
  document.documentElement.setAttribute('data-theme', theme.value)
}

applyTheme()

export function useTheme() {
  watchEffect(applyTheme)

  function toggleTheme() {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    try {
      localStorage.setItem(STORAGE_KEY, theme.value)
    } catch {
      // localStorage unavailable
    }
    applyTheme()
  }

  return { theme, toggleTheme }
}

export function _resetForTesting() {
  theme.value = 'light'
  if (typeof document !== 'undefined') {
    document.documentElement.removeAttribute('data-theme')
  }
}
