<script setup lang="ts">
export type BadgeVariant = 'default' | 'success' | 'warning' | 'error' | 'info'

withDefaults(
  defineProps<{
    variant?: BadgeVariant
    size?: 'sm' | 'md'
  }>(),
  { variant: 'default', size: 'md' },
)

const variantClasses: Record<BadgeVariant, string> = {
  default: 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300',
  success: 'bg-green-100 dark:bg-green-900/40 text-green-800 dark:text-green-300',
  warning: 'bg-yellow-100 dark:bg-yellow-900/40 text-yellow-800 dark:text-yellow-300',
  error: 'bg-red-100 dark:bg-red-900/40 text-red-800 dark:text-red-300',
  info: 'bg-blue-100 dark:bg-blue-900/40 text-blue-800 dark:text-blue-300',
}

const sizeClasses: Record<string, string> = {
  sm: 'px-1.5 py-0.5 text-[10px]',
  md: 'px-2 py-0.5 text-xs',
}
</script>

<template>
  <span
    class="inline-flex items-center font-medium rounded-full"
    :class="[variantClasses[variant!], sizeClasses[size!]]"
  >
    <slot />
  </span>
</template>
