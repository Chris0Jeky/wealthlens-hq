<script setup lang="ts">
/**
 * ChartLoadError — Fallback component shown when an async chart chunk
 * fails to load (network error, deploy race condition, etc.).
 *
 * Displays a user-friendly error message with a retry button that
 * reloads the page to re-attempt chunk loading.
 */

function retry() {
  window.location.reload();
}
</script>

<template>
  <div class="chart-load-error" role="alert" aria-live="assertive">
    <p class="chart-load-error__icon" aria-hidden="true">!</p>
    <p class="chart-load-error__message">
      Failed to load chart. This may be a temporary network issue.
    </p>
    <button
      class="chart-load-error__retry"
      type="button"
      @click="retry"
    >
      Retry
    </button>
  </div>
</template>

<style scoped>
.chart-load-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;
  min-height: 200px;
}

.chart-load-error__icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--wl-red, #dc2626);
  color: #fff;
  font-weight: 700;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 0 16px;
}

.chart-load-error__message {
  font-size: 16px;
  color: var(--wl-ink-body, #374151);
  margin: 0 0 20px;
  max-width: 36ch;
}

.chart-load-error__retry {
  font-family: var(--wl-mono, monospace);
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 10px 24px;
  border: 1px solid var(--wl-ink, #111827);
  background: transparent;
  color: var(--wl-ink, #111827);
  cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease;
}

.chart-load-error__retry:hover {
  background: var(--wl-ink, #111827);
  color: #fff;
}

.chart-load-error__retry:focus-visible {
  outline: 2px solid var(--wl-red, #dc2626);
  outline-offset: 2px;
}
</style>
