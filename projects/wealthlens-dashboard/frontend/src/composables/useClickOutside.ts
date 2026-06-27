import { onUnmounted, type Ref, watch } from "vue"

export function useClickOutside(target: Ref<HTMLElement | null>, handler: () => void) {
  function listener(event: Event) {
    const el = target.value
    if (!el || el === event.target || el.contains(event.target as Node)) return
    handler()
  }

  let active = false

  function start() {
    if (active) return
    document.addEventListener("pointerdown", listener, true)
    active = true
  }

  function stop() {
    if (!active) return
    document.removeEventListener("pointerdown", listener, true)
    active = false
  }

  watch(
    target,
    (el) => {
      if (el) start()
      else stop()
    },
    { immediate: true },
  )

  onUnmounted(stop)

  return { start, stop }
}
