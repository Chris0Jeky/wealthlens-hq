<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { RouterLink } from 'vue-router'

const mobileMenuOpen = ref(false)
const hamburgerBtn = ref<HTMLButtonElement | null>(null)
const mobileNav = ref<HTMLElement | null>(null)

function toggleMenu() {
  mobileMenuOpen.value = !mobileMenuOpen.value
  if (mobileMenuOpen.value) {
    // Move focus into the mobile menu after it renders
    nextTick(() => {
      const firstLink = mobileNav.value?.querySelector<HTMLElement>('a')
      firstLink?.focus()
    })
  }
}

function closeMenu(returnFocus = false) {
  mobileMenuOpen.value = false
  if (returnFocus) {
    // Return focus to the hamburger button when closed via Escape
    nextTick(() => hamburgerBtn.value?.focus())
  }
}

function onMenuKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    closeMenu(true)
  }
}

const today = new Date().toLocaleDateString('en-GB', {
  day: 'numeric',
  month: 'short',
  year: 'numeric',
})
</script>

<template>
  <nav class="masthead" aria-label="Site header">
    <!-- Top band — dark ink strip -->
    <div class="masthead-band">
      <div class="band-left">
        <span class="live">
          <span class="dot" aria-hidden="true"></span>
          <span>Live · Updated {{ today }}</span>
        </span>
        <span class="band-issue">Issue №07 · Vol. MMXXVI</span>
      </div>
      <div class="band-right">
        <span>Open source · MIT</span>
        <span>England · Wales · Scotland · NI</span>
      </div>
    </div>

    <!-- Main nav row -->
    <div class="nav-inner">
      <RouterLink to="/" class="brand" aria-label="WealthLens UK — home page" @click="closeMenu()">
        <svg
          class="brand-mark"
          viewBox="0 0 68 68"
          fill="none"
          aria-hidden="true"
        >
          <circle
            cx="34"
            cy="34"
            r="26"
            stroke="currentColor"
            stroke-width="3"
            fill="none"
            style="color: var(--wl-ink)"
          />
          <path
            d="M 8 60 Q 32 60 44 50 Q 56 36 60 8"
            stroke="var(--wl-red)"
            stroke-width="2.8"
            fill="none"
            stroke-linecap="round"
          />
          <line
            x1="52"
            y1="52"
            x2="62"
            y2="62"
            stroke="var(--wl-ink)"
            stroke-width="3.5"
            stroke-linecap="round"
          />
        </svg>
        <span class="brand-text">WealthLens</span>
        <span class="brand-uk">UK</span>
      </RouterLink>

      <!-- Desktop nav links -->
      <div class="nav-links">
        <RouterLink to="/" class="nav-link" active-class="active" @click="closeMenu()">
          {{ $t('nav.home') }}
        </RouterLink>
        <RouterLink to="/charts/wealth-shares" class="nav-link" active-class="active" @click="closeMenu()">
          {{ $t('nav.data') }}
        </RouterLink>
        <RouterLink to="/simulator" class="nav-link" active-class="active" @click="closeMenu()">
          {{ $t('nav.simulator') }}
        </RouterLink>
        <RouterLink to="/data-sources" class="nav-link" active-class="active" @click="closeMenu()">
          {{ $t('nav.sources') }}
        </RouterLink>
        <RouterLink to="/methodology" class="nav-link" active-class="active" @click="closeMenu()">
          {{ $t('nav.methodology') }}
        </RouterLink>
        <RouterLink to="/about" class="nav-link" active-class="active" @click="closeMenu()">
          {{ $t('nav.about') }}
        </RouterLink>
        <RouterLink to="/contribute" class="nav-link" active-class="active" @click="closeMenu()">
          {{ $t('nav.contribute') }}
        </RouterLink>
      </div>

      <!-- Desktop right-side buttons -->
      <div class="nav-right">
        <a
          href="https://github.com/Chris0Jeky/wealthlens-hq"
          target="_blank"
          rel="noopener"
          class="wl-btn wl-btn--ghost wl-btn--sm"
        >
          {{ $t('nav.viewSource') }} ↗
        </a>
        <RouterLink to="/charts/wealth-shares" class="wl-btn wl-btn--red wl-btn--sm">
          {{ $t('nav.readTheData') }} →
        </RouterLink>
      </div>

      <!-- Mobile hamburger button -->
      <button
        ref="hamburgerBtn"
        class="hamburger"
        :aria-expanded="mobileMenuOpen"
        aria-controls="mobile-menu"
        aria-label="Toggle navigation menu"
        @click="toggleMenu"
      >
        <span class="hamburger-bar" :class="{ open: mobileMenuOpen }"></span>
        <span class="hamburger-bar" :class="{ open: mobileMenuOpen }"></span>
        <span class="hamburger-bar" :class="{ open: mobileMenuOpen }"></span>
      </button>
    </div>

    <!-- Mobile menu overlay -->
    <div
      v-if="mobileMenuOpen"
      id="mobile-menu"
      ref="mobileNav"
      class="mobile-menu"
      aria-label="Mobile navigation"
      @keydown="onMenuKeydown"
    >
      <RouterLink to="/" class="mobile-link" active-class="active" @click="closeMenu()">
        {{ $t('nav.home') }}
      </RouterLink>
      <RouterLink to="/charts/wealth-shares" class="mobile-link" active-class="active" @click="closeMenu()">
        {{ $t('nav.data') }}
      </RouterLink>
      <RouterLink to="/simulator" class="mobile-link" active-class="active" @click="closeMenu()">
        {{ $t('nav.simulator') }}
      </RouterLink>
      <RouterLink to="/data-sources" class="mobile-link" active-class="active" @click="closeMenu()">
        {{ $t('nav.sources') }}
      </RouterLink>
      <RouterLink to="/methodology" class="mobile-link" active-class="active" @click="closeMenu()">
        {{ $t('nav.methodology') }}
      </RouterLink>
      <RouterLink to="/about" class="mobile-link" active-class="active" @click="closeMenu()">
        {{ $t('nav.about') }}
      </RouterLink>
      <RouterLink to="/contribute" class="mobile-link" active-class="active" @click="closeMenu()">
        {{ $t('nav.contribute') }}
      </RouterLink>
      <div class="mobile-actions">
        <a
          href="https://github.com/Chris0Jeky/wealthlens-hq"
          target="_blank"
          rel="noopener"
          class="wl-btn wl-btn--ghost wl-btn--sm"
        >
          {{ $t('nav.viewSource') }} ↗
        </a>
        <RouterLink to="/charts/wealth-shares" class="wl-btn wl-btn--red wl-btn--sm" @click="closeMenu()">
          {{ $t('nav.readTheData') }} →
        </RouterLink>
      </div>
    </div>
  </nav>
</template>

<style scoped>
/* ============================================================
   MASTHEAD — broadsheet-style sticky nav
   ============================================================ */
.masthead {
  position: sticky;
  top: 0;
  z-index: 50;
  background: var(--wl-bg);
  border-bottom: 1px solid var(--wl-ink);
}

/* --- Top band ------------------------------------------------ */
.masthead-band {
  background: var(--wl-ink);
  color: var(--wl-paper);
  font-family: var(--wl-mono);
  font-size: 11px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 32px;
}

.band-left {
  display: flex;
  gap: 24px;
  align-items: center;
}

.live {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--wl-red);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.35; }
}

.band-right {
  display: flex;
  gap: 18px;
  opacity: 0.7;
}

/* --- Nav inner ------------------------------------------------ */
.nav-inner {
  max-width: var(--wl-max);
  margin: 0 auto;
  padding: 18px 32px;
  display: flex;
  align-items: center;
  gap: 32px;
}

/* --- Brand --------------------------------------------------- */
.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
}

.brand:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: 4px;
  border-radius: var(--wl-radius);
}

.brand-mark {
  width: 32px;
  height: 32px;
}

.brand-text {
  font-family: var(--wl-serif);
  font-weight: 700;
  font-size: 24px;
  letter-spacing: -0.025em;
  color: var(--wl-ink);
  line-height: 1;
}

.brand-uk {
  font-family: var(--wl-mono);
  font-size: 10px;
  letter-spacing: 0.22em;
  color: var(--wl-ink-muted);
  text-transform: uppercase;
  padding: 2px 6px;
  border: 1px solid var(--wl-rule-strong);
}

/* --- Nav links ----------------------------------------------- */
.nav-links {
  display: flex;
  gap: 2px;
  margin-left: 28px;
}

.nav-link {
  padding: 8px 14px;
  font-size: 14px;
  text-decoration: none;
  color: var(--wl-ink-body);
  font-weight: 500;
  border-bottom: 2px solid transparent;
  transition: color 0.15s ease;
}

.nav-link:hover {
  color: var(--wl-red);
}

.nav-link:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: 2px;
  border-radius: var(--wl-radius);
}

.nav-link.active {
  color: var(--wl-ink);
  border-bottom: 2px solid var(--wl-red);
  padding-bottom: 6px;
}

/* --- Right-side buttons -------------------------------------- */
.nav-right {
  margin-left: auto;
  display: flex;
  gap: 8px;
  align-items: center;
}

/* --- Hamburger (mobile only) --------------------------------- */
.hamburger {
  display: none;
  flex-direction: column;
  justify-content: center;
  gap: 5px;
  width: 32px;
  height: 32px;
  margin-left: auto;
  padding: 4px;
  border: none;
  background: transparent;
  cursor: pointer;
}

.hamburger:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: 2px;
  border-radius: var(--wl-radius);
}

.hamburger-bar {
  display: block;
  width: 100%;
  height: 2px;
  background: var(--wl-ink);
  transition: transform 0.25s ease, opacity 0.25s ease;
  transform-origin: center;
}

.hamburger-bar.open:nth-child(1) {
  transform: translateY(7px) rotate(45deg);
}

.hamburger-bar.open:nth-child(2) {
  opacity: 0;
}

.hamburger-bar.open:nth-child(3) {
  transform: translateY(-7px) rotate(-45deg);
}

/* --- Mobile menu --------------------------------------------- */
.mobile-menu {
  display: none;
  flex-direction: column;
  padding: 16px 32px 24px;
  border-top: 1px solid var(--wl-rule);
  background: var(--wl-bg);
}

.mobile-link {
  display: block;
  padding: 12px 0;
  font-size: 16px;
  font-weight: 500;
  text-decoration: none;
  color: var(--wl-ink-body);
  border-bottom: 1px solid var(--wl-rule);
}

.mobile-link:hover {
  color: var(--wl-red);
}

.mobile-link:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: 2px;
}

.mobile-link.active {
  color: var(--wl-red);
  font-weight: 600;
}

.mobile-actions {
  display: flex;
  gap: 8px;
  margin-top: 16px;
  flex-wrap: wrap;
}

/* --- Responsive ---------------------------------------------- */
@media (max-width: 768px) {
  .masthead-band {
    padding: 6px 16px;
    font-size: 10px;
  }

  .band-right {
    display: none;
  }

  .band-issue {
    display: none;
  }

  .nav-inner {
    padding: 14px 16px;
    gap: 16px;
  }

  .nav-links {
    display: none;
  }

  .nav-right {
    display: none;
  }

  .hamburger {
    display: flex;
  }

  .mobile-menu {
    display: flex;
    padding: 16px;
  }

  .brand-text {
    font-size: 20px;
  }
}

@media (max-width: 480px) {
  .masthead-band {
    padding: 4px 12px;
    font-size: 9px;
  }

  .nav-inner {
    padding: 12px;
  }

  .brand-uk {
    display: none;
  }
}
</style>
