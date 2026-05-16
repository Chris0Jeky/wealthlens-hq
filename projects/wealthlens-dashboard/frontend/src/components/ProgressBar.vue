<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    value: number
    max?: number
    label?: string
    showPercent?: boolean
    size?: 'sm' | 'md' | 'lg'
  }>(),
  { max: 100, showPercent: false, size: 'md' },
)

const percent = computed(() => {
  if (props.max <= 0) return 0
  return Math.min(100, Math.max(0, (props.value / props.max) * 100))
})

const heightClass: Record<string, string> = {
  sm: 'h-1',
  md: 'h-2',
  lg: 'h-4',
}
</script>

<template>
  <div class="w-full">
    <div
      v-if="label || showPercent"
      class="flex justify-between text-xs text-gray-600 dark:text-gray-400 mb-1"
    >
      <span v-if="label">{{ label }}</span>
      <span v-if="showPercent">{{ Math.round(percent) }}%</span>
    </div>
    <div
      role="progressbar"
      :aria-valuenow="value"
      :aria-valuemin="0"
      :aria-valuemax="max"
      :aria-label="label ?? 'Progress'"
      class="w-full rounded-full bg-gray-200 dark:bg-gray-700 overflow-hidden"
      :class="heightClass[size]"
    >
      <div
        class="h-full rounded-full bg-blue-600 dark:bg-blue-500 transition-all duration-300"
        :style="{ width: `${percent}%` }"
      />
    </div>
  </div>
</template>
