<script setup lang="ts">
defineProps<{
  name: string;
  description: string;
}>();
</script>

<template>
  <div class="rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
    <h3 class="text-lg font-semibold mb-2">{{ name }}</h3>
    <p class="text-sm text-gray-600 mb-3">{{ description }}</p>
    <router-link
      :to="`/charts/${name}`"
      class="inline-flex items-center text-sm font-medium text-blue-600 hover:text-blue-800"
    >
      View Chart &rarr;
    </router-link>
  </div>
</template>
