import { onMounted, onUnmounted, type Ref, watch, isRef } from "vue"

type Target = EventTarget | Ref<EventTarget | null | undefined>

export function useEventListener<K extends keyof WindowEventMap>(
  target: Target,
  event: K,
  handler: (evt: WindowEventMap[K]) => void,
  options?: boolean | AddEventListenerOptions,
): void {
  function add(el: EventTarget) {
    el.addEventListener(event, handler as EventListener, options)
  }

  function remove(el: EventTarget) {
    el.removeEventListener(event, handler as EventListener, options)
  }

  if (isRef(target)) {
    watch(
      target,
      (newEl, oldEl) => {
        if (oldEl) remove(oldEl)
        if (newEl) add(newEl)
      },
      { immediate: true },
    )
    onUnmounted(() => {
      if (target.value) remove(target.value)
    })
  } else {
    onMounted(() => add(target))
    onUnmounted(() => remove(target))
  }
}
