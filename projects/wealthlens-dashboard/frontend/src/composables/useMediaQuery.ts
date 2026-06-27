import { ref, onUnmounted, type Ref } from "vue"

export function useMediaQuery(query: string): Ref<boolean> {
  const matches = ref(false)

  if (typeof window === "undefined" || typeof window.matchMedia !== "function") {
    return matches
  }

  const mql = window.matchMedia(query)
  matches.value = mql.matches

  function handler(event: MediaQueryListEvent) {
    matches.value = event.matches
  }

  mql.addEventListener("change", handler)

  onUnmounted(() => {
    mql.removeEventListener("change", handler)
  })

  return matches
}
