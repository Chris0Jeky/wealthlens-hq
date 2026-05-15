<script setup lang="ts">
import { useRouter } from "vue-router";

/** Dataset names that have a chart implementation. */
const SUPPORTED_CHARTS = new Set(["wealth-shares", "housing-affordability", "cgt-concentration", "wealth-by-decile"]);

const props = defineProps<{
  name: string;
  description: string;
  /** Override chart availability. When omitted, checks SUPPORTED_CHARTS. */
  hasChart?: boolean;
}>();

const chartAvailable =
  props.hasChart !== undefined ? props.hasChart : SUPPORTED_CHARTS.has(props.name);

const router = useRouter();

function onEnter() {
  if (chartAvailable) {
    router.push(`/charts/${props.name}`);
  }
}
</script>

<template>
  <div
    role="article"
    tabindex="0"
    :aria-label="`Dataset: ${name} — ${description}`"
    class="rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow focus:outline-none focus:ring-2 focus:ring-blue-500"
    @keydown.enter="onEnter"
  >
    <h3 class="text-lg font-semibold mb-2">{{ name }}</h3>
    <p class="text-sm text-gray-600 mb-3">{{ description }}</p>
    <router-link
      v-if="chartAvailable"
      :to="`/charts/${name}`"
      class="inline-flex items-center text-sm font-medium text-blue-600 hover:text-blue-800"
    >
      View Chart &rarr;
    </router-link>
    <span v-else class="text-sm text-gray-400 italic">Chart coming soon</span>
  </div>
</template>
