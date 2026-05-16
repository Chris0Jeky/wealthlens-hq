<script setup lang="ts">
withDefaults(
  defineProps<{
    minWidth?: string
    gap?: string
  }>(),
  { minWidth: '280px', gap: '1.5rem' },
)
</script>

<template>
  <div
    class="grid"
    :style="{
      gridTemplateColumns: `repeat(auto-fill, minmax(${minWidth}, 1fr))`,
      gap,
    }"
  >
    <slot />
  </div>
</template>
