import { ref } from 'vue'

export function useClipboard() {
  const copied = ref(false)
  let timeout: ReturnType<typeof setTimeout> | null = null

  async function copy(text: string): Promise<boolean> {
    if (typeof navigator === 'undefined' || !navigator.clipboard) return false

    try {
      await navigator.clipboard.writeText(text)
      copied.value = true
      if (timeout) clearTimeout(timeout)
      timeout = setTimeout(() => {
        copied.value = false
      }, 2000)
      return true
    } catch {
      copied.value = false
      return false
    }
  }

  return { copied, copy }
}
