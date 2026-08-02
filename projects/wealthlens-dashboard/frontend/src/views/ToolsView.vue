<script setup lang="ts">
import { RouterLink } from "vue-router"
import { usePageMeta } from "@/composables/usePageMeta"
import { SITE_URL } from "@/constants/site"
import { TOOLS } from "@/config/tools"

usePageMeta({
  title: "Interactive tools | WealthLens UK",
  description:
    "Explore WealthLens UK calculators, simulations, and visual tools for understanding wealth and tax.",
  url: `${SITE_URL}/tools`,
})
</script>

<template>
  <article class="tools-page">
    <header class="tools-header">
      <p class="tools-kicker">Interactive tools</p>
      <h1>Explore the numbers yourself</h1>
      <p class="tools-intro">
        Use these calculators and visualisations to explore where wealth sits, how tax affects
        income, and what different wealth-tax policies could raise.
      </p>
    </header>

    <ul class="tools-grid" role="list" aria-label="Interactive tools and related help">
      <li v-for="tool in TOOLS" :key="tool.to" class="tool-card">
        <RouterLink :to="tool.to" class="tool-link">
          <span class="tool-name">{{ tool.name }}</span>
          <span class="tool-blurb">{{ tool.blurb }}</span>
          <span class="tool-action" aria-hidden="true">Open {{ tool.name }} →</span>
        </RouterLink>
      </li>
    </ul>
  </article>
</template>

<style scoped>
.tools-page {
  max-width: var(--wl-max);
  margin: 0 auto;
  padding: 64px 32px 80px;
}

.tools-header {
  max-width: 720px;
  margin-bottom: 40px;
}

.tools-kicker {
  margin: 0 0 12px;
  color: var(--wl-red);
  font-family: var(--wl-mono);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

h1 {
  margin: 0;
  color: var(--wl-ink);
  font-family: var(--wl-serif);
  font-size: clamp(2.25rem, 5vw, 4rem);
  letter-spacing: -0.03em;
  line-height: 1.05;
}

.tools-intro {
  max-width: 62ch;
  margin: 20px 0 0;
  color: var(--wl-ink-body);
  font-size: 1.1rem;
  line-height: 1.65;
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 250px), 1fr));
  gap: 16px;
  margin: 0;
  padding: 0;
}

.tool-card {
  min-height: 190px;
  list-style: none;
}

.tool-link {
  display: flex;
  height: 100%;
  flex-direction: column;
  padding: 24px;
  color: var(--wl-ink);
  text-decoration: none;
  background: var(--wl-paper);
  border: 1px solid var(--wl-rule);
  border-top: 3px solid var(--wl-red);
  transition:
    border-color 0.15s ease,
    transform 0.15s ease,
    box-shadow 0.15s ease;
}

.tool-link:hover {
  border-color: var(--wl-red);
  box-shadow: 0 8px 20px rgb(0 0 0 / 10%);
  transform: translateY(-2px);
}

.tool-link:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: 3px;
}

.tool-name {
  font-family: var(--wl-serif);
  font-size: 1.35rem;
  font-weight: 700;
  line-height: 1.2;
}

.tool-blurb {
  margin-top: 12px;
  color: var(--wl-ink-body);
  line-height: 1.55;
}

.tool-action {
  margin-top: auto;
  padding-top: 20px;
  color: var(--wl-red);
  font-family: var(--wl-mono);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

@media (max-width: 600px) {
  .tools-page {
    padding: 48px 16px 64px;
  }

  .tools-header {
    margin-bottom: 28px;
  }
}
</style>
