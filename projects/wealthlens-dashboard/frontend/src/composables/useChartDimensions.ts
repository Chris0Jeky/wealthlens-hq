import { ref, onMounted, onBeforeUnmount, type Ref } from 'vue'

export interface ChartDimensions {
  width: number
  height: number
}

const MIN_HEIGHT = 300
const MAX_HEIGHT = 600
const ASPECT_RATIO = 0.56

/**
 * Tracks container width via ResizeObserver and computes a responsive chart
 * height using a fixed aspect ratio clamped between MIN_HEIGHT and MAX_HEIGHT.
 */
export function useChartDimensions(
  containerRef: Ref<HTMLElement | null>,
): { dimensions: Ref<ChartDimensions> } {
  const dimensions = ref<ChartDimensions>({ width: 0, height: MIN_HEIGHT })
  let observer: ResizeObserver | null = null

  function update(width: number): void {
    const height = Math.round(
      Math.min(MAX_HEIGHT, Math.max(MIN_HEIGHT, width * ASPECT_RATIO)),
    )
    dimensions.value = { width: Math.round(width), height }
  }

  onMounted(() => {
    const el = containerRef.value
    if (!el) return

    observer = new ResizeObserver((entries) => {
      const entry = entries[0]
      if (entry) {
        update(entry.contentRect.width)
      }
    })
    observer.observe(el)

    update(el.clientWidth)
  })

  onBeforeUnmount(() => {
    observer?.disconnect()
    observer = null
  })

  return { dimensions }
}
