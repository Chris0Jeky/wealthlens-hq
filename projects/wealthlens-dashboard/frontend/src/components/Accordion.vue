<script setup lang="ts">
import { ref, useId } from "vue"

defineProps<{
  title: string
  defaultOpen?: boolean
}>()

const headingId = useId()
const panelId = useId()
const open = ref(false)

function toggle() {
  open.value = !open.value
}
</script>

<template>
  <div class="border-b border-gray-200 dark:border-gray-700">
    <h3>
      <button
        :id="headingId"
        type="button"
        :aria-expanded="open"
        :aria-controls="panelId"
        class="flex w-full items-center justify-between py-4 text-left text-sm font-medium text-gray-900 dark:text-gray-100 hover:text-blue-600 dark:hover:text-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1 rounded"
        @click="toggle"
      >
        <span>{{ title }}</span>
        <span
          aria-hidden="true"
          class="ml-2 shrink-0 transition-transform duration-200"
          :class="{ 'rotate-180': open }"
          >&#9660;</span
        >
      </button>
    </h3>
    <div
      v-show="open"
      :id="panelId"
      role="region"
      :aria-labelledby="headingId"
      class="pb-4 text-sm text-gray-600 dark:text-gray-400"
    >
      <slot />
    </div>
  </div>
</template>
