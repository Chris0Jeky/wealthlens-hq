import { ref, onMounted, onUnmounted } from 'vue'

export type ColorScheme = 'light' | 'dark'

export function useColorScheme(): { scheme: ReturnType<typeof ref<ColorScheme>> } {
  const scheme = ref<ColorScheme>('light')
  let mql: MediaQueryList | null = null

  function update() {
    scheme.value = mql?.matches ? 'dark' : 'light'
  }

  onMounted(() => {
    if (typeof window === 'undefined') return
    mql = window.matchMedia('(prefers-color-scheme: dark)')
    update()
    mql.addEventListener('change', update)
  })

  onUnmounted(() => {
    mql?.removeEventListener('change', update)
  })

  return { scheme }
}
