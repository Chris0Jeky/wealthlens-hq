<script setup lang="ts">
defineProps<{
  title?: string
  message: string
  /** Show retry button */
  retryable?: boolean
}>()

defineEmits<{
  retry: []
}>()
</script>

<template>
  <div class="w-full text-center py-10" aria-live="assertive" aria-atomic="true">
    <p class="text-red-600 font-medium mb-2">{{ title ?? "Failed to load data" }}</p>
    <p class="text-sm text-gray-600 mb-4">{{ message }}</p>
    <button
      v-if="retryable"
      type="button"
      class="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
      @click="$emit('retry')"
    >
      Try again
    </button>
  </div>
</template>
