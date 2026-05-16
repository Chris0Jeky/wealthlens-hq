<script setup lang="ts">
import { computed } from 'vue'

export interface Tab {
  id: string
  label: string
}

const props = defineProps<{
  tabs: Tab[]
  activeId: string
}>()

const emit = defineEmits<{
  (e: 'update:activeId', id: string): void
}>()

const activeTab = computed(() => props.tabs.find((t) => t.id === props.activeId) ?? props.tabs[0])
</script>

<template>
  <div>
    <div role="tablist" aria-label="Content tabs" class="flex border-b border-gray-200 dark:border-gray-700">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        type="button"
        role="tab"
        :id="`tab-${tab.id}`"
        :aria-selected="tab.id === activeTab?.id"
        :aria-controls="`panel-${tab.id}`"
        :tabindex="tab.id === activeTab?.id ? 0 : -1"
        :class="[
          'px-4 py-2.5 text-sm font-medium border-b-2 -mb-px transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-inset',
          tab.id === activeTab?.id
            ? 'border-blue-600 text-blue-600 dark:border-blue-400 dark:text-blue-400'
            : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300',
        ]"
        @click="emit('update:activeId', tab.id)"
      >
        {{ tab.label }}
      </button>
    </div>
    <div
      v-for="tab in tabs"
      :key="tab.id"
      :id="`panel-${tab.id}`"
      role="tabpanel"
      :aria-labelledby="`tab-${tab.id}`"
      :hidden="tab.id !== activeTab?.id"
      class="pt-4"
    >
      <slot v-if="tab.id === activeTab?.id" :name="tab.id" />
    </div>
  </div>
</template>
