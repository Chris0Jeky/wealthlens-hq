<script setup lang="ts">
import { ref, onErrorCaptured } from "vue";

const error = ref<Error | null>(null);

function reset() {
  error.value = null;
}

onErrorCaptured((err: Error) => {
  error.value = err;
  return false;
});
</script>

<template>
  <slot v-if="!error" />
  <div v-else class="max-w-2xl mx-auto px-6 py-10 text-center" role="alert">
    <h2 class="text-xl font-semibold text-red-600 mb-3">Something went wrong</h2>
    <p class="text-gray-600 mb-4">{{ error.message }}</p>
    <button
      class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
      @click="reset"
    >
      Try again
    </button>
  </div>
</template>
