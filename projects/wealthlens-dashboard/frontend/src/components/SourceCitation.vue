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
  <p class="text-sm text-gray-500 mt-4 text-center">
    Source:
    <a
      :href="safeUrl"
      target="_blank"
      rel="noopener noreferrer"
      class="underline hover:text-gray-700"
    >{{ source }}<span class="sr-only"> (opens in new tab)</span></a>,
    accessed {{ accessDate }}
  </p>
</template>
