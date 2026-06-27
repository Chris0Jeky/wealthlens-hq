import { ref, onUnmounted } from "vue"

const query = "(prefers-reduced-motion: reduce)"

export function useReducedMotion() {
  const prefersReducedMotion = ref(false)

  if (typeof window === "undefined" || typeof window.matchMedia !== "function") {
    return { prefersReducedMotion }
  }

  const mql = window.matchMedia(query)
  prefersReducedMotion.value = mql.matches

  function onChange(event: MediaQueryListEvent) {
    prefersReducedMotion.value = event.matches
  }

  mql.addEventListener("change", onChange)
  onUnmounted(() => mql.removeEventListener("change", onChange))

  return { prefersReducedMotion }
}
