<script setup lang="ts">
withDefaults(
  defineProps<{
    title?: string
    message?: string
    icon?: string
  }>(),
  {
    title: 'No data available',
    message: 'There is nothing to display here yet.',
    icon: '&#128202;',
  },
)
</script>

<template>
  <div class="flex flex-col items-center justify-center py-16 px-4 text-center">
    <span class="text-4xl mb-4" aria-hidden="true" v-html="icon" />
    <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
      {{ title }}
    </h3>
    <p class="text-sm text-gray-500 dark:text-gray-400 max-w-sm">
      {{ message }}
    </p>
    <div v-if="$slots.action" class="mt-6">
      <slot name="action" />
    </div>
  </div>
</template>
