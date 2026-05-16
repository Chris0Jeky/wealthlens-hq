<script setup lang="ts">
import { ref, onUnmounted } from 'vue'

const props = defineProps<{
  text: string
  label?: string
}>()

const copied = ref(false)
const error = ref(false)
let timeout: ReturnType<typeof setTimeout> | null = null

function resetTimer() {
  if (timeout) {
    clearTimeout(timeout)
    timeout = null
  }
}

async function handleCopy() {
  if (typeof navigator === 'undefined' || !navigator.clipboard) return

  try {
    await navigator.clipboard.writeText(props.text)
    copied.value = true
    error.value = false
    resetTimer()
    timeout = setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch {
    copied.value = false
    error.value = true
    resetTimer()
    timeout = setTimeout(() => {
      error.value = false
    }, 2000)
  }
}

onUnmounted(resetTimer)
</script>

<template>
  <button
    type="button"
    :aria-label="error ? 'Copy failed — try again' : copied ? (label ? label + ' — copied' : 'Copied to clipboard') : (label ?? 'Copy to clipboard')"
    class="inline-flex items-center gap-1 rounded px-2 py-1 text-xs font-medium text-gray-600 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
    @click="handleCopy"
  >
    <span v-if="copied" aria-hidden="true">&#10003;</span>
    <span v-else aria-hidden="true">&#128203;</span>
    <span class="sr-only sm:not-sr-only">{{ copied ? 'Copied!' : 'Copy' }}</span>
  </button>
  <span role="status" aria-live="polite" class="sr-only">
    {{ copied ? 'Copied!' : error ? 'Copy failed' : '' }}
  </span>
</template>
