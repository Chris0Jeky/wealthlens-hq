/**
 * useTheme — composable for cycling between three broadsheet themes.
 *
 * Themes:
 *   'light'  → "Front Page"  (default cream, no data-theme attribute)
 *   'dark'   → "Late Edition" (data-theme="dark")
 *   'stark'  → "Stark"       (data-theme="stark")
 *
 * Persists choice in localStorage under `wl-theme`.
 * Falls back to system `prefers-color-scheme: dark` on first visit.
 */

import { ref, watch } from 'vue'

export type ThemeName = 'light' | 'dark' | 'stark'

/** Human-readable labels used in UI and aria text. */
export const THEME_LABELS: Record<ThemeName, string> = {
  light: 'Front Page',
  dark: 'Late Edition',
  stark: 'Stark',
}

/** Cycle order when the user clicks the toggle. */
const CYCLE: ThemeName[] = ['light', 'dark', 'stark']

const STORAGE_KEY = 'wl-theme'

/** Detect OS-level dark-mode preference. */
function systemPrefersDark(): boolean {
  if (typeof window === 'undefined') return false
  return window.matchMedia('(prefers-color-scheme: dark)').matches
}

/** Apply the theme to the document root. */
function applyTheme(theme: ThemeName): void {
  if (typeof document === 'undefined') return
  if (theme === 'light') {
    delete document.documentElement.dataset.theme
  } else {
    document.documentElement.dataset.theme = theme
  }
}

/** Read persisted theme, falling back to system preference then light. */
function resolveInitialTheme(): ThemeName {
  if (typeof localStorage !== 'undefined') {
    const stored = localStorage.getItem(STORAGE_KEY) as ThemeName | null
    if (stored && CYCLE.includes(stored)) return stored
  }
  return systemPrefersDark() ? 'dark' : 'light'
}

// Module-level singleton so every component shares one reactive ref.
const currentTheme = ref<ThemeName>(resolveInitialTheme())
let listenerAttached = false

/**
 * Composable entry point.
 *
 * Call once in App.vue to initialise; call again anywhere to read or
 * mutate the current theme.
 */
// One-time setup: watch + mediaQuery listener are app-lifetime singletons.
if (typeof window !== 'undefined' && !listenerAttached) {
  listenerAttached = true

  watch(currentTheme, (next) => {
    applyTheme(next)
    try {
      localStorage.setItem(STORAGE_KEY, next)
    } catch {
      // localStorage may be unavailable (private browsing, quota, etc.)
    }
  })

  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  mediaQuery.addEventListener('change', (e: MediaQueryListEvent) => {
    if (!localStorage.getItem(STORAGE_KEY)) {
      currentTheme.value = e.matches ? 'dark' : 'light'
    }
  })
}

export function useTheme() {
  applyTheme(currentTheme.value)

  /** Cycle to the next theme in order. */
  function toggleTheme(): void {
    const idx = CYCLE.indexOf(currentTheme.value)
    currentTheme.value = CYCLE[(idx + 1) % CYCLE.length]
  }

  /** Jump directly to a named theme. */
  function setTheme(name: ThemeName): void {
    currentTheme.value = name
  }

  return {
    currentTheme,
    toggleTheme,
    setTheme,
    THEME_LABELS,
  }
}
