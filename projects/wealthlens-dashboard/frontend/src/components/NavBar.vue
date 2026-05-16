<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const mobileOpen = ref(false)

const navLinks = [
  { to: '/', label: 'Dashboard' },
  { to: '/charts/wealth-shares', label: 'Wealth Shares' },
  { to: '/charts/housing-affordability', label: 'Housing' },
  { to: '/charts/wealth-by-decile', label: 'Wealth by Decile' },
  { to: '/charts/cgt-concentration', label: 'CGT' },
]

function isActive(to: string): boolean {
  if (to === '/') return route.path === '/'
  return route.path.startsWith(to)
}

function closeMobile() {
  mobileOpen.value = false
}
</script>

<template>
  <header class="border-b border-gray-200 bg-white dark:bg-gray-900 dark:border-gray-700">
    <div class="max-w-6xl mx-auto px-4 sm:px-6">
      <div class="flex items-center justify-between h-14">
        <router-link
          to="/"
          class="text-xl font-bold tracking-tight text-gray-900 dark:text-white"
          @click="closeMobile"
        >
          WealthLens<span class="text-blue-600"> UK</span>
        </router-link>

        <nav
          aria-label="Main navigation"
          class="hidden md:flex items-center gap-1"
        >
          <router-link
            v-for="link in navLinks"
            :key="link.to"
            :to="link.to"
            class="px-3 py-1.5 rounded text-sm font-medium transition-colors"
            :class="
              isActive(link.to)
                ? 'bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300'
                : 'text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white'
            "
            :aria-current="isActive(link.to) ? 'page' : undefined"
          >
            {{ link.label }}
          </router-link>
          <a
            href="https://github.com/Chris0Jeky/wealthlens-hq"
            target="_blank"
            rel="noopener"
            class="ml-2 px-3 py-1.5 text-sm text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
          >
            GitHub
          </a>
        </nav>

        <button
          type="button"
          class="md:hidden p-2 rounded text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          :aria-expanded="mobileOpen"
          aria-controls="mobile-nav"
          aria-label="Toggle navigation menu"
          @click="mobileOpen = !mobileOpen"
        >
          <svg
            class="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              v-if="!mobileOpen"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 6h16M4 12h16M4 18h16"
            />
            <path
              v-else
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>

      <nav
        v-if="mobileOpen"
        id="mobile-nav"
        aria-label="Mobile navigation"
        class="md:hidden pb-3 space-y-1"
      >
        <router-link
          v-for="link in navLinks"
          :key="link.to"
          :to="link.to"
          class="block px-3 py-2 rounded text-sm font-medium transition-colors"
          :class="
            isActive(link.to)
              ? 'bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300'
              : 'text-gray-600 hover:bg-gray-50 dark:text-gray-400 dark:hover:bg-gray-800'
          "
          :aria-current="isActive(link.to) ? 'page' : undefined"
          @click="closeMobile"
        >
          {{ link.label }}
        </router-link>
        <a
          href="https://github.com/Chris0Jeky/wealthlens-hq"
          target="_blank"
          rel="noopener"
          class="block px-3 py-2 text-sm text-gray-500 hover:text-gray-900 dark:text-gray-400"
        >
          GitHub &nearr;
        </a>
      </nav>
    </div>
  </header>
</template>
