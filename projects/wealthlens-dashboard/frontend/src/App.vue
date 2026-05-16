<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import ErrorBoundary from '@/components/ErrorBoundary.vue'
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import { useAnalytics } from '@/composables/useAnalytics'

const { init: initAnalytics } = useAnalytics()

onMounted(() => {
  initAnalytics()
})
</script>

<template>
  <!-- Root wrapper uses design-token backgrounds and ink colours.
       Theme switching: set data-theme="dark" or "stark" on <html>
       and all --wl-* custom properties update automatically. -->
  <div class="min-h-screen bg-[var(--wl-bg)] text-[var(--wl-ink-body)] font-wl-sans">
    <a
      href="#main-content"
      class="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-50 focus:px-4 focus:py-2 focus:bg-[var(--wl-red)] focus:text-white focus:rounded-wl"
    >
      Skip to main content
    </a>
    <AppHeader />
    <main id="main-content" tabindex="-1">
      <ErrorBoundary>
        <RouterView />
      </ErrorBoundary>
    </main>
    <AppFooter />
  </div>
</template>
