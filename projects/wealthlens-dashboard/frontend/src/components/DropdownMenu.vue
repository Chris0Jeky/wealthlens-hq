<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

export interface DropdownItem {
  id: string
  label: string
  disabled?: boolean
}

const props = defineProps<{
  items: DropdownItem[]
  label: string
}>()

const emit = defineEmits<{ select: [id: string] }>()

const open = ref(false)
const triggerRef = ref<HTMLButtonElement | null>(null)
const menuRef = ref<HTMLElement | null>(null)

function toggle() {
  open.value = !open.value
}

function close() {
  open.value = false
}

function selectItem(item: DropdownItem) {
  if (item.disabled) return
  emit('select', item.id)
  close()
  triggerRef.value?.focus()
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    close()
    triggerRef.value?.focus()
  }
}

function handleClickOutside(event: MouseEvent) {
  if (!open.value) return
  const target = event.target as Node
  if (
    menuRef.value &&
    !menuRef.value.contains(target) &&
    triggerRef.value &&
    !triggerRef.value.contains(target)
  ) {
    close()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div class="relative inline-block" @keydown="handleKeydown">
    <button
      ref="triggerRef"
      type="button"
      :aria-expanded="open"
      aria-haspopup="true"
      class="inline-flex items-center gap-1 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
      @click="toggle"
    >
      {{ label }}
      <span aria-hidden="true" class="ml-1">&#9662;</span>
    </button>
    <ul
      v-if="open"
      ref="menuRef"
      role="menu"
      class="absolute left-0 z-10 mt-1 w-48 origin-top-left rounded-md bg-white dark:bg-gray-800 shadow-lg ring-1 ring-black/5 dark:ring-white/10 focus:outline-none"
    >
      <li
        v-for="item in items"
        :key="item.id"
        role="menuitem"
        :aria-disabled="item.disabled ? 'true' : undefined"
        :tabindex="item.disabled ? -1 : 0"
        class="block w-full cursor-pointer px-4 py-2 text-left text-sm"
        :class="item.disabled
          ? 'text-gray-400 dark:text-gray-500 cursor-not-allowed'
          : 'text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700'"
        @click="selectItem(item)"
        @keydown.enter="selectItem(item)"
        @keydown.space.prevent="selectItem(item)"
      >
        {{ item.label }}
      </li>
    </ul>
  </div>
</template>
