<script setup lang="ts">
import { ref, nextTick, onErrorCaptured } from "vue";

const MAX_RETRIES = 3;

const error = ref<Error | null>(null);
const retryCount = ref(0);
const errorContainer = ref<HTMLDivElement | null>(null);

function reset() {
  retryCount.value++;
  error.value = null;
}

onErrorCaptured((err: Error) => {
  error.value = err;
  nextTick(() => {
    errorContainer.value?.focus();
  });
  return false;
});
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
    <h2 class="text-xl font-semibold text-red-600 mb-3">Something went wrong</h2>
    <p class="text-gray-600 mb-4">{{ error.message }}</p>
    <button
      v-if="retryCount < MAX_RETRIES"
      class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
      @click="reset"
    >
      Try again
    </button>
    <router-link
      v-else
      to="/"
      class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
    >
      &larr; Back to dashboard
    </router-link>
  </div>
</template>
