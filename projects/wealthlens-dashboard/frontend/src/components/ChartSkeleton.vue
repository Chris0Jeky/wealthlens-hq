<script setup lang="ts">
/**
 * ChartSkeleton — Reusable shimmer/pulse skeleton that mimics a chart layout
 * during data loading. Provides better perceived performance than a plain text
 * "Loading..." message.
 *
 * Uses deterministic bar heights to avoid layout shifts on re-render.
 * Accessible: role="status" + aria-label + sr-only text.
 */
const barHeights = [35, 55, 40, 65, 50, 75, 45, 60, 30, 70, 55, 45]
</script>

<template>
  <div class="animate-pulse" role="status" aria-label="Loading chart">
    <!-- Title skeleton -->
    <div class="flex justify-center mb-6">
      <div class="h-5 bg-gray-200 rounded w-64"></div>
    </div>

    <!-- Chart area skeleton -->
    <div class="relative" style="height: 480px">
      <!-- Y-axis labels -->
      <div class="absolute left-0 top-1/2 -translate-y-1/2">
        <div class="h-3 bg-gray-200 rounded w-8 mb-2"></div>
        <div class="h-3 bg-gray-200 rounded w-8 mb-2"></div>
        <div class="h-3 bg-gray-200 rounded w-8 mb-2"></div>
        <div class="h-3 bg-gray-200 rounded w-8"></div>
      </div>

      <!-- Chart body -->
      <div class="ml-12 mr-4 h-full flex items-end space-x-1">
        <div
          v-for="(h, i) in barHeights"
          :key="i"
          class="flex-1 bg-gray-200 rounded-t"
          :style="{ height: `${h}%` }"
        ></div>
      </div>

      <!-- X-axis labels -->
      <div class="ml-12 mr-4 flex justify-between mt-2">
        <div class="h-3 bg-gray-200 rounded w-8"></div>
        <div class="h-3 bg-gray-200 rounded w-8"></div>
        <div class="h-3 bg-gray-200 rounded w-8"></div>
        <div class="h-3 bg-gray-200 rounded w-8"></div>
      </div>
    </div>

    <!-- Legend skeleton -->
    <div class="flex justify-center space-x-6 mt-4">
      <div class="flex items-center space-x-2">
        <div class="h-3 w-3 bg-gray-200 rounded-full"></div>
        <div class="h-3 bg-gray-200 rounded w-16"></div>
      </div>
      <div class="flex items-center space-x-2">
        <div class="h-3 w-3 bg-gray-200 rounded-full"></div>
        <div class="h-3 bg-gray-200 rounded w-16"></div>
      </div>
    </div>

    <span class="sr-only">Loading chart data</span>
  </div>
</template>
