<script setup lang="ts">
/**
 * LoadingSkeleton — animated placeholder shown while chart/card data loads.
 * Replaces the plain "Loading chart data..." text with a pulsing skeleton.
 */
withDefaults(
  defineProps<{
    /** Visual layout: "chart" renders tall bars + axes, "card" renders compact lines. */
    variant?: "chart" | "card"
  }>(),
  { variant: "chart" },
)
</script>

<template>
  <div role="status" aria-label="Loading content" class="animate-pulse">
    <!-- Screen-reader-only text -->
    <span class="sr-only">Loading...</span>

    <!-- Chart variant: mimics a bar chart with axis lines -->
    <div v-if="variant === 'chart'" class="space-y-3">
      <!-- Simulated bars -->
      <div class="flex items-end space-x-2 h-40">
        <div class="bg-gray-200 rounded w-1/6 h-3/4"></div>
        <div class="bg-gray-200 rounded w-1/6 h-full"></div>
        <div class="bg-gray-200 rounded w-1/6 h-1/2"></div>
        <div class="bg-gray-200 rounded w-1/6 h-5/6"></div>
        <div class="bg-gray-200 rounded w-1/6 h-2/3"></div>
        <div class="bg-gray-200 rounded w-1/6 h-3/5"></div>
      </div>
      <!-- X-axis line -->
      <div class="bg-gray-200 rounded h-1 w-full"></div>
      <!-- Axis labels -->
      <div class="flex justify-between">
        <div class="bg-gray-200 rounded h-3 w-10"></div>
        <div class="bg-gray-200 rounded h-3 w-10"></div>
        <div class="bg-gray-200 rounded h-3 w-10"></div>
        <div class="bg-gray-200 rounded h-3 w-10"></div>
      </div>
    </div>

    <!-- Card variant: mimics a content card with text lines -->
    <div v-else class="space-y-3">
      <!-- Title line -->
      <div class="bg-gray-200 rounded h-5 w-2/3"></div>
      <!-- Body lines -->
      <div class="bg-gray-200 rounded h-4 w-full"></div>
      <div class="bg-gray-200 rounded h-4 w-5/6"></div>
      <div class="bg-gray-200 rounded h-4 w-4/6"></div>
    </div>
  </div>
</template>
