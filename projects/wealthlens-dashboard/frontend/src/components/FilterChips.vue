<script setup lang="ts">
export interface ChipOption {
  id: string
  label: string
}

const props = defineProps<{
  options: ChipOption[]
  selected: string[]
  label: string
}>()

const emit = defineEmits<{ 'update:selected': [ids: string[]] }>()

function toggle(id: string) {
  const current = new Set(props.selected)
  if (current.has(id)) {
    current.delete(id)
  } else {
    current.add(id)
  }
  emit('update:selected', [...current])
}

function isSelected(id: string): boolean {
  return props.selected.includes(id)
}
</script>

<template>
  <fieldset class="space-y-2">
    <legend class="text-sm font-medium text-gray-700 dark:text-gray-300">
      {{ label }}
    </legend>
    <div class="flex flex-wrap gap-2" role="group" :aria-label="label">
      <button
        v-for="option in options"
        :key="option.id"
        type="button"
        :aria-pressed="isSelected(option.id)"
        class="inline-flex items-center rounded-full px-3 py-1 text-xs font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1"
        :class="isSelected(option.id)
          ? 'bg-blue-600 text-white dark:bg-blue-500'
          : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'"
        @click="toggle(option.id)"
      >
        {{ option.label }}
      </button>
    </div>
  </fieldset>
</template>
