import { onMounted, onUnmounted } from 'vue'

export interface ShortcutOptions {
  ctrl?: boolean
  shift?: boolean
  alt?: boolean
  prevent?: boolean
}

export function useKeyboardShortcut(
  key: string,
  handler: (event: KeyboardEvent) => void,
  options: ShortcutOptions = {},
): void {
  const { ctrl = false, shift = false, alt = false, prevent = true } = options

  function onKeydown(event: KeyboardEvent) {
    if (event.key !== key) return
    if (ctrl !== (event.ctrlKey || event.metaKey)) return
    if (shift !== event.shiftKey) return
    if (alt !== event.altKey) return

    if (prevent) event.preventDefault()
    handler(event)
  }

  onMounted(() => {
    document.addEventListener('keydown', onKeydown)
  })

  onUnmounted(() => {
    document.removeEventListener('keydown', onKeydown)
  })
}
