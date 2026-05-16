<script setup lang="ts">
defineProps<{
  target?: string
}>()
</script>

<template>
  <a
    :href="target ?? '#main-content'"
    class="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-50 focus:px-4 focus:py-2 focus:bg-blue-600 focus:text-white focus:rounded focus:shadow-lg focus:outline-none"
  >
    Skip to main content
  </a>
</template>
