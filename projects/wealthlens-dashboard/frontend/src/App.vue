<script setup lang="ts">
import { computed, onMounted, watch } from "vue"
import { RouterView, useRouter, useRoute } from "vue-router"
import ErrorBoundary from "@/components/ErrorBoundary.vue"
import AppHeader from "@/components/AppHeader.vue"
import AppFooter from "@/components/AppFooter.vue"
import SkipLink from "@/components/SkipLink.vue"
import { useAnalytics } from "@/composables/useAnalytics"

const { init: initAnalytics } = useAnalytics()

/**
 * Chrome-free mode for /embed/:name (RFC-001f): no header, footer, or skip
 * link inside third-party iframes. The pathname check covers the window
 * between mount and the router's first resolution, so embeds never flash
 * the site chrome.
 */
const route = useRoute()
const isEmbedPath = typeof window !== "undefined" && window.location.pathname.includes("/embed/")
const isEmbed = computed(() => route.meta.embed === true || isEmbedPath)

onMounted(() => {
  initAnalytics()
})

/**
 * Move focus to #main-content on route change so keyboard and screen-reader
 * users start from the top of the new page (WCAG 2.4.3 Focus Order).
 */
const router = useRouter()
watch(
  () => router.currentRoute.value.fullPath,
  () => {
    const main = document.getElementById("main-content")
    if (main) {
      main.focus({ preventScroll: false })
    }
  },
)
</script>

<template>
  <!-- Root wrapper uses design-token backgrounds and ink colours.
       Theme switching: set data-theme="dark" or "stark" on <html>
       and all --wl-* custom properties update automatically. -->
  <div class="min-h-screen bg-[var(--wl-bg)] text-[var(--wl-ink-body)] font-wl-sans">
    <SkipLink v-if="!isEmbed" />
    <!-- Reserved space for the Pulseboard Beta bar (observatory/README.md): after the skip
         link so keyboard users reach "Skip to main content" first. Static and v-once, so a
         re-render never patches it or the bar the SDK draws inside it; never v-if'd, so it
         survives route changes. min-height, never height: a wrapped bar grows it. The SDK
         releases it when no bar shows; src/utils/observatory.ts does wherever it is not loaded. -->
    <div v-once data-pulseboard-bar style="min-height: 2.5rem"></div>
    <AppHeader v-if="!isEmbed" />
    <main id="main-content" tabindex="-1">
      <ErrorBoundary>
        <RouterView />
      </ErrorBoundary>
    </main>
    <AppFooter v-if="!isEmbed" />
  </div>
</template>
