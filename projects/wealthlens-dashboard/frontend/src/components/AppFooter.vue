<script setup lang="ts">
import { RouterLink } from 'vue-router'
import HealthStatus from './HealthStatus.vue'

const year = new Date().getFullYear()
</script>

<template>
  <footer class="foot" role="contentinfo">
    <div class="foot-inner">
      <!-- Brand column -->
      <div class="foot-col foot-brand">
        <RouterLink to="/" class="brand" aria-label="WealthLens UK — home page">
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
              stroke="var(--wl-ink)"
              stroke-width="3"
              fill="none"
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
        <p>
          Every statistic on this site links to its primary source.
          Source-backed. Open-source. Impossible to ignore.
        </p>
      </div>

      <!-- Explore column -->
      <div class="foot-col">
        <h4>Explore</h4>
        <ul>
          <li>
            <RouterLink to="/charts/wealth-shares">All charts</RouterLink>
          </li>
          <li>
            <RouterLink to="/charts/wealth-shares">Wealth</RouterLink>
          </li>
          <li>
            <RouterLink to="/charts/housing-affordability">Housing</RouterLink>
          </li>
          <li>
            <RouterLink to="/charts/cgt-concentration">Tax</RouterLink>
          </li>
          <li>
            <RouterLink to="/charts/wealth-by-decile">
              Income &amp; opportunity
            </RouterLink>
          </li>
        </ul>
      </div>

      <!-- Project column -->
      <div class="foot-col">
        <h4>Project</h4>
        <ul>
          <li><RouterLink to="/about">About</RouterLink></li>
          <li><RouterLink to="/methodology">Methodology</RouterLink></li>
          <li><RouterLink to="/contribute">Contribute</RouterLink></li>
          <li>
            <a
              href="https://github.com/Chris0Jeky/wealthlens-hq/blob/main/LICENSE"
              target="_blank"
              rel="noopener"
            >
              Licence (MIT)
            </a>
          </li>
        </ul>
      </div>

      <!-- Follow column -->
      <div class="foot-col">
        <h4>Follow</h4>
        <ul>
          <li>
            <a
              href="https://github.com/Chris0Jeky/wealthlens-hq"
              target="_blank"
              rel="noopener"
            >
              GitHub
            </a>
          </li>
          <!-- TODO: Replace with actual WealthLens Bluesky profile URL once confirmed -->
          <li>
            <a
              href="#"
              target="_blank"
              rel="noopener"
            >
              Bluesky
            </a>
          </li>
          <!-- TODO: Replace with actual WealthLens Mastodon profile URL once confirmed -->
          <li>
            <a
              href="#"
              target="_blank"
              rel="noopener"
            >
              Mastodon
            </a>
          </li>
        </ul>
      </div>
    </div>

    <!-- Bottom bar -->
    <div class="foot-base">
      <span>&copy; {{ year }} WealthLens UK · MIT licensed</span>
      <HealthStatus />
      <span>Made in London · Independent · Non-partisan</span>
    </div>
  </footer>
</template>

<style scoped>
/* ============================================================
   FOOTER — 4-column broadsheet footer
   ============================================================ */
.foot {
  padding: 56px 0 32px;
  background: var(--wl-bg);
}

.foot-inner {
  max-width: var(--wl-max);
  margin: 0 auto;
  padding: 0 32px;
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 48px;
}

/* --- Column styles ------------------------------------------- */
.foot-col h4 {
  font-family: var(--wl-mono);
  font-size: 11px;
  letter-spacing: 0.14em;
  color: var(--wl-ink-muted);
  text-transform: uppercase;
  margin: 0 0 14px;
  font-weight: 500;
}

.foot-col ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.foot-col a {
  color: var(--wl-ink-body);
  text-decoration: none;
  font-size: 14px;
  transition: color 0.15s ease;
}

.foot-col a:hover {
  color: var(--wl-red);
}

.foot-col a:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: 2px;
  border-radius: var(--wl-radius);
}

/* --- Brand column -------------------------------------------- */
.foot-brand .brand {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
}

.foot-brand .brand:focus-visible {
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

.foot-brand p {
  font-size: 13px;
  color: var(--wl-ink-muted);
  margin: 14px 0 0;
  max-width: 36ch;
  line-height: 1.5;
}

/* --- Bottom bar ---------------------------------------------- */
.foot-base {
  max-width: var(--wl-max);
  margin: 56px auto 0;
  padding: 20px 32px 0;
  border-top: 1px solid var(--wl-rule);
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
  font-family: var(--wl-mono);
  font-size: 11px;
  color: var(--wl-ink-muted);
}

/* --- Responsive ---------------------------------------------- */
@media (max-width: 768px) {
  .foot-inner {
    grid-template-columns: 1fr 1fr;
    gap: 32px;
    padding: 0 16px;
  }

  .foot-brand {
    grid-column: 1 / -1;
  }

  .foot-base {
    padding: 20px 16px 0;
    margin-top: 32px;
  }
}

@media (max-width: 480px) {
  .foot-inner {
    grid-template-columns: 1fr;
    gap: 24px;
    padding: 0 12px;
  }

  .foot-base {
    flex-direction: column;
    gap: 8px;
    padding: 16px 12px 0;
  }
}
</style>
