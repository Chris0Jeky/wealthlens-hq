<script setup lang="ts">
defineProps<{
  width?: string
  height?: string
  rounded?: boolean
  lines?: number
}>()
</script>

<template>
  <div
    v-if="!lines || lines <= 1"
    role="status"
    aria-label="Loading"
    class="animate-pulse bg-gray-200 dark:bg-gray-700"
    :class="{ 'rounded-full': rounded, 'rounded': !rounded }"
    :style="{ width: width ?? '100%', height: height ?? '1rem' }"
  />
  <div v-else role="status" aria-label="Loading" class="space-y-2">
    <div
      v-for="i in lines"
      :key="i"
      class="animate-pulse bg-gray-200 dark:bg-gray-700 rounded"
      :style="{
        width: i === lines ? '75%' : (width ?? '100%'),
        height: height ?? '1rem',
      }"
    />
  </div>
</template>
