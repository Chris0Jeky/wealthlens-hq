<script setup lang="ts">
/**
 * TaxCalculatorView — page wrapper for the tax calculator tool.
 *
 * Renders a breadcrumb trail and the TaxCalculator component.
 * Route: /tools/tax-calculator
 */
import TaxCalculator from "@/components/TaxCalculator.vue";
</script>

<template>
  <div class="calculator-page">
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
          <span class="crumb__current" aria-current="page">
            Tax Calculator
          </span>
        </li>
      </ol>
    </nav>

    <TaxCalculator />
  </div>
</template>

<style scoped>
.calculator-page {
  max-width: 1320px;
  margin: 0 auto;
}

.crumb {
  padding: 18px 32px 0;
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

@media (max-width: 768px) {
  .crumb {
    padding-left: 16px;
    padding-right: 16px;
  }
}
</style>
