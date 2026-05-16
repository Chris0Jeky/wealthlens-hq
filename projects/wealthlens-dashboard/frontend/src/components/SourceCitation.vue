<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  source: string
  sourceUrl: string
  accessDate: string
}

const props = defineProps<Props>()

const safeUrl = computed(() => {
  if (/^https?:\/\//i.test(props.sourceUrl)) return props.sourceUrl
  return '#'
})
</script>

<template>
  <footer class="mt-4 pt-3 border-t border-[var(--wl-rule)] text-xs text-[var(--wl-ink-muted)]">
    <p>
      Source:
      <a
        :href="safeUrl"
        target="_blank"
        rel="noopener noreferrer"
        class="underline hover:text-[var(--wl-ink)] focus:outline-none focus:ring-2 focus:ring-[var(--wl-red)] rounded"
      >{{ source }}<span class="sr-only"> (opens in new tab)</span></a>.
      Accessed {{ accessDate }}.
    </p>
  </footer>
</template>
