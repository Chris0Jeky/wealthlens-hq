import { ref } from "vue";

const STORAGE_KEY = "theme";

function getInitialValue(): boolean {
  if (typeof window === "undefined") return false;
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored === "dark") return true;
  if (stored === "light") return false;
  return window.matchMedia("(prefers-color-scheme: dark)").matches;
}

function applyTheme(dark: boolean) {
  if (dark) {
    document.documentElement.classList.add("dark");
  } else {
    document.documentElement.classList.remove("dark");
  }
}

const isDark = ref(getInitialValue());
applyTheme(isDark.value);

const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
function handleSystemChange(e: MediaQueryListEvent) {
  if (!localStorage.getItem(STORAGE_KEY)) {
    isDark.value = e.matches;
    applyTheme(isDark.value);
  }
}
mediaQuery.addEventListener("change", handleSystemChange);

function toggle() {
  isDark.value = !isDark.value;
  localStorage.setItem(STORAGE_KEY, isDark.value ? "dark" : "light");
  applyTheme(isDark.value);
}

export function useDarkMode() {
  return { isDark, toggle };
}
