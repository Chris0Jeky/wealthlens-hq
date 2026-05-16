<script setup lang="ts">
import { ref } from 'vue'
import { RouterView } from 'vue-router'
import ErrorBoundary from '@/components/ErrorBoundary.vue'

/** Mobile nav open state. */
const mobileNavOpen = ref(false)

function toggleMobileNav() {
  mobileNavOpen.value = !mobileNavOpen.value
}

function closeMobileNav() {
  mobileNavOpen.value = false
}
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

        <!-- Desktop navigation -->
        <nav aria-label="Main navigation" class="hidden sm:flex gap-6 text-sm">
          <router-link
            to="/about"
            class="text-[var(--wl-ink-muted)] hover:text-[var(--wl-ink)]"
          >
            About
          </router-link>
          <router-link
            to="/methodology"
            class="text-[var(--wl-ink-muted)] hover:text-[var(--wl-ink)]"
          >
            Methodology
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

        <!-- Mobile nav toggle -->
        <button
          class="sm:hidden p-2 text-[var(--wl-ink-muted)] hover:text-[var(--wl-ink)]"
          :aria-expanded="mobileNavOpen"
          aria-controls="mobile-nav"
          aria-label="Toggle navigation menu"
          @click="toggleMobileNav"
        >
          <svg
            v-if="!mobileNavOpen"
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <line x1="3" y1="6" x2="21" y2="6" />
            <line x1="3" y1="12" x2="21" y2="12" />
            <line x1="3" y1="18" x2="21" y2="18" />
          </svg>
          <svg
            v-else
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>

      <!-- Mobile navigation menu -->
      <nav
        v-if="mobileNavOpen"
        id="mobile-nav"
        aria-label="Mobile navigation"
        class="sm:hidden mt-4 pt-4 border-t border-[var(--wl-rule)] flex flex-col gap-3 text-sm"
      >
        <router-link
          to="/about"
          class="text-[var(--wl-ink-muted)] hover:text-[var(--wl-ink)]"
          @click="closeMobileNav"
        >
          About
        </router-link>
        <router-link
          to="/methodology"
          class="text-[var(--wl-ink-muted)] hover:text-[var(--wl-ink)]"
          @click="closeMobileNav"
        >
          Methodology
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
      <p class="mt-2">
        <router-link
          to="/about"
          class="text-[var(--wl-ink-muted)] hover:text-[var(--wl-red)]"
        >About</router-link>
        <span class="mx-2" aria-hidden="true">&middot;</span>
        <router-link
          to="/methodology"
          class="text-[var(--wl-ink-muted)] hover:text-[var(--wl-red)]"
        >Methodology</router-link>
        <span class="mx-2" aria-hidden="true">&middot;</span>
        <a
          href="https://github.com/Chris0Jeky/wealthlens-hq"
          target="_blank"
          rel="noopener"
          class="text-[var(--wl-ink-muted)] hover:text-[var(--wl-red)]"
        >GitHub</a>
      </p>
    </footer>
  </div>
</template>
