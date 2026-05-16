<script setup lang="ts">
import { RouterView } from 'vue-router'
import ErrorBoundary from '@/components/ErrorBoundary.vue'
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
    <header class="border-b border-[var(--wl-rule)] px-6 py-4">
      <div class="max-w-wl mx-auto flex items-center justify-between">
        <router-link to="/" class="text-xl font-bold tracking-tight">
          WealthLens<span class="text-[var(--wl-red)]"> UK</span>
        </router-link>
        <nav aria-label="Main navigation" class="flex gap-6 text-sm">
          <router-link
            to="/tools/wealth-calculator"
            class="text-[var(--wl-ink-muted)] hover:text-[var(--wl-ink)]"
          >
            Wealth Calculator
          </router-link>
          <a
            href="https://github.com/Chris0Jeky/wealthlens-hq"
            target="_blank"
            rel="noopener"
            class="text-[var(--wl-ink-muted)] hover:text-[var(--wl-ink)]"
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
    <footer
      role="contentinfo"
      class="border-t border-[var(--wl-rule)] px-6 py-6 mt-12 text-center text-sm text-[var(--wl-ink-muted)]"
    >
      <p>
        WealthLens UK &middot; Open source &middot; Data cited from ONS, WID,
        HMRC
      </p>
    </footer>
  </div>
</template>
