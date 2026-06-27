<script setup lang="ts">
import { ref, watch } from "vue"

const props = withDefaults(
  defineProps<{
    modelValue: string
    placeholder?: string
    debounceMs?: number
  }>(),
  { placeholder: "Search...", debounceMs: 300 },
)

const emit = defineEmits<{
  (e: "update:modelValue", value: string): void
}>()

const localValue = ref(props.modelValue)
let timeout: ReturnType<typeof setTimeout> | null = null

watch(
  () => props.modelValue,
  (v) => {
    localValue.value = v
  },
)

function onInput(event: Event) {
  const val = (event.target as HTMLInputElement).value
  localValue.value = val

  if (timeout) clearTimeout(timeout)
  timeout = setTimeout(() => {
    emit("update:modelValue", val)
  }, props.debounceMs)
}

function clear() {
  localValue.value = ""
  emit("update:modelValue", "")
  if (timeout) clearTimeout(timeout)
}
</script>

<template>
  <div class="relative">
    <label for="search-input" class="sr-only">{{ placeholder }}</label>
    <input
      id="search-input"
      type="search"
      :value="localValue"
      :placeholder="placeholder"
      autocomplete="off"
      class="w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-2 pl-10 text-sm text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
      @input="onInput"
    />
    <span
      class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
      aria-hidden="true"
    >
      &#128269;
    </span>
    <button
      v-if="localValue"
      type="button"
      aria-label="Clear search"
      class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded"
      @click="clear"
    >
      &times;
    </button>
  </div>
</template>
