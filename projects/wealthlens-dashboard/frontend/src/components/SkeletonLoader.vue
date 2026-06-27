<script setup lang="ts">
import { computed } from "vue"

const props = defineProps<{
  width?: string
  height?: string
  rounded?: boolean
  lines?: number
  label?: string
}>()

const lineCount = computed(() => Math.max(1, props.lines ?? 1))
</script>

<template>
  <div
    v-if="lineCount <= 1"
    role="status"
    :aria-label="label ?? 'Loading'"
    aria-busy="true"
    class="motion-safe:animate-pulse bg-gray-200 dark:bg-gray-700"
    :class="{ 'rounded-full': rounded, rounded: !rounded }"
    :style="{ width: width ?? '100%', height: height ?? '1rem' }"
  />
  <div v-else role="status" :aria-label="label ?? 'Loading'" aria-busy="true" class="space-y-2">
    <div
      v-for="i in lineCount"
      :key="i"
      class="motion-safe:animate-pulse bg-gray-200 dark:bg-gray-700"
      :class="{ 'rounded-full': rounded, rounded: !rounded }"
      :style="{
        width: i === lineCount ? '75%' : (width ?? '100%'),
        height: height ?? '1rem',
      }"
    />
  </div>
</template>
