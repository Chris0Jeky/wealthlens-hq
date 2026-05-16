<script setup lang="ts">
import { ref, watch, nextTick, onUnmounted, useId } from 'vue'

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

const triggerId = useId()
const open = ref(false)
const focusedIndex = ref(-1)
const triggerRef = ref<HTMLButtonElement | null>(null)
const menuRef = ref<HTMLElement | null>(null)

function getEnabledIndices(): number[] {
  return props.items.reduce<number[]>((acc, item, i) => {
    if (!item.disabled) acc.push(i)
    return acc
  }, [])
}

function focusItem(index: number) {
  focusedIndex.value = index
  const els = menuRef.value?.querySelectorAll<HTMLElement>('[role="menuitem"]')
  els?.[index]?.focus()
}

async function openMenu() {
  open.value = true
  await nextTick()
  const enabled = getEnabledIndices()
  if (enabled.length > 0) focusItem(enabled[0])
}

function close() {
  open.value = false
  focusedIndex.value = -1
}

async function toggle() {
  if (open.value) {
    close()
  } else {
    await openMenu()
  }
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
    return
  }

  if (!open.value) return

  const enabled = getEnabledIndices()
  if (!enabled.length) return

  if (event.key === 'ArrowDown') {
    event.preventDefault()
    const currentPos = enabled.indexOf(focusedIndex.value)
    const next = currentPos < enabled.length - 1 ? enabled[currentPos + 1] : enabled[0]
    focusItem(next)
  } else if (event.key === 'ArrowUp') {
    event.preventDefault()
    const currentPos = enabled.indexOf(focusedIndex.value)
    const prev = currentPos > 0 ? enabled[currentPos - 1] : enabled[enabled.length - 1]
    focusItem(prev)
  } else if (event.key === 'Home') {
    event.preventDefault()
    focusItem(enabled[0])
  } else if (event.key === 'End') {
    event.preventDefault()
    focusItem(enabled[enabled.length - 1])
  } else if (event.key === 'Tab') {
    close()
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

watch(open, (isOpen) => {
  if (isOpen) {
    document.addEventListener('mousedown', handleClickOutside)
  } else {
    document.removeEventListener('mousedown', handleClickOutside)
  }
})

onUnmounted(() => {
  document.removeEventListener('mousedown', handleClickOutside)
})
</script>

<template>
  <div class="relative inline-block" @keydown="handleKeydown">
    <button
      :id="triggerId"
      ref="triggerRef"
      type="button"
      :aria-expanded="open"
      aria-haspopup="menu"
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
      :aria-labelledby="triggerId"
      class="absolute left-0 z-10 mt-1 w-48 origin-top-left rounded-md bg-white dark:bg-gray-800 shadow-lg ring-1 ring-black/5 dark:ring-white/10 focus:outline-none"
    >
      <li
        v-for="(item, idx) in items"
        :key="item.id"
        role="menuitem"
        :aria-disabled="item.disabled ? 'true' : undefined"
        :tabindex="item.disabled ? -1 : 0"
        class="block w-full cursor-pointer px-4 py-2 text-left text-sm outline-none"
        :class="[
          item.disabled
            ? 'text-gray-400 dark:text-gray-500 cursor-not-allowed'
            : 'text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 focus:bg-gray-100 dark:focus:bg-gray-700',
        ]"
        @click="selectItem(item)"
        @keydown.enter="selectItem(item)"
        @keydown.space.prevent="selectItem(item)"
      >
        {{ item.label }}
      </li>
    </ul>
  </div>
</template>
