<script setup lang="ts">
import { usePageMeta } from "@/composables/usePageMeta"

// No `url`: a 404 page must not declare a canonical. The prerender bakes
// this view into dist/404.html (ADR 0001), so noindex ships to crawlers.
usePageMeta({
  title: "Page not found",
  description: "The page you're looking for doesn't exist or has been moved.",
  robots: "noindex",
})
</script>

<template>
  <div class="max-w-6xl mx-auto px-6 py-20 text-center">
    <p class="text-6xl font-bold text-[var(--wl-ink-faint)] mb-4" aria-hidden="true">404</p>
    <h1 class="text-2xl font-semibold mb-3">Page not found</h1>
    <p class="text-[var(--wl-ink-muted)] mb-6">
      The page you're looking for doesn't exist or has been moved.
    </p>
    <router-link
      to="/"
      class="inline-flex items-center px-4 py-2 bg-[var(--wl-red)] text-white rounded hover:bg-[var(--wl-red-deep)] transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--wl-red)]"
    >
      &larr; Back to dashboard
    </router-link>
  </div>
</template>
