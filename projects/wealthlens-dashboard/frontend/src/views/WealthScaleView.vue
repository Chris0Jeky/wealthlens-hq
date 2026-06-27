<script setup lang="ts">
/**
 * WealthScaleView — page wrapper for the wealth scale scroller tool.
 *
 * Renders a breadcrumb trail, introductory text, the WealthScaleScroller
 * component, and source citations.
 *
 * Route: /tools/wealth-scale
 */
import WealthScaleScroller from "@/components/WealthScaleScroller.vue"
import SourceCitation from "@/components/SourceCitation.vue"
</script>

<template>
  <div class="scale-page">
    <!-- Breadcrumb -->
    <nav class="crumb" aria-label="Breadcrumb">
      <ol class="crumb__list">
        <li class="crumb__item">
          <router-link to="/" class="crumb__link">Home</router-link>
          <span class="crumb__sep" aria-hidden="true">/</span>
        </li>
        <li class="crumb__item">
          <span class="crumb__current">Tools</span>
          <span class="crumb__sep" aria-hidden="true">/</span>
        </li>
        <li class="crumb__item">
          <span class="crumb__current" aria-current="page"> Wealth to Scale </span>
        </li>
      </ol>
    </nav>

    <!-- Page header -->
    <header class="scale-page__header">
      <h1 class="scale-page__title">1 pixel = £1,000</h1>
      <p class="scale-page__subtitle">UK household wealth, to scale</p>
      <p class="scale-page__description">
        Scroll horizontally to explore how wealth is distributed across UK households. Each pixel
        you scroll represents £1,000. The median household sits at just 302 pixels from the left —
        but the richest individuals would be millions of pixels away.
      </p>
      <p class="scale-page__instructions">
        <strong>How to use:</strong> Scroll horizontally, swipe on mobile, or use arrow keys
        (Shift+Arrow for larger jumps). Press Home/End to jump to the start or end.
      </p>
    </header>

    <!-- The scroller component -->
    <WealthScaleScroller />

    <!-- Disclaimer -->
    <aside class="scale-page__disclaimer" aria-label="Data disclaimer">
      <p>
        Illustrative. Based on ONS Wealth and Assets Survey Round 7 (2018–2020). Individual
        circumstances vary. Wealth includes property, pensions, financial assets, and physical
        possessions minus debts.
      </p>
    </aside>

    <!-- Source citation -->
    <SourceCitation
      source="ONS, Total wealth in Great Britain: April 2018 to March 2020"
      source-url="https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/bulletins/totalwealthingreatbritain/april2018tomarch2020"
      access-date="2026-05-16"
    />
  </div>
</template>

<style scoped>
.scale-page {
  max-width: 1320px;
  margin: 0 auto;
  padding: 0 32px 64px;
}

.crumb {
  padding: 18px 0 0;
  font-family: var(--wl-mono);
  font-size: 11px;
  color: var(--wl-ink-muted);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.crumb__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}
.crumb__item {
  display: inline-flex;
  align-items: center;
}
.crumb__link {
  color: var(--wl-ink-muted);
  text-decoration: none;
}
.crumb__link:hover {
  color: var(--wl-red);
}
.crumb__link:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: 2px;
}
.crumb__sep {
  margin: 0 8px;
  color: var(--wl-rule-strong);
}
.crumb__current {
  color: var(--wl-ink);
}

/* Page header */
.scale-page__header {
  margin: 32px 0 24px;
}
.scale-page__title {
  font-family: var(--wl-serif);
  font-size: clamp(1.75rem, 4vw, 2.5rem);
  font-weight: 700;
  color: var(--wl-ink);
  margin: 0 0 4px;
  line-height: 1.2;
}
.scale-page__subtitle {
  font-family: var(--wl-serif);
  font-size: clamp(1rem, 2.5vw, 1.25rem);
  color: var(--wl-ink-muted);
  margin: 0 0 16px;
}
.scale-page__description {
  font-size: 0.95rem;
  color: var(--wl-ink);
  line-height: 1.6;
  max-width: 680px;
  margin: 0 0 12px;
}
.scale-page__instructions {
  font-size: 0.85rem;
  color: var(--wl-ink-muted);
  line-height: 1.5;
  max-width: 680px;
  margin: 0;
}

/* Disclaimer */
.scale-page__disclaimer {
  margin-top: 24px;
  padding: 12px 16px;
  background: var(--wl-paper);
  border: 1px solid var(--wl-rule);
  border-left: 3px solid var(--wl-red);
  border-radius: 3px;
  font-size: 0.8rem;
  color: var(--wl-ink-muted);
  line-height: 1.5;
}
.scale-page__disclaimer p {
  margin: 0;
}

@media (max-width: 768px) {
  .scale-page {
    padding: 0 16px 48px;
  }
}
</style>
