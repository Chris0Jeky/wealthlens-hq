<script setup lang="ts">
import { useTheme } from '@/composables/useTheme'

const { theme, toggleTheme } = useTheme()
</script>

<template>
  <button
    type="button"
    aria-label="Toggle dark mode"
    :aria-pressed="theme === 'dark'"
    class="theme-toggle"
    @click="toggleTheme"
  >
    <span v-if="theme === 'dark'" aria-hidden="true" class="theme-toggle__icon">&#9728;</span>
    <span v-else aria-hidden="true" class="theme-toggle__icon">&#9789;</span>
  </button>
</template>

<style scoped>
.theme-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  padding: 0;
  border: 1px solid var(--wl-rule-strong);
  border-radius: var(--wl-radius);
  background: var(--wl-bg-muted);
  color: var(--wl-ink);
  cursor: pointer;
  transition: background 0.12s ease, border-color 0.12s ease;
}

.theme-toggle:hover {
  border-color: var(--wl-ink-muted);
}

.theme-toggle:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: 2px;
}

.theme-toggle__icon {
  font-size: 16px;
  line-height: 1;
}
</style>
