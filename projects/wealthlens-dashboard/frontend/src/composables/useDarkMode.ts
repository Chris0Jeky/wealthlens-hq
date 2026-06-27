import { ref } from "vue"
import { getStorageItem, setStorageItem } from "@/utils/browserStorage"

const STORAGE_KEY = "theme"

function getInitialValue(): boolean {
  if (typeof window === "undefined") return false
  const stored = getStorageItem(STORAGE_KEY)
  if (stored === "dark") return true
  if (stored === "light") return false
  if (typeof window.matchMedia !== "function") return false
  return window.matchMedia("(prefers-color-scheme: dark)").matches
}

function applyTheme(dark: boolean) {
  if (typeof document === "undefined") return
  if (dark) {
    document.documentElement.classList.add("dark")
  } else {
    document.documentElement.classList.remove("dark")
  }
}

const isDark = ref(getInitialValue())
applyTheme(isDark.value)

function handleSystemChange(e: MediaQueryListEvent) {
  if (!getStorageItem(STORAGE_KEY)) {
    isDark.value = e.matches
    applyTheme(isDark.value)
  }
}

if (typeof window !== "undefined" && typeof window.matchMedia === "function") {
  const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)")
  mediaQuery.addEventListener("change", handleSystemChange)
}

function toggle() {
  isDark.value = !isDark.value
  setStorageItem(STORAGE_KEY, isDark.value ? "dark" : "light")
  applyTheme(isDark.value)
}

export function useDarkMode() {
  return { isDark, toggle }
}
