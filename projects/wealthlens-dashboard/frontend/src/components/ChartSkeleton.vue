<script setup lang="ts">
defineProps<{
  /** Number of skeleton bar elements to show */
  bars?: number
}>()
</script>

<template>
  <div
    class="w-full animate-pulse"
    role="status"
    aria-label="Loading chart"
  >
    <div class="h-6 w-48 bg-gray-200 rounded mb-4" />
    <div class="h-4 w-64 bg-gray-200 rounded mb-6" />
    <div class="flex items-end gap-2 h-64">
      <div
        v-for="i in (bars ?? 7)"
        :key="i"
        class="flex-1 bg-gray-200 rounded-t"
        :style="{ height: `${20 + ((i * 37) % 80)}%` }"
      />
    </div>
    <div class="h-3 w-56 bg-gray-200 rounded mt-4 mx-auto" />
    <span class="sr-only">Loading chart data…</span>
  </div>
</template>
