import { ref, watchEffect } from "vue"

export type Theme = "light" | "dark"

const STORAGE_KEY = "wl-theme"
const OLD_STORAGE_KEY = "wealthlens-theme"

function migrateOldKey(): void {
  try {
    const old = localStorage.getItem(OLD_STORAGE_KEY)
    if (old === "light" || old === "dark") {
      localStorage.setItem(STORAGE_KEY, old)
      localStorage.removeItem(OLD_STORAGE_KEY)
    }
  } catch {
    // localStorage unavailable
  }
}

function getInitialTheme(): Theme {
  if (typeof window === "undefined") return "light"

  migrateOldKey()

  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored === "light" || stored === "dark") return stored
  } catch {
    // localStorage unavailable
  }

  if (typeof window.matchMedia === "function") {
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"
  }

  return "light"
}

function hasExplicitPreference(): boolean {
  try {
    return localStorage.getItem(STORAGE_KEY) !== null
  } catch {
    return false
  }
}

const theme = ref<Theme>(getInitialTheme())

function applyTheme() {
  if (typeof document === "undefined") return
  document.documentElement.setAttribute("data-theme", theme.value)
  document.documentElement.classList.toggle("dark", theme.value === "dark")
}

// Single module-scoped watcher — runs once regardless of how many components call useTheme()
let watcherCreated = false

function ensureWatcher() {
  if (watcherCreated) return
  watcherCreated = true
  watchEffect(applyTheme)
}

// Listen for system theme changes when no explicit preference is set
if (typeof window !== "undefined" && typeof window.matchMedia === "function") {
  const mql = window.matchMedia("(prefers-color-scheme: dark)")
  mql.addEventListener("change", (e) => {
    if (!hasExplicitPreference()) {
      theme.value = e.matches ? "dark" : "light"
    }
  })
}

applyTheme()

export function useTheme() {
  ensureWatcher()

  function toggleTheme() {
    theme.value = theme.value === "light" ? "dark" : "light"
    try {
      localStorage.setItem(STORAGE_KEY, theme.value)
    } catch {
      // localStorage unavailable
    }
    applyTheme()
  }

  return { theme, toggleTheme }
}

export function _resetForTesting(detectFromEnv = false) {
  watcherCreated = false
  if (detectFromEnv) {
    theme.value = getInitialTheme()
  } else {
    theme.value = "light"
  }
  applyTheme()
}
