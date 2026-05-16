<script setup lang="ts">
/**
 * ThemeToggle — three-way theme switcher for the broadsheet masthead.
 *
 * Cycles:  Front Page  →  Late Edition  →  Stark  → …
 * Icons are inline SVGs so there are no external dependencies.
 */
import { computed } from 'vue'
import { useTheme, type ThemeName } from '@/composables/useTheme'

const { currentTheme, toggleTheme, THEME_LABELS } = useTheme()

/** Next theme in the cycle — used for the aria-label hint. */
const NEXT: Record<ThemeName, ThemeName> = {
  light: 'dark',
  dark: 'stark',
  stark: 'light',
}

const ariaLabel = computed(
  () =>
    `Theme: ${THEME_LABELS[currentTheme.value]}. ` +
    `Switch to ${THEME_LABELS[NEXT[currentTheme.value]]}`,
)
</script>

<template>
  <button
    class="theme-toggle"
    type="button"
    :aria-label="ariaLabel"
    @click="toggleTheme"
  >
    <!-- Sun icon — Front Page (light) -->
    <svg
      v-if="currentTheme === 'light'"
      class="theme-icon"
      viewBox="0 0 20 20"
      fill="none"
      aria-hidden="true"
    >
      <circle cx="10" cy="10" r="4" stroke="currentColor" stroke-width="1.5" />
      <path
        d="M10 2v2M10 16v2M2 10h2M16 10h2M4.93 4.93l1.41 1.41M13.66 13.66l1.41 1.41M4.93 15.07l1.41-1.41M13.66 6.34l1.41-1.41"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
      />
    </svg>

    <!-- Moon icon — Late Edition (dark) -->
    <svg
      v-else-if="currentTheme === 'dark'"
      class="theme-icon"
      viewBox="0 0 20 20"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M15.5 11.5a6 6 0 01-7-7 6 6 0 107 7z"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    </svg>

    <!-- Contrast icon — Stark -->
    <svg
      v-else
      class="theme-icon"
      viewBox="0 0 20 20"
      fill="none"
      aria-hidden="true"
    >
      <circle cx="10" cy="10" r="7" stroke="currentColor" stroke-width="1.5" />
      <path d="M10 3a7 7 0 010 14V3z" fill="currentColor" />
    </svg>

    <span class="theme-label">{{ THEME_LABELS[currentTheme] }}</span>
  </button>
</template>

<style scoped>
.theme-toggle {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 32px;
  padding: 0 10px;
  font-family: var(--wl-mono);
  font-size: 11px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--wl-ink-body);
  background: transparent;
  border: 1px solid var(--wl-rule-strong);
  border-radius: var(--wl-radius);
  cursor: pointer;
  transition: border-color 0.15s ease, color 0.15s ease;
  white-space: nowrap;
}

.theme-toggle:hover {
  border-color: var(--wl-ink-muted);
  color: var(--wl-ink);
}

.theme-toggle:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: 2px;
  border-radius: var(--wl-radius);
}

.theme-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.theme-label {
  /* Hide label on very small screens to save space */
}

@media (max-width: 480px) {
  .theme-label {
    display: none;
  }

  .theme-toggle {
    padding: 0 8px;
  }
}
</style>
