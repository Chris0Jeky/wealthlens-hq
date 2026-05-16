<script setup lang="ts">
defineProps<{
  title: string
  description?: string
}>()
</script>

<template>
  <header class="mb-8">
    <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100 sm:text-3xl">
      {{ title }}
    </h1>
    <p v-if="description" class="mt-2 text-sm text-gray-600 dark:text-gray-400 max-w-2xl">
      {{ description }}
    </p>
    <div v-if="$slots.actions" class="mt-4 flex flex-wrap gap-3">
      <slot name="actions" />
    </div>
  </header>
</template>
