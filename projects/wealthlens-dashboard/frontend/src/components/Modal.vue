<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'

defineProps<{
  title: string
  open: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

function onKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') emit('close')
}

onMounted(() => {
  document.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
})
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-50 flex items-center justify-center"
      role="dialog"
      aria-modal="true"
      :aria-label="title"
    >
      <div
        class="absolute inset-0 bg-black/50 dark:bg-black/70"
        aria-hidden="true"
        @click="emit('close')"
      />
      <div class="relative z-10 w-full max-w-lg mx-4 rounded-xl bg-white dark:bg-gray-900 shadow-xl">
        <header class="flex items-center justify-between border-b border-gray-200 dark:border-gray-700 px-6 py-4">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">{{ title }}</h2>
          <button
            type="button"
            aria-label="Close dialog"
            class="rounded p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
            @click="emit('close')"
          >
            &times;
          </button>
        </header>
        <div class="px-6 py-4">
          <slot />
        </div>
      </div>
    </div>
  </Teleport>
</template>
