<script setup lang="ts">
export type StatusVariant = "online" | "offline" | "warning" | "idle"

const props = withDefaults(
  defineProps<{
    status: StatusVariant
    label?: string
    pulse?: boolean
  }>(),
  { pulse: false },
)

const colorClasses: Record<StatusVariant, string> = {
  online: "bg-green-500",
  offline: "bg-red-500",
  warning: "bg-yellow-500",
  idle: "bg-gray-400",
}
</script>

<template>
  <span class="inline-flex items-center gap-1.5">
    <span
      class="inline-block h-2.5 w-2.5 rounded-full"
      :class="[colorClasses[props.status], { 'motion-safe:animate-pulse': pulse }]"
      aria-hidden="true"
    />
    <span v-if="label" class="text-xs text-gray-600 dark:text-gray-400">{{ label }}</span>
    <span class="sr-only">{{ label ?? status }}</span>
  </span>
</template>
