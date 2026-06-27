<script setup lang="ts">
import { ref, nextTick, onErrorCaptured } from "vue"

const MAX_RETRIES = 3

const error = ref<Error | null>(null)
const errorId = ref("")
const retryCount = ref(0)
const errorContainer = ref<HTMLDivElement | null>(null)

function generateErrorId(): string {
  return `ERR-${Date.now().toString(36).slice(-6).toUpperCase()}`
}

function reset() {
  retryCount.value++
  error.value = null
}

onErrorCaptured((err: Error) => {
  error.value = err
  errorId.value = generateErrorId()
  nextTick(() => {
    errorContainer.value?.focus()
  })
  return false
})
</script>

<template>
  <slot v-if="!error" />
  <div
    v-else
    ref="errorContainer"
    tabindex="-1"
    class="max-w-2xl mx-auto px-6 py-10 text-center focus:outline-none"
    role="alert"
  >
    <h2 class="text-xl font-semibold text-[var(--wl-red)] mb-3">Something went wrong</h2>
    <p class="text-[var(--wl-ink-muted)] mb-4">{{ error.message }}</p>
    <p class="text-xs text-[var(--wl-ink-faint)] mb-4 font-mono">
      Error ID: {{ errorId }} · Attempt {{ retryCount + 1 }}/{{ MAX_RETRIES + 1 }}
    </p>
    <button
      v-if="retryCount < MAX_RETRIES"
      class="px-4 py-2 bg-[var(--wl-red)] text-white rounded hover:bg-[var(--wl-red-deep)] transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--wl-red)]"
      @click="reset"
    >
      Try again
    </button>
    <router-link
      v-else
      to="/"
      class="inline-flex items-center px-4 py-2 bg-[var(--wl-red)] text-white rounded hover:bg-[var(--wl-red-deep)] transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--wl-red)]"
    >
      &larr; Back to dashboard
    </router-link>
  </div>
</template>
