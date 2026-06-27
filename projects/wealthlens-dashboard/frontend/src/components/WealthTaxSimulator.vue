<script setup lang="ts">
/**
 * WealthTaxSimulator — interactive wealth tax revenue calculator.
 *
 * Allows users to configure progressive wealth tax bands with sliders
 * and see estimated annual revenue, affected households, and spending
 * comparisons. Uses a simplified Pareto model for illustration.
 *
 * Sources:
 * - ONS Wealth and Assets Survey, Round 7, April 2018 to March 2020
 *   URL: https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/bulletins/totalwealthingreatbritain/april2018tomarch2020
 *   Accessed: 2026-05-16
 * - Advani, Hughson and Tarrant (2021), Revenue and distributional
 *   modelling for a UK wealth tax
 *   URL: https://doi.org/10.1111/1475-5890.12280
 *   Accessed: 2026-05-17
 * - Wealth Tax Commission (2020), A wealth tax for the UK
 *   URL: https://www.ukwealth.tax/
 *   Accessed: 2026-05-17
 *
 * All calculation is client-side. No personal data is stored or transmitted.
 */
import { ref, computed } from "vue"
import {
  simulateWealthTax,
  formatRevenue,
  formatHouseholds,
  formatThreshold,
  getSpendingComparison,
  PRESET_SCENARIOS,
  SIMULATOR_SOURCES,
  type WealthTaxBand,
  type PresetScenario,
} from "@/utils/wealthTaxSimulator"

// ============================================================
// SLIDER OPTIONS
// ============================================================

/** Threshold steps for the slider (log-like steps) */
const THRESHOLD_STEPS = [
  500_000, 750_000, 1_000_000, 1_500_000, 2_000_000, 3_000_000, 5_000_000, 7_500_000, 10_000_000,
] as const

/** Rate steps for the slider */
const RATE_STEPS = [0.001, 0.0025, 0.005, 0.01, 0.015, 0.02, 0.03, 0.05] as const

/** Format a rate as a percentage string */
function formatRate(rate: number): string {
  return `${(rate * 100).toFixed(rate * 100 < 1 ? 2 : (rate * 100) % 1 === 0 ? 0 : 1)}%`
}

// ============================================================
// STATE
// ============================================================

interface BandState {
  thresholdIndex: number
  rateIndex: number
}

const MAX_BANDS = 3

/** Active bands as slider index positions */
const bands = ref<BandState[]>([
  { thresholdIndex: 4, rateIndex: 3 }, // £2m, 1%
])

/** Active preset name (null if user has modified sliders) */
const activePreset = ref<string | null>(null)

// ============================================================
// COMPUTED
// ============================================================

/** Convert slider indices to WealthTaxBand objects */
const taxBands = computed<WealthTaxBand[]>(() =>
  bands.value.map((b) => ({
    threshold: THRESHOLD_STEPS[b.thresholdIndex],
    rate: RATE_STEPS[b.rateIndex],
  })),
)

/** Simulation results */
const results = computed(() => simulateWealthTax(taxBands.value))

/** Spending comparison text */
const spendingText = computed(() => getSpendingComparison(results.value.annualRevenue))

/** Whether the add-band button should be shown */
const canAddBand = computed(() => bands.value.length < MAX_BANDS)

// ============================================================
// ACTIONS
// ============================================================

function addBand() {
  if (!canAddBand.value) return
  // Default new band: next threshold step above the last band, same rate
  const lastBand = bands.value[bands.value.length - 1]
  const nextThreshold = Math.min(lastBand.thresholdIndex + 2, THRESHOLD_STEPS.length - 1)
  const nextRate = Math.min(lastBand.rateIndex + 1, RATE_STEPS.length - 1)
  bands.value.push({ thresholdIndex: nextThreshold, rateIndex: nextRate })
  activePreset.value = null
}

function removeBand(index: number) {
  if (bands.value.length <= 1) return
  bands.value.splice(index, 1)
  activePreset.value = null
}

function applyPreset(preset: PresetScenario) {
  bands.value = preset.bands.map((b) => ({
    thresholdIndex: Math.max(
      0,
      THRESHOLD_STEPS.findIndex((t) => t === b.threshold),
    ),
    rateIndex: Math.max(
      0,
      RATE_STEPS.findIndex((r) => r === b.rate),
    ),
  }))
  activePreset.value = preset.name
}

function onSliderChange() {
  activePreset.value = null
}
</script>

<template>
  <div class="sim">
    <!-- Header -->
    <header class="sim__header">
      <p class="wl-eyebrow">Interactive tool</p>
      <h1 class="sim__title">
        Wealth Tax
        <em>Revenue Simulator</em>
      </h1>
      <p class="sim__lede">
        How much could a UK wealth tax raise? Adjust the thresholds and rates below to explore
        different scenarios. The model uses ONS wealth distribution data and a Pareto approximation.
      </p>
      <p class="sim__privacy">
        All calculation happens in your browser. No data is stored or transmitted.
      </p>
    </header>

    <!-- Preset scenarios -->
    <section class="sim__presets" aria-label="Preset scenarios">
      <p class="sim__presets-label">Preset scenarios:</p>
      <div class="sim__presets-row" role="group" aria-label="Preset scenario buttons">
        <button
          v-for="preset in PRESET_SCENARIOS"
          :key="preset.name"
          :class="[
            'wl-btn wl-btn--ghost wl-btn--sm',
            { 'wl-btn--active': activePreset === preset.name },
          ]"
          :aria-pressed="activePreset === preset.name"
          @click="applyPreset(preset)"
        >
          {{ preset.name }}
          <span class="sim__preset-desc">{{ preset.description }}</span>
        </button>
      </div>
    </section>

    <!-- Tax bands configuration -->
    <section class="sim__bands" aria-label="Tax band configuration">
      <h2 class="sim__section-heading">Configure tax bands</h2>

      <div v-for="(band, i) in bands" :key="i" class="sim__band" :aria-label="`Tax band ${i + 1}`">
        <div class="sim__band-header">
          <span class="sim__band-number">Band {{ i + 1 }}</span>
          <button
            v-if="bands.length > 1"
            class="sim__band-remove"
            :aria-label="`Remove band ${i + 1}`"
            @click="removeBand(i)"
          >
            Remove
          </button>
        </div>

        <div class="sim__band-controls">
          <!-- Threshold slider -->
          <div class="sim__slider-group">
            <label :for="`threshold-${i}`" class="sim__slider-label">
              Threshold:
              <strong class="sim__slider-value">
                {{ formatThreshold(THRESHOLD_STEPS[band.thresholdIndex]) }}
              </strong>
            </label>
            <input
              :id="`threshold-${i}`"
              v-model.number="band.thresholdIndex"
              type="range"
              :min="0"
              :max="THRESHOLD_STEPS.length - 1"
              step="1"
              class="sim__slider"
              :aria-valuetext="formatThreshold(THRESHOLD_STEPS[band.thresholdIndex])"
              @input="onSliderChange"
            />
            <div class="sim__slider-range">
              <span>{{ formatThreshold(THRESHOLD_STEPS[0]) }}</span>
              <span>{{ formatThreshold(THRESHOLD_STEPS[THRESHOLD_STEPS.length - 1]) }}</span>
            </div>
          </div>

          <!-- Rate slider -->
          <div class="sim__slider-group">
            <label :for="`rate-${i}`" class="sim__slider-label">
              Rate:
              <strong class="sim__slider-value">
                {{ formatRate(RATE_STEPS[band.rateIndex]) }}
              </strong>
            </label>
            <input
              :id="`rate-${i}`"
              v-model.number="band.rateIndex"
              type="range"
              :min="0"
              :max="RATE_STEPS.length - 1"
              step="1"
              class="sim__slider"
              :aria-valuetext="formatRate(RATE_STEPS[band.rateIndex])"
              @input="onSliderChange"
            />
            <div class="sim__slider-range">
              <span>{{ formatRate(RATE_STEPS[0]) }}</span>
              <span>{{ formatRate(RATE_STEPS[RATE_STEPS.length - 1]) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Add band button -->
      <button v-if="canAddBand" class="wl-btn wl-btn--ghost sim__add-band" @click="addBand">
        + Add band ({{ bands.length }}/{{ MAX_BANDS }})
      </button>
    </section>

    <!-- Results -->
    <section class="sim__results" aria-live="polite" aria-label="Simulation results">
      <hr class="wl-rule-red" />

      <!-- Headline revenue -->
      <div class="sim__headline">
        <p class="wl-eyebrow">Estimated annual revenue</p>
        <p class="sim__revenue">{{ formatRevenue(results.annualRevenue) }}</p>
        <p v-if="spendingText" class="sim__comparison">
          {{ spendingText }}
        </p>
      </div>

      <!-- Stats grid -->
      <div class="sim__stat-grid">
        <div class="sim__stat">
          <span class="sim__stat-label">Taxable units affected</span>
          <span class="sim__stat-value wl-num">
            {{ formatHouseholds(results.affectedHouseholds) }}
          </span>
        </div>
        <div class="sim__stat">
          <span class="sim__stat-label">Average tax per household</span>
          <span class="sim__stat-value wl-num">
            {{ formatRevenue(results.averageTaxPerHousehold) }}
          </span>
        </div>
        <div class="sim__stat">
          <span class="sim__stat-label">Revenue as % of GDP</span>
          <span class="sim__stat-value wl-num"> {{ results.revenueAsPercentGDP }}% </span>
        </div>
      </div>

      <!-- Band summary -->
      <div class="sim__band-summary">
        <h3 class="sim__summary-heading">Your tax bands</h3>
        <ul class="sim__summary-list">
          <li v-for="(band, i) in taxBands" :key="i" class="sim__summary-item">
            <strong>{{ formatRate(band.rate) }}</strong> on wealth above
            <strong>{{ formatThreshold(band.threshold) }}</strong>
          </li>
        </ul>
      </div>
    </section>

    <!-- Disclaimer and sources -->
    <footer class="sim__footer">
      <div class="sim__disclaimer">
        <p class="sim__disclaimer-text">
          {{ SIMULATOR_SOURCES.disclaimer }}
        </p>
      </div>

      <div class="sim__source">
        <span class="wl-source">Sources:</span>
        <p class="sim__source-detail">
          <span
            v-for="source in SIMULATOR_SOURCES.references"
            :key="source.url"
            class="sim__source-item"
          >
            <a :href="source.url" target="_blank" rel="noopener">
              {{ source.label }}
            </a>
            <span>Accessed {{ source.accessDate }}</span>
          </span>
        </p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* ============================================================ */
/* SIMULATOR LAYOUT                                              */
/* ============================================================ */
.sim {
  max-width: 860px;
  margin: 0 auto;
  padding: 48px 32px 96px;
}

/* ============================================================ */
/* HEADER                                                        */
/* ============================================================ */
.sim__header {
  margin-bottom: 40px;
  border-bottom: 2px solid var(--wl-ink);
  padding-bottom: 32px;
}

.sim__title {
  font-family: var(--wl-serif);
  font-size: clamp(36px, 6vw, 64px);
  font-weight: 600;
  line-height: 1;
  letter-spacing: -0.025em;
  color: var(--wl-ink);
  margin: 12px 0 20px;
}
.sim__title em {
  font-style: italic;
  color: var(--wl-red);
  font-weight: 500;
}

.sim__lede {
  font-size: 18px;
  line-height: 1.6;
  color: var(--wl-ink-body);
  max-width: 56ch;
  margin: 0 0 12px;
}

.sim__privacy {
  font-family: var(--wl-mono);
  font-size: 11px;
  color: var(--wl-ink-faint);
  letter-spacing: 0.04em;
  margin: 0;
}

/* ============================================================ */
/* PRESETS                                                       */
/* ============================================================ */
.sim__presets {
  margin-bottom: 32px;
}

.sim__presets-label {
  font-family: var(--wl-mono);
  font-size: 11px;
  color: var(--wl-ink-muted);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  margin: 0 0 12px;
}

.sim__presets-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.sim__preset-desc {
  display: block;
  font-size: 10px;
  opacity: 0.7;
  margin-top: 2px;
}

.wl-btn--active {
  background: var(--wl-red);
  color: #fff;
  border-color: var(--wl-red);
}

/* ============================================================ */
/* BAND CONFIGURATION                                            */
/* ============================================================ */
.sim__bands {
  margin-bottom: 40px;
}

.sim__section-heading {
  font-family: var(--wl-serif);
  font-size: 22px;
  font-weight: 600;
  color: var(--wl-ink);
  margin: 0 0 20px;
}

.sim__band {
  background: var(--wl-card);
  border: 1px solid var(--wl-rule);
  padding: 20px 24px;
  margin-bottom: 12px;
}

.sim__band-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.sim__band-number {
  font-family: var(--wl-mono);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--wl-ink-muted);
  font-weight: 600;
}

.sim__band-remove {
  font-family: var(--wl-mono);
  font-size: 11px;
  color: var(--wl-red);
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 8px;
  letter-spacing: 0.04em;
}
.sim__band-remove:hover {
  text-decoration: underline;
}
.sim__band-remove:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: 2px;
}

.sim__band-controls {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

/* ============================================================ */
/* SLIDERS                                                       */
/* ============================================================ */
.sim__slider-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sim__slider-label {
  font-family: var(--wl-mono);
  font-size: 12px;
  color: var(--wl-ink-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.sim__slider-value {
  color: var(--wl-ink);
  font-size: 16px;
  text-transform: none;
  letter-spacing: 0;
}

.sim__slider {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 6px;
  background: var(--wl-bg-muted, #e5e5e5);
  border-radius: 3px;
  outline: none;
  cursor: pointer;
}

.sim__slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--wl-red);
  border: 2px solid var(--wl-card);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  cursor: pointer;
}

.sim__slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--wl-red);
  border: 2px solid var(--wl-card);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  cursor: pointer;
}

.sim__slider:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: 4px;
}

.sim__slider-range {
  display: flex;
  justify-content: space-between;
  font-family: var(--wl-mono);
  font-size: 10px;
  color: var(--wl-ink-faint);
}

/* ============================================================ */
/* ADD BAND BUTTON                                               */
/* ============================================================ */
.sim__add-band {
  width: 100%;
  margin-top: 8px;
  border-style: dashed;
}

/* ============================================================ */
/* RESULTS                                                       */
/* ============================================================ */
.sim__results {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.sim__headline {
  text-align: center;
  padding: 36px 0 24px;
}

.sim__revenue {
  font-family: var(--wl-serif);
  font-size: clamp(36px, 6vw, 56px);
  font-weight: 700;
  color: var(--wl-red);
  margin: 12px 0 8px;
  line-height: 1.1;
}

.sim__comparison {
  font-size: 16px;
  color: var(--wl-ink-body);
  margin: 8px 0 0;
  font-style: italic;
}

/* ============================================================ */
/* STATS GRID                                                    */
/* ============================================================ */
.sim__stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1px;
  background: var(--wl-rule);
  border: 1px solid var(--wl-ink);
  margin: 24px 0;
}

.sim__stat {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 16px 20px;
  background: var(--wl-card);
}

.sim__stat-label {
  font-family: var(--wl-mono);
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--wl-ink-muted);
}

.sim__stat-value {
  font-size: 22px;
  font-weight: 600;
  color: var(--wl-ink);
}

/* ============================================================ */
/* BAND SUMMARY                                                  */
/* ============================================================ */
.sim__band-summary {
  margin: 28px 0;
  padding: 20px 24px;
  background: var(--wl-card);
  border: 1px solid var(--wl-rule);
}

.sim__summary-heading {
  font-family: var(--wl-mono);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--wl-ink-muted);
  margin: 0 0 12px;
}

.sim__summary-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.sim__summary-item {
  font-size: 15px;
  color: var(--wl-ink-body);
  padding: 6px 0;
  border-bottom: 1px solid var(--wl-rule);
}
.sim__summary-item:last-child {
  border-bottom: none;
}
.sim__summary-item strong {
  color: var(--wl-ink);
  font-weight: 600;
}

/* ============================================================ */
/* FOOTER / DISCLAIMER                                           */
/* ============================================================ */
.sim__footer {
  margin-top: 40px;
  padding-top: 24px;
  border-top: 1px solid var(--wl-rule);
}

.sim__disclaimer {
  padding: 16px 20px;
  background: var(--wl-bg-muted, #f5f5f5);
  border-left: 3px solid var(--wl-ink-faint);
  margin-bottom: 20px;
}

.sim__disclaimer-text {
  font-family: var(--wl-mono);
  font-size: 12px;
  color: var(--wl-ink-muted);
  margin: 0;
  line-height: 1.5;
}

.sim__source {
  margin: 16px 0;
}

.sim__source-detail {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-family: var(--wl-mono);
  font-size: 11px;
  color: var(--wl-ink-muted);
  margin: 8px 0 0;
  line-height: 1.5;
}
.sim__source-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.sim__source-detail a {
  color: var(--wl-red);
  text-decoration: none;
  border-bottom: 1px solid var(--wl-red);
}
.sim__source-detail a:hover {
  border-bottom-width: 2px;
}
.sim__source-detail a:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: 2px;
}

/* ============================================================ */
/* RESPONSIVE                                                    */
/* ============================================================ */
@media (max-width: 768px) {
  .sim {
    padding: 32px 16px 64px;
  }

  .sim__band-controls {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .sim__stat-grid {
    grid-template-columns: 1fr;
  }

  .sim__presets-row {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
