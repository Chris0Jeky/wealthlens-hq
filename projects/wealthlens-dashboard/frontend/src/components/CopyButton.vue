<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  text: string
  label?: string
}>()

const copied = ref(false)
let timeout: ReturnType<typeof setTimeout> | null = null

async function handleCopy() {
  if (typeof navigator === 'undefined' || !navigator.clipboard) return

  try {
    await navigator.clipboard.writeText(props.text)
    copied.value = true
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch {
    copied.value = false
  }
}
</script>

<template>
  <button
    type="button"
    :aria-label="label ?? 'Copy to clipboard'"
    class="inline-flex items-center gap-1 rounded px-2 py-1 text-xs font-medium text-gray-600 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
    @click="handleCopy"
  >
    <span v-if="copied" aria-hidden="true">&#10003;</span>
    <span v-else aria-hidden="true">&#128203;</span>
    <span class="sr-only sm:not-sr-only">{{ copied ? 'Copied!' : 'Copy' }}</span>
  </button>
</template>
