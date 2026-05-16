<script setup lang="ts">
/** Dataset names that have a chart implementation. */
const SUPPORTED_CHARTS = new Set(["wealth-shares", "housing-affordability", "cgt-concentration"]);

const props = defineProps<{
  name: string;
  description: string;
  /** Override chart availability. When omitted, checks SUPPORTED_CHARTS. */
  hasChart?: boolean;
}>();

const chartAvailable =
  props.hasChart !== undefined ? props.hasChart : SUPPORTED_CHARTS.has(props.name);
</script>

<template>
  <div class="rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
    <h3 class="text-lg font-semibold mb-2">{{ name }}</h3>
    <p class="text-sm text-gray-600 mb-3">{{ description }}</p>
    <router-link
      v-if="chartAvailable"
      :to="`/charts/${name}`"
      class="inline-flex items-center text-sm font-medium text-blue-600 hover:text-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded"
    >
      View Chart &rarr;
    </router-link>
    <span v-else class="text-sm text-gray-400 italic">Chart coming soon</span>
  </div>
</template>
