<script setup lang="ts">
/**
 * HomeView — the WealthLens UK front page.
 *
 * Composes the hero section (rotating headlines + wealth flow Sankey),
 * rent ticker, and the existing dataset listing. The dataset listing
 * is kept below as a fallback until the full landing page sections
 * (gut test, two Britains, pillars, etc.) are built in a later PR.
 */
import { onMounted } from 'vue'
import { useDataStore } from '@/stores/data'
import HeroSection from '@/components/HeroSection.vue'
import RentTicker from '@/components/RentTicker.vue'
import DatasetCard from '@/components/DatasetCard.vue'

const store = useDataStore()

const descriptions: Record<string, string> = {
  'wealth-shares':
    'Top 1% and 10% share of UK net personal wealth since 1820 (WID)',
  'housing-affordability':
    'House price to earnings ratio by region, 1997-2025 (ONS)',
  'wealth-by-decile':
    'Total net wealth by decile group in Great Britain (ONS WAS)',
  'cgt-concentration': 'Capital gains concentration by size of gain (HMRC)',
}

onMounted(() => {
  store.fetchDatasets()
})
</script>

<template>
  <div>
    <!-- Hero: rotating headlines + wealth flow Sankey -->
    <HeroSection />

    <!-- Live rent ticker -->
    <RentTicker />

    <!-- Existing dataset listing — kept until full landing page sections are built -->
    <div class="datasets-section">
      <section class="datasets-inner">
        <h2 class="datasets-heading">Available Datasets</h2>

        <div aria-live="polite">
          <p v-if="store.loading" class="datasets-loading">Loading datasets...</p>
        </div>
        <div aria-live="assertive">
          <p v-if="store.error" class="datasets-error">{{ store.error }}</p>
        </div>

        <div
          v-if="!store.loading && !store.error"
          class="datasets-grid"
          role="list"
        >
          <div v-for="name in store.datasets" :key="name" role="listitem">
            <DatasetCard
              :name="name"
              :description="descriptions[name] ?? 'UK inequality dataset'"
            />
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
/* ============================================================
   Datasets section — interim listing below the hero
   ============================================================ */
.datasets-section {
  padding: 64px 0;
  background: var(--wl-bg);
  border-bottom: 1px solid var(--wl-rule);
}

.datasets-inner {
  max-width: var(--wl-max);
  margin: 0 auto;
  padding: 0 32px;
}

.datasets-heading {
  font-family: var(--wl-serif);
  font-size: 28px;
  font-weight: 600;
  color: var(--wl-ink);
  margin: 0 0 24px;
  letter-spacing: -0.01em;
}

.datasets-loading {
  color: var(--wl-ink-muted);
  font-size: 15px;
}

.datasets-error {
  color: var(--wl-red);
  font-size: 15px;
}

.datasets-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
}

@media (max-width: 768px) {
  .datasets-section {
    padding: 36px 0;
  }

  .datasets-inner {
    padding: 0 16px;
  }

  .datasets-grid {
    grid-template-columns: 1fr;
  }
}
</style>
