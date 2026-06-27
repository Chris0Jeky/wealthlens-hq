<script setup lang="ts">
withDefaults(
  defineProps<{
    size?: "sm" | "md" | "lg"
    label?: string
  }>(),
  { size: "md", label: "Loading" },
)

const sizeClasses = {
  sm: "h-4 w-4 border-2",
  md: "h-8 w-8 border-3",
  lg: "h-12 w-12 border-4",
}
</script>

<template>
  <div class="flex items-center justify-center" role="status">
    <div
      :class="[
        'motion-safe:animate-spin rounded-full border-gray-200 dark:border-gray-700 border-t-blue-600 dark:border-t-blue-400',
        sizeClasses[size],
      ]"
      aria-hidden="true"
    />
    <span class="sr-only">{{ label }}</span>
  </div>
</template>
