import { ref, onMounted, onUnmounted, type Ref } from 'vue'

export interface UseIntersectionObserverOptions {
  threshold?: number
  rootMargin?: string
  once?: boolean
}

export function useIntersectionObserver(
  target: Ref<HTMLElement | null>,
  options: UseIntersectionObserverOptions = {},
) {
  const isVisible = ref(false)
  let observer: IntersectionObserver | null = null

  const { threshold = 0.1, rootMargin = '0px', once = true } = options

  onMounted(() => {
    if (typeof window === 'undefined' || !('IntersectionObserver' in window)) {
      isVisible.value = true
      return
    }

    observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          isVisible.value = true
          if (once && observer && target.value) {
            observer.unobserve(target.value)
          }
        } else if (!once) {
          isVisible.value = false
        }
      },
      { threshold, rootMargin },
    )

    if (target.value) {
      observer.observe(target.value)
    }
  })

  onUnmounted(() => {
    observer?.disconnect()
    observer = null
  })

  return { isVisible }
}
