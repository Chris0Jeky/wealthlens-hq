<script setup lang="ts">
import { ref } from 'vue'

export type AlertVariant = 'info' | 'warning' | 'error' | 'success'

const props = withDefaults(
  defineProps<{
    variant?: AlertVariant
    dismissible?: boolean
  }>(),
  { variant: 'info', dismissible: false },
)

defineEmits<{ dismiss: [] }>()

const dismissed = ref(false)

const variantClasses: Record<AlertVariant, string> = {
  info: 'bg-blue-50 dark:bg-blue-900/30 border-blue-300 dark:border-blue-700 text-blue-800 dark:text-blue-200',
  warning: 'bg-yellow-50 dark:bg-yellow-900/30 border-yellow-300 dark:border-yellow-700 text-yellow-800 dark:text-yellow-200',
  error: 'bg-red-50 dark:bg-red-900/30 border-red-300 dark:border-red-700 text-red-800 dark:text-red-200',
  success: 'bg-green-50 dark:bg-green-900/30 border-green-300 dark:border-green-700 text-green-800 dark:text-green-200',
}

const iconMap: Record<AlertVariant, string> = {
  info: 'ℹ️',
  warning: '⚠️',
  error: '❌',
  success: '✅',
}
</script>

<template>
  <div
    v-if="!dismissed"
    role="alert"
    class="flex items-start gap-3 rounded-md border px-4 py-3 text-sm"
    :class="variantClasses[props.variant]"
  >
    <span aria-hidden="true" class="shrink-0 text-base">{{ iconMap[props.variant] }}</span>
    <div class="flex-1 min-w-0">
      <slot />
    </div>
    <button
      v-if="dismissible"
      type="button"
      aria-label="Dismiss alert"
      class="shrink-0 ml-2 opacity-70 hover:opacity-100 transition-opacity"
      @click="dismissed = true; $emit('dismiss')"
    >
      &#10005;
    </button>
  </div>
</template>
