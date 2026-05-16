<script setup lang="ts">
import { computed, useId } from 'vue'

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

const uid = useId()

const percent = computed(() => {
  if (props.max <= 0) return 0
  return Math.min(100, Math.max(0, (props.value / props.max) * 100))
})

const clampedValue = computed(() => {
  if (props.max <= 0) return 0
  return Math.min(props.max, Math.max(0, props.value))
})

const heightClass: Record<'sm' | 'md' | 'lg', string> = {
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
      <span v-if="label" :id="uid">{{ label }}</span>
      <span v-if="showPercent">{{ Math.round(percent) }}%</span>
    </div>
    <div
      role="progressbar"
      :aria-valuenow="clampedValue"
      :aria-valuemin="0"
      :aria-valuemax="max"
      :aria-labelledby="label ? uid : undefined"
      :aria-label="label ? undefined : 'Progress'"
      class="w-full rounded-full bg-gray-200 dark:bg-gray-700 overflow-hidden"
      :class="heightClass[size] ?? heightClass['md']"
    >
      <div
        class="h-full rounded-full bg-blue-600 dark:bg-blue-500 transition-all duration-300"
        :style="{ width: `${percent}%` }"
      />
    </div>
  </div>
</template>
