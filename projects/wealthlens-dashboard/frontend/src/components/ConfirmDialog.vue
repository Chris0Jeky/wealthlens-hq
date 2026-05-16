<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'

const props = withDefaults(
  defineProps<{
    open: boolean
    title: string
    confirmLabel?: string
    cancelLabel?: string
    destructive?: boolean
  }>(),
  { confirmLabel: 'Confirm', cancelLabel: 'Cancel', destructive: false },
)

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()

const dialogRef = ref<HTMLDialogElement | null>(null)
const cancelBtnRef = ref<HTMLButtonElement | null>(null)

watch(
  () => props.open,
  async (isOpen) => {
    if (!dialogRef.value) return
    if (isOpen) {
      dialogRef.value.showModal()
      await nextTick()
      cancelBtnRef.value?.focus()
    } else {
      dialogRef.value.close()
    }
  },
)

function handleCancel() {
  emit('cancel')
}

function handleConfirm() {
  emit('confirm')
}

function handleNativeCancel(e: Event) {
  e.preventDefault()
  emit('cancel')
}
</script>

<template>
  <dialog
    ref="dialogRef"
    class="rounded-lg shadow-xl p-0 backdrop:bg-black/50 max-w-md w-full"
    @cancel="handleNativeCancel"
  >
    <div class="p-6">
      <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
        {{ title }}
      </h2>
      <div class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        <slot />
      </div>
      <div class="flex justify-end gap-3">
        <button
          ref="cancelBtnRef"
          type="button"
          class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-400 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
          @click="handleCancel"
        >
          {{ cancelLabel }}
        </button>
        <button
          type="button"
          class="px-4 py-2 text-sm font-medium text-white rounded focus:outline-none focus:ring-2 focus:ring-offset-2"
          :class="
            destructive
              ? 'bg-red-600 hover:bg-red-700 focus:ring-red-500'
              : 'bg-blue-600 hover:bg-blue-700 focus:ring-blue-500'
          "
          @click="handleConfirm"
        >
          {{ confirmLabel }}
        </button>
      </div>
    </div>
  </dialog>
</template>
