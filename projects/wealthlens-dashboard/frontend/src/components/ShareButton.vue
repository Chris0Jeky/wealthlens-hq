<script setup lang="ts">
/**
 * ShareButton — Copies the current page URL to the clipboard.
 *
 * Displays "Copy link" by default and briefly shows "Copied!" for 2 seconds
 * after a successful copy. Only renders when the Clipboard API is available.
 */
import { ref, computed, onBeforeUnmount } from "vue";

const copied = ref(false);

/** Whether the Clipboard API is available in this browser. */
const isClipboardSupported = computed(
  () => typeof navigator !== "undefined" && !!navigator.clipboard,
);

let timeoutId: ReturnType<typeof setTimeout> | null = null;

async function copyUrl(): Promise<void> {
  try {
    await navigator.clipboard.writeText(window.location.href);
    copied.value = true;

    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    timeoutId = setTimeout(() => {
      copied.value = false;
      timeoutId = null;
    }, 2000);
  } catch {
    // Clipboard write failed — silently ignore.
  }
}

onBeforeUnmount(() => {
  if (timeoutId) {
    clearTimeout(timeoutId);
    timeoutId = null;
  }
});
</script>

<template>
  <button
    v-if="isClipboardSupported"
    type="button"
    aria-label="Copy chart URL to clipboard"
    class="text-sm text-gray-600 hover:text-gray-900 border border-gray-300 rounded px-3 py-1 inline-flex items-center gap-1 transition-colors"
    @click="copyUrl"
  >
    <!-- Inline SVG link icon -->
    <svg
      xmlns="http://www.w3.org/2000/svg"
      class="h-4 w-4"
      viewBox="0 0 20 20"
      fill="currentColor"
      aria-hidden="true"
    >
      <path
        fill-rule="evenodd"
        d="M12.586 4.586a2 2 0 112.828 2.828l-3 3a2 2 0 01-2.828 0 1 1 0 00-1.414 1.414 4 4 0 005.656 0l3-3a4 4 0 00-5.656-5.656l-1.5 1.5a1 1 0 101.414 1.414l1.5-1.5zm-5 5a2 2 0 012.828 0 1 1 0 101.414-1.414 4 4 0 00-5.656 0l-3 3a4 4 0 105.656 5.656l1.5-1.5a1 1 0 10-1.414-1.414l-1.5 1.5a2 2 0 11-2.828-2.828l3-3z"
        clip-rule="evenodd"
      />
    </svg>
    <span>{{ copied ? "Copied!" : "Copy link" }}</span>
  </button>
</template>
