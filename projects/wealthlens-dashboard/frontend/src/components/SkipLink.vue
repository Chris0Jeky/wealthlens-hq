<script setup lang="ts">
defineProps<{
  target?: string
}>()
</script>

<template>
  <a
    :href="target ?? '#main-content'"
    class="skip-link"
  >
    Skip to main content
  </a>
</template>

<style scoped>
/*
 * WCAG 2.4.1 — Skip-to-content link.
 * Visually hidden by default; becomes visible on :focus-visible
 * so keyboard users can bypass repetitive navigation.
 */
.skip-link {
  position: fixed;
  top: -9999px;
  left: -9999px;
  z-index: 9999;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  font-family: var(--wl-sans);
  background: var(--wl-red);
  color: #fff;
  border-radius: var(--wl-radius);
  text-decoration: none;
  outline: 2px solid transparent;
  outline-offset: 2px;
}

.skip-link:focus-visible {
  top: 0.5rem;
  left: 0.5rem;
  outline-color: var(--wl-ink);
}
</style>
