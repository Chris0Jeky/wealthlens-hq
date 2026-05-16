<script setup lang="ts">
import { RouterView } from "vue-router";
import ErrorBoundary from "@/components/ErrorBoundary.vue";
</script>

<template>
  <div class="min-h-screen bg-white text-gray-900 font-sans">
    <a
      href="#main-content"
      class="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-50 focus:px-4 focus:py-2 focus:bg-blue-600 focus:text-white focus:rounded"
    >
      Skip to main content
    </a>
    <header class="border-b border-gray-200 px-6 py-4">
      <div class="max-w-6xl mx-auto flex items-center justify-between">
        <router-link to="/" class="text-xl font-bold tracking-tight">
          WealthLens<span class="text-blue-600"> UK</span>
        </router-link>
        <nav aria-label="Main navigation" class="flex gap-6 text-sm">
          <a
            href="https://github.com/Chris0Jeky/wealthlens-hq"
            target="_blank"
            rel="noopener"
            class="text-gray-600 hover:text-gray-900"
          >
            GitHub
          </a>
        </nav>
      </div>
    </header>
    <main id="main-content" tabindex="-1">
      <ErrorBoundary>
        <RouterView />
      </ErrorBoundary>
    </main>
    <footer role="contentinfo" class="border-t border-gray-200 px-6 py-6 mt-12 text-center text-sm text-gray-500">
      <p>
        WealthLens UK &middot; Open source &middot; Data cited from ONS, WID, HMRC
      </p>
    </footer>
  </div>
</template>
