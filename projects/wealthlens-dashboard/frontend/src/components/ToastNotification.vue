<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue"

const props = withDefaults(
  defineProps<{
    message: string
    type?: "info" | "success" | "error"
    durationMs?: number
  }>(),
  { type: "info", durationMs: 5000 },
)

const emit = defineEmits<{
  (e: "dismiss"): void
}>()

const visible = ref(true)
let timer: ReturnType<typeof setTimeout> | null = null

function dismiss() {
  visible.value = false
  emit("dismiss")
}

onMounted(() => {
  if (props.durationMs > 0) {
    timer = setTimeout(dismiss, props.durationMs)
  }
})

onUnmounted(() => {
  if (timer) clearTimeout(timer)
})

const typeStyles = {
  info: "bg-blue-50 dark:bg-blue-900/30 border-blue-200 dark:border-blue-700 text-blue-800 dark:text-blue-200",
  success:
    "bg-green-50 dark:bg-green-900/30 border-green-200 dark:border-green-700 text-green-800 dark:text-green-200",
  error:
    "bg-red-50 dark:bg-red-900/30 border-red-200 dark:border-red-700 text-red-800 dark:text-red-200",
}
</script>

<template>
  <div
    v-if="visible"
    role="alert"
    :class="[
      'fixed bottom-4 right-4 z-50 max-w-sm rounded-lg border px-4 py-3 shadow-lg motion-safe:animate-in motion-safe:slide-in-from-bottom-4',
      typeStyles[type],
    ]"
  >
    <div class="flex items-start gap-3">
      <p class="flex-1 text-sm font-medium">{{ message }}</p>
      <button
        type="button"
        aria-label="Dismiss notification"
        class="shrink-0 rounded p-0.5 hover:opacity-70 focus:outline-none focus:ring-2 focus:ring-current"
        @click="dismiss"
      >
        &times;
      </button>
    </div>
  </div>
</template>
