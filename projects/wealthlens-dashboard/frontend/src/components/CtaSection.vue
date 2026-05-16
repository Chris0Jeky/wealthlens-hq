<script setup lang="ts">
/**
 * CtaSection — centered call-to-action at the bottom of the landing page.
 *
 * Headline: "You can't fix what you can't see. Now you can see it."
 * Three action buttons: "Read the data" (red), "Contribute on GitHub"
 * (ghost), "Follow on Bluesky" (ghost).
 */
import { RouterLink } from 'vue-router'
</script>

<template>
  <section
    class="cta"
    data-screen-label="01 Landing — CTA"
    aria-labelledby="cta-heading"
  >
    <div class="cta-inner">
      <p class="cta-eyebrow">&darr; Ready when you are</p>

      <h2 id="cta-heading">
        You can't fix what you can't see.<br>
        Now you can <em>see it.</em>
      </h2>

      <p class="cta-lead">
        Pull the figure that proves what you already knew. Send it to the
        friend who needs the words. Build the chart you can't unsee.
      </p>

      <div class="cta-actions">
        <RouterLink to="/charts/wealth-shares" class="wl-btn wl-btn--red">
          Read the data &rarr;
        </RouterLink>
        <a
          href="https://github.com/Chris0Jeky/wealthlens-hq"
          target="_blank"
          rel="noopener noreferrer"
          class="wl-btn wl-btn--ghost"
        >
          Contribute on GitHub
        </a>
        <a
          href="https://bsky.app/profile/wealthlens.bsky.social"
          target="_blank"
          rel="noopener noreferrer"
          class="wl-btn wl-btn--ghost"
        >
          Follow on Bluesky
        </a>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* ============================================================
   CTA — final call-to-action
   ============================================================ */
.cta {
  padding: 120px 0;
  text-align: center;
  background: var(--wl-bg);
  border-bottom: 1px solid var(--wl-ink);
}

.cta-inner {
  max-width: 920px;
  margin: 0 auto;
  padding: 0 32px;
}

/* --- Eyebrow ------------------------------------------------ */
.cta-eyebrow {
  font-family: var(--wl-mono);
  font-size: 11px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--wl-red);
  font-weight: 600;
  margin: 0 0 24px;
}

/* --- Heading ------------------------------------------------ */
.cta h2 {
  font-family: var(--wl-serif);
  font-size: clamp(40px, 5.5vw, 72px);
  font-weight: 600;
  line-height: 1.02;
  letter-spacing: -0.025em;
  color: var(--wl-ink);
  margin: 0 0 36px;
  text-wrap: balance;
}

.cta h2 em {
  font-style: italic;
  color: var(--wl-red);
  font-weight: 500;
}

/* --- Lead text ---------------------------------------------- */
.cta-lead {
  font-size: 18px;
  color: var(--wl-ink-muted);
  line-height: 1.55;
  max-width: 38em;
  margin: -16px auto 36px;
}

/* --- Action buttons ----------------------------------------- */
.cta-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

/* --- Responsive --------------------------------------------- */
@media (max-width: 768px) {
  .cta {
    padding: 64px 0;
  }

  .cta-inner {
    padding: 0 16px;
  }

  .cta-lead {
    font-size: 16px;
  }

  .cta-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .cta-actions .wl-btn {
    justify-content: center;
    min-height: 44px;
    text-align: center;
  }
}

@media (max-width: 375px) {
  .cta {
    padding: 48px 0;
  }

  .cta h2 {
    font-size: clamp(28px, 7vw, 48px);
  }

  .cta-lead {
    font-size: 15px;
  }
}
</style>
