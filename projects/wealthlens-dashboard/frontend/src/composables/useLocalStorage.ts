import { ref, watch, type Ref } from "vue"
import { getStorageItem, setStorageItem } from "@/utils/browserStorage"

export function useLocalStorage<T>(key: string, defaultValue: T): Ref<T> {
  const stored = read(key)
  const data = ref<T>((stored !== null ? stored : defaultValue) as T) as Ref<T>

  watch(
    data,
    (val) => {
      write(key, val)
    },
    { deep: true },
  )

  return data
}

function read(key: string): unknown | null {
  try {
    const raw = getStorageItem(key)
    if (raw === null) return null
    return JSON.parse(raw)
  } catch {
    return null
  }
}

function write(key: string, value: unknown): void {
  try {
    setStorageItem(key, JSON.stringify(value))
  } catch {
    // QuotaExceededError or SecurityError — fail silently
  }
}
