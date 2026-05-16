import { ref, onMounted, onUnmounted, type Ref } from 'vue'

export interface ChartDimensions {
  width: number
  height: number
}

const MIN_HEIGHT = 200
const MAX_HEIGHT = 600
const ASPECT_RATIO = 0.5

export function useChartDimensions(
  containerRef: Ref<HTMLElement | null>,
): { dimensions: Ref<ChartDimensions> } {
  const dimensions = ref<ChartDimensions>({ width: 0, height: MIN_HEIGHT })
  let observer: ResizeObserver | null = null

  function update(width: number) {
    const h = Math.min(MAX_HEIGHT, Math.max(MIN_HEIGHT, Math.round(width * ASPECT_RATIO)))
    dimensions.value = { width, height: h }
  }

  onMounted(() => {
    const el = containerRef.value
    if (!el) return
    if (typeof ResizeObserver === 'undefined') return

    observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        update(entry.contentRect.width)
      }
    })
    observer.observe(el)
    update(el.clientWidth)
  })

  onUnmounted(() => {
    observer?.disconnect()
  })

  return { dimensions }
}
