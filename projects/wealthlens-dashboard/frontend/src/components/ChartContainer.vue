<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
  loading?: boolean
  error?: string | null
}>()
</script>

<template>
  <section
    class="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4 sm:p-6"
    :aria-label="title"
    aria-live="polite"
  >
    <header class="mb-4">
      <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
        {{ title }}
      </h2>
      <p v-if="subtitle" class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        {{ subtitle }}
      </p>
    </header>

    <div v-if="error" role="alert" class="rounded-md bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 p-4 text-sm text-red-700 dark:text-red-300">
      {{ error }}
    </div>

    <div v-else-if="loading" class="flex items-center justify-center py-12" aria-busy="true">
      <div class="motion-safe:animate-spin h-8 w-8 rounded-full border-4 border-gray-200 dark:border-gray-600 border-t-blue-600 dark:border-t-blue-400" role="status" aria-label="Loading chart" />
    </div>

    <div v-else>
      <slot />
    </div>

    <footer v-if="$slots.footer" class="mt-4 pt-3 border-t border-gray-100 dark:border-gray-700">
      <slot name="footer" />
    </footer>
  </section>
</template>
