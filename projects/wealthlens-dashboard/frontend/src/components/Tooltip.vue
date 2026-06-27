<script setup lang="ts">
import { ref } from "vue"

withDefaults(
  defineProps<{
    text: string
    position?: "top" | "bottom"
  }>(),
  { position: "top" },
)

const visible = ref(false)
</script>

<template>
  <span
    class="relative inline-block"
    @mouseenter="visible = true"
    @mouseleave="visible = false"
    @focusin="visible = true"
    @focusout="visible = false"
  >
    <slot />
    <span
      v-if="visible"
      role="tooltip"
      :class="[
        'absolute left-1/2 -translate-x-1/2 z-40 whitespace-nowrap rounded bg-gray-900 dark:bg-gray-100 px-2.5 py-1.5 text-xs font-medium text-white dark:text-gray-900 shadow-lg pointer-events-none',
        position === 'top' ? 'bottom-full mb-2' : 'top-full mt-2',
      ]"
    >
      {{ text }}
    </span>
  </span>
</template>
