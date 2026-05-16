<script setup lang="ts">
interface Props {
  source: string
  sourceUrl: string
  accessDate: string
}

defineProps<Props>()
</script>

<template>
  <p class="text-sm text-gray-500 mt-4 text-center">
    Source:
    <a
      :href="sourceUrl"
      target="_blank"
      rel="noopener"
      class="underline hover:text-gray-700"
    >{{ source }}</a>,
    accessed {{ accessDate }}
  </p>
</template>
