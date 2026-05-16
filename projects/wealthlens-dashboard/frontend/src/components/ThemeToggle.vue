<script setup lang="ts">
import { computed } from 'vue'
import { useTheme } from '@/composables/useTheme'
import type { ThemePreference } from '@/composables/useTheme'

const { preference, setPreference } = useTheme()

const options: { value: ThemePreference; label: string }[] = [
  { value: 'light', label: 'Light' },
  { value: 'dark', label: 'Dark' },
  { value: 'system', label: 'System' },
]

const nextOption = computed(() => {
  const idx = options.findIndex((o) => o.value === preference.value)
  return options[(idx + 1) % options.length]
})

function cycle() {
  setPreference(nextOption.value.value)
}

const currentLabel = computed(() => options.find((o) => o.value === preference.value)?.label)
</script>

<template>
  <button
    type="button"
    :aria-label="`Switch theme to ${nextOption.label} (current: ${currentLabel})`"
    class="inline-flex items-center gap-1.5 rounded-md px-2.5 py-1.5 text-sm font-medium text-gray-700 dark:text-gray-200 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1 transition-colors"
    @click="cycle"
  >
    <span v-if="preference === 'light'" aria-hidden="true">&#9728;</span>
    <span v-else-if="preference === 'dark'" aria-hidden="true">&#9790;</span>
    <span v-else aria-hidden="true">&#9881;</span>
    <span class="sr-only sm:not-sr-only">{{ currentLabel }}</span>
  </button>
</template>
