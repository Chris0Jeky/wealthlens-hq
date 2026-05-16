import { ref } from 'vue'

const STORAGE_KEY = 'theme'

/**
 * Composable for managing dark mode state.
 *
 * Priority:
 * 1. localStorage 'theme' key (user's explicit choice)
 * 2. System preference via prefers-color-scheme media query
 *
 * Listens for system preference changes when no localStorage override exists.
 */
export function useDarkMode() {
  const isDark = ref(getInitialValue())

  /** Apply or remove the `dark` class on the root HTML element. */
  function applyTheme(dark: boolean) {
    if (dark) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  /** Toggle between light and dark mode and persist the choice. */
  function toggle() {
    isDark.value = !isDark.value
    localStorage.setItem(STORAGE_KEY, isDark.value ? 'dark' : 'light')
    applyTheme(isDark.value)
  }

  // Apply theme on init
  applyTheme(isDark.value)

  // Listen for system preference changes when no explicit user override
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  const handleSystemChange = (e: MediaQueryListEvent) => {
    if (!localStorage.getItem(STORAGE_KEY)) {
      isDark.value = e.matches
      applyTheme(isDark.value)
    }
  }
  mediaQuery.addEventListener('change', handleSystemChange)

  return { isDark, toggle }
}

/** Determine initial dark mode value from localStorage or system preference. */
function getInitialValue(): boolean {
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored === 'dark') return true
  if (stored === 'light') return false
  return window.matchMedia('(prefers-color-scheme: dark)').matches
}
