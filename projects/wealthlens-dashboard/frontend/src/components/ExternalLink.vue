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
    class="underline rounded focus:outline-none focus:ring-2 focus:ring-offset-1 text-[color:var(--wl-link)] hover:text-[color:var(--wl-link-hover)] focus:ring-[color:var(--wl-link-hover)]"
  >
    <slot />
    <span class="sr-only"> (opens in new tab)</span>
  </a>
</template>
