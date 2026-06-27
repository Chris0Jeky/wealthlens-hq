import { ref, watch, onUnmounted, type Ref } from "vue"

export function useDebounce<T>(source: Ref<T>, delay = 300): Ref<T> {
  const debounced = ref(source.value) as Ref<T>
  let timeout: ReturnType<typeof setTimeout> | null = null

  function clear() {
    if (timeout) {
      clearTimeout(timeout)
      timeout = null
    }
  }

  watch(source, (val) => {
    clear()
    timeout = setTimeout(() => {
      debounced.value = val
    }, delay)
  })

  onUnmounted(clear)

  return debounced
}
