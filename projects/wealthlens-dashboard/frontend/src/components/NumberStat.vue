<script setup lang="ts">
defineProps<{
  value: string
  label: string
  description?: string
}>()
</script>

<template>
  <div class="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 p-6 text-center">
    <p class="text-3xl font-bold text-gray-900 dark:text-gray-100" aria-hidden="true">
      {{ value }}
    </p>
    <p class="mt-1 text-sm font-medium text-gray-600 dark:text-gray-400">
      {{ label }}
    </p>
    <p v-if="description" class="mt-2 text-xs text-gray-500 dark:text-gray-500">
      {{ description }}
    </p>
    <span class="sr-only">{{ label }}: {{ value }}</span>
  </div>
</template>
