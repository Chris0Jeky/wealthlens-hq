<script setup lang="ts">
/**
 * RentTicker — dark band showing live rent flowing to private landlords.
 *
 * Displays a real-time counter of UK private rental sector revenue
 * (£85bn/year ≈ £2,695/second) accumulated since the user opened the
 * page. Red top border, pulsing dot, elapsed timer.
 *
 * Source: ONS Private Rental Market Statistics, 2024.
 */
import { useRentTicker } from '@/composables/useRentTicker'

const { rentPaid, elapsed } = useRentTicker()
</script>

<template>
  <section class="rent-ticker-band" aria-label="Live rent ticker">
    <div class="rent-ticker-inner">
      <span class="rent-ticker-label">
        <span class="rent-ticker-pulse" aria-hidden="true"></span>
        Live · since you opened this tab
      </span>

      <div class="rent-ticker-body">
        <span class="rent-ticker-num">{{ rentPaid }}</span>
        of <span class="rent-ticker-red">your generation's wages</span>
        have just become a private landlord's pension.
      </div>

      <div class="rent-ticker-aside">
        £85bn / year · UK private rents<br>
        ≈ <b>£2,695</b> every second · <b>{{ elapsed }}</b> on this page
      </div>
    </div>
  </section>
</template>

<style scoped>
/* ============================================================
   RENT TICKER — dark band between hero and content
   ============================================================ */
.rent-ticker-band {
  background: var(--wl-ink);
  color: var(--wl-paper);
  border-bottom: 1px solid var(--wl-ink);
  overflow: hidden;
  position: relative;
}

.rent-ticker-band::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--wl-red);
}

.rent-ticker-inner {
  max-width: var(--wl-max);
  margin: 0 auto;
  padding: 22px 32px;
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 32px;
  align-items: center;
}

/* --- Label with pulsing dot --------------------------------- */
.rent-ticker-label {
  font-family: var(--wl-mono);
  font-size: 10px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--wl-red);
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  white-space: nowrap;
}

.rent-ticker-pulse {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--wl-red);
  animation: ticker-pulse 1.4s infinite;
}

@keyframes ticker-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.35; }
}

/* --- Main body ---------------------------------------------- */
.rent-ticker-body {
  font-family: var(--wl-serif);
  font-size: 22px;
  line-height: 1.3;
  color: rgba(244, 239, 230, 0.92);
  letter-spacing: -0.01em;
}

.rent-ticker-num {
  font-family: var(--wl-serif);
  font-weight: 700;
  color: var(--wl-paper);
  font-variant-numeric: tabular-nums;
  font-size: 28px;
  letter-spacing: -0.02em;
  margin-right: 4px;
}

.rent-ticker-red {
  color: var(--wl-red);
}

/* --- Aside -------------------------------------------------- */
.rent-ticker-aside {
  font-family: var(--wl-mono);
  font-size: 11px;
  letter-spacing: 0.08em;
  text-align: right;
  color: rgba(244, 239, 230, 0.55);
  line-height: 1.5;
  white-space: nowrap;
}

.rent-ticker-aside b {
  color: var(--wl-paper);
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

/* --- Responsive --------------------------------------------- */
@media (max-width: 768px) {
  .rent-ticker-inner {
    grid-template-columns: 1fr;
    gap: 16px;
    padding: 18px 16px;
  }

  .rent-ticker-body {
    font-size: 18px;
  }

  .rent-ticker-num {
    font-size: 24px;
  }

  .rent-ticker-aside {
    text-align: left;
    font-size: 10px;
  }
}
</style>
