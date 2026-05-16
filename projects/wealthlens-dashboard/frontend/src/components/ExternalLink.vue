<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  href: string
}>()

const safeHref = computed(() => {
  if (/^https?:\/\//i.test(props.href)) return props.href
  return '#'
})
</script>

<template>
  <a
    :href="safeHref"
    target="_blank"
    rel="noopener noreferrer"
    class="text-blue-600 hover:text-blue-800 underline focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1 rounded"
  >
    <slot />
    <span class="sr-only"> (opens in new tab)</span>
  </a>
</template>
