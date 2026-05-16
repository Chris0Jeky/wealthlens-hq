<script setup lang="ts">
/**
 * WealthCalculator — "Where Do You Fit in UK Wealth?"
 *
 * Interactive calculator that lets users enter their estimated net
 * household wealth and see where they rank in the UK wealth distribution.
 * Uses ONS Wealth and Assets Survey Round 7 (2018-2020) decile data.
 *
 * All calculation is client-side. No personal data is stored or transmitted.
 *
 * Source: ONS Wealth and Assets Survey, Round 7, April 2018 to March 2020
 * URL: https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/bulletins/totalwealthingreatbritain/april2018tomarch2020
 * Accessed: 2026-05-16
 */
import { ref, computed } from "vue";
import {
  getDecile,
  getPercentile,
  getContext,
  formatGBP,
  DECILE_DATA,
  COMPARISON_STATS,
} from "@/utils/wealthPosition";

/** Raw text input from the user */
const wealthInput = ref("");

/** Whether the user has triggered a calculation */
const hasCalculated = ref(false);

/** Parse the input, stripping £, commas, and whitespace */
const parsedWealth = computed(() => {
  const cleaned = wealthInput.value.replace(/[£,\s]/g, "");
  const num = Number(cleaned);
  return Number.isFinite(num) ? num : null;
});

/** Whether the current input is valid */
const isValid = computed(() => parsedWealth.value !== null);

/** Current decile (1-10) */
const decile = computed(() =>
  parsedWealth.value !== null ? getDecile(parsedWealth.value) : null,
);

/** Approximate percentile (0-100) */
const percentile = computed(() =>
  parsedWealth.value !== null ? getPercentile(parsedWealth.value) : null,
);

/** Contextual explanation message */
const contextMessage = computed(() =>
  decile.value !== null ? getContext(decile.value) : "",
);

/** Ordinal suffix for decile display */
const decileOrdinal = computed(() => {
  if (decile.value === null) return "";
  const n = decile.value;
  if (n === 1) return "1st";
  if (n === 2) return "2nd";
  if (n === 3) return "3rd";
  return `${n}th`;
});

/** Apply a preset value to the input */
function applyPreset(value: number) {
  wealthInput.value = value.toLocaleString("en-GB");
  hasCalculated.value = false;
}

/** Run the calculation */
function calculate() {
  if (isValid.value) {
    hasCalculated.value = true;
  }
}

/** Handle Enter key on the input */
function onKeydown(e: KeyboardEvent) {
  if (e.key === "Enter") {
    calculate();
  }
}

/** Reset the calculator */
function reset() {
  wealthInput.value = "";
  hasCalculated.value = false;
}
</script>

<template>
  <div class="calc">
    <!-- Header -->
    <header class="calc__header">
      <p class="wl-eyebrow">Interactive tool</p>
      <h1 class="calc__title">
        Where do you fit in
        <em>UK wealth?</em>
      </h1>
      <p class="calc__lede">
        Enter your estimated total household net wealth — property equity,
        pensions, savings and investments, minus any mortgages and debts —
        and see where you rank among UK households.
      </p>
      <p class="calc__privacy">
        All calculation happens in your browser. No data is stored or
        transmitted.
      </p>
    </header>

    <!-- Input section -->
    <section class="calc__input-section" aria-label="Wealth input">
      <label for="wealth-input" class="calc__label">
        Your total household net wealth
      </label>
      <p id="wealth-input-help" class="calc__help">
        Add up: property equity + pension value + savings + investments,
        then subtract mortgages + debts. This is about
        <strong>household</strong> wealth, not individual.
      </p>

      <div class="calc__input-row">
        <span class="calc__currency" aria-hidden="true">&pound;</span>
        <input
          id="wealth-input"
          v-model="wealthInput"
          type="text"
          inputmode="numeric"
          class="calc__input"
          placeholder="e.g. 150,000"
          aria-describedby="wealth-input-help"
          :aria-invalid="wealthInput.length > 0 && !isValid ? 'true' : undefined"
          @keydown="onKeydown"
        />
        <button
          class="wl-btn wl-btn--red calc__btn"
          :disabled="!isValid"
          @click="calculate"
        >
          Calculate
        </button>
      </div>

      <p
        v-if="wealthInput.length > 0 && !isValid"
        class="calc__error"
        role="alert"
      >
        Please enter a valid number. You can include negative values for
        net debt.
      </p>

      <!-- Quick presets -->
      <div class="calc__presets" role="group" aria-label="Quick presets">
        <p class="calc__presets-label">Quick estimates:</p>
        <button
          class="wl-btn wl-btn--ghost wl-btn--sm"
          @click="applyPreset(5_000)"
        >
          Renter, ~&pound;5k savings
        </button>
        <button
          class="wl-btn wl-btn--ghost wl-btn--sm"
          @click="applyPreset(100_000)"
        >
          Homeowner, &pound;100k equity
        </button>
        <button
          class="wl-btn wl-btn--ghost wl-btn--sm"
          @click="applyPreset(302_500)"
        >
          UK median (&pound;302,500)
        </button>
        <button
          class="wl-btn wl-btn--ghost wl-btn--sm"
          @click="applyPreset(-5_000)"
        >
          Net debt (-&pound;5k)
        </button>
      </div>
    </section>

    <!-- Results section -->
    <section
      v-if="hasCalculated && decile !== null && percentile !== null && parsedWealth !== null"
      class="calc__results"
      aria-live="polite"
      aria-label="Your wealth position"
    >
      <hr class="wl-rule-red" />

      <!-- Position headline -->
      <div class="calc__position">
        <p class="wl-eyebrow">Your position</p>
        <p class="calc__position-headline">
          You are in the
          <span class="calc__decile-num">{{ decileOrdinal }}</span>
          decile
        </p>
        <p class="calc__position-sub">
          Wealthier than approximately
          <span class="wl-num">{{ percentile }}%</span>
          of UK households
        </p>
      </div>

      <!-- Decile bar visualisation -->
      <div
        class="calc__bar"
        role="img"
        :aria-label="`Decile bar chart showing your position in the ${decileOrdinal} decile out of 10`"
      >
        <div class="calc__bar-track">
          <div
            v-for="d in DECILE_DATA"
            :key="d.decile"
            :class="[
              'calc__bar-block',
              { 'calc__bar-block--active': d.decile === decile },
            ]"
            :aria-label="`Decile ${d.decile}: ${d.rangeLabel}${d.decile === decile ? ' (your position)' : ''}`"
          >
            <span class="calc__bar-label">{{ d.decile }}</span>
            <span
              v-if="d.decile === decile"
              class="calc__bar-marker"
              aria-hidden="true"
            >
              &#9660;
            </span>
          </div>
        </div>
        <div class="calc__bar-ranges">
          <div
            v-for="d in DECILE_DATA"
            :key="`range-${d.decile}`"
            :class="[
              'calc__bar-range',
              { 'calc__bar-range--active': d.decile === decile },
            ]"
          >
            {{ d.rangeLabel }}
          </div>
        </div>
        <div class="calc__bar-legend">
          <span>Least wealthy</span>
          <span>Most wealthy</span>
        </div>
      </div>

      <!-- Comparison stats -->
      <div class="calc__comparisons">
        <h2 class="calc__comparisons-heading">How you compare</h2>
        <div class="calc__stat-grid">
          <div class="calc__stat">
            <span class="calc__stat-label">Your net wealth</span>
            <span class="calc__stat-value wl-num">
              {{ formatGBP(parsedWealth) }}
            </span>
          </div>
          <div class="calc__stat">
            <span class="calc__stat-label">Median UK household</span>
            <span class="calc__stat-value wl-num">
              {{ formatGBP(COMPARISON_STATS.medianUK) }}
            </span>
          </div>
          <div class="calc__stat">
            <span class="calc__stat-label">Bottom 50% median</span>
            <span class="calc__stat-value wl-num">
              ~{{ formatGBP(COMPARISON_STATS.medianBottom50) }}
            </span>
          </div>
          <div class="calc__stat">
            <span class="calc__stat-label">Top 10% threshold</span>
            <span class="calc__stat-value wl-num">
              {{ formatGBP(COMPARISON_STATS.top10Threshold) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Context message -->
      <div class="calc__context">
        <p class="calc__context-text">{{ contextMessage }}</p>
      </div>

      <!-- Source citation -->
      <div class="calc__source">
        <span class="wl-source">
          {{ COMPARISON_STATS.source }}
        </span>
        <p class="calc__source-detail">
          <a
            :href="COMPARISON_STATS.sourceUrl"
            target="_blank"
            rel="noopener"
          >
            View source data on ONS
          </a>
          &middot; Accessed {{ COMPARISON_STATS.accessed }}
        </p>
      </div>

      <!-- Reset -->
      <button class="wl-btn wl-btn--ghost calc__reset" @click="reset">
        Try another amount
      </button>
    </section>
  </div>
</template>

<style scoped>
/* ============================================================ */
/* CALCULATOR LAYOUT                                             */
/* ============================================================ */
.calc {
  max-width: 860px;
  margin: 0 auto;
  padding: 48px 32px 96px;
}

/* ============================================================ */
/* HEADER                                                        */
/* ============================================================ */
.calc__header {
  margin-bottom: 40px;
  border-bottom: 2px solid var(--wl-ink);
  padding-bottom: 32px;
}

.calc__title {
  font-family: var(--wl-serif);
  font-size: clamp(36px, 6vw, 64px);
  font-weight: 600;
  line-height: 1;
  letter-spacing: -0.025em;
  color: var(--wl-ink);
  margin: 12px 0 20px;
}
.calc__title em {
  font-style: italic;
  color: var(--wl-red);
  font-weight: 500;
}

.calc__lede {
  font-size: 18px;
  line-height: 1.6;
  color: var(--wl-ink-body);
  max-width: 56ch;
  margin: 0 0 12px;
}

.calc__privacy {
  font-family: var(--wl-mono);
  font-size: 11px;
  color: var(--wl-ink-faint);
  letter-spacing: 0.04em;
  margin: 0;
}

/* ============================================================ */
/* INPUT SECTION                                                 */
/* ============================================================ */
.calc__input-section {
  margin-bottom: 40px;
}

.calc__label {
  display: block;
  font-family: var(--wl-serif);
  font-size: 22px;
  font-weight: 600;
  color: var(--wl-ink);
  margin-bottom: 8px;
}

.calc__help {
  font-size: 14px;
  color: var(--wl-ink-muted);
  margin: 0 0 16px;
  max-width: 56ch;
  line-height: 1.5;
}
.calc__help strong {
  color: var(--wl-ink);
  font-weight: 600;
}

.calc__input-row {
  display: flex;
  align-items: stretch;
  gap: 0;
  max-width: 480px;
}

.calc__currency {
  display: flex;
  align-items: center;
  padding: 0 14px;
  background: var(--wl-paper-tint);
  border: 1px solid var(--wl-ink);
  border-right: none;
  font-family: var(--wl-mono);
  font-size: 18px;
  color: var(--wl-ink);
  border-radius: var(--wl-radius) 0 0 var(--wl-radius);
}

.calc__input {
  flex: 1;
  min-width: 0;
  padding: 12px 16px;
  font-family: var(--wl-mono);
  font-size: 18px;
  font-variant-numeric: tabular-nums;
  color: var(--wl-ink);
  background: var(--wl-card);
  border: 1px solid var(--wl-ink);
  border-left: none;
  border-right: none;
  outline: none;
}
.calc__input:focus {
  box-shadow: inset 0 0 0 2px var(--wl-red);
}
.calc__input::placeholder {
  color: var(--wl-ink-faint);
}

.calc__btn {
  border-radius: 0 var(--wl-radius) var(--wl-radius) 0;
  white-space: nowrap;
}
.calc__btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.calc__error {
  color: var(--wl-red);
  font-size: 13px;
  margin: 8px 0 0;
}

/* ============================================================ */
/* PRESETS                                                       */
/* ============================================================ */
.calc__presets {
  margin-top: 20px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.calc__presets-label {
  font-family: var(--wl-mono);
  font-size: 11px;
  color: var(--wl-ink-muted);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  margin: 0;
}

/* ============================================================ */
/* RESULTS                                                       */
/* ============================================================ */
.calc__results {
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

/* ============================================================ */
/* POSITION HEADLINE                                             */
/* ============================================================ */
.calc__position {
  text-align: center;
  padding: 36px 0 32px;
}

.calc__position-headline {
  font-family: var(--wl-serif);
  font-size: clamp(28px, 4vw, 42px);
  font-weight: 600;
  color: var(--wl-ink);
  margin: 12px 0 8px;
  line-height: 1.15;
}

.calc__decile-num {
  color: var(--wl-red);
  font-weight: 700;
}

.calc__position-sub {
  font-size: 18px;
  color: var(--wl-ink-body);
  margin: 0;
}
.calc__position-sub .wl-num {
  color: var(--wl-red);
  font-weight: 600;
  font-size: 20px;
}

/* ============================================================ */
/* DECILE BAR VISUALISATION                                      */
/* ============================================================ */
.calc__bar {
  margin: 32px 0;
  padding: 24px;
  background: var(--wl-card);
  border: 1px solid var(--wl-ink);
}

.calc__bar-track {
  display: flex;
  gap: 2px;
}

.calc__bar-block {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  padding: 14px 2px 10px;
  background: var(--wl-paper-tint);
  border: 1px solid var(--wl-rule);
  transition: background 0.2s ease, border-color 0.2s ease;
}

/* Gradient from light (decile 1) to darker (decile 10) */
.calc__bar-block:nth-child(1) { background: var(--wl-paper); }
.calc__bar-block:nth-child(2) { background: color-mix(in srgb, var(--wl-paper) 90%, var(--wl-ink)); }
.calc__bar-block:nth-child(3) { background: color-mix(in srgb, var(--wl-paper) 82%, var(--wl-ink)); }
.calc__bar-block:nth-child(4) { background: color-mix(in srgb, var(--wl-paper) 74%, var(--wl-ink)); }
.calc__bar-block:nth-child(5) { background: color-mix(in srgb, var(--wl-paper) 66%, var(--wl-ink)); }
.calc__bar-block:nth-child(6) { background: color-mix(in srgb, var(--wl-paper) 58%, var(--wl-ink)); }
.calc__bar-block:nth-child(7) { background: color-mix(in srgb, var(--wl-paper) 50%, var(--wl-ink)); }
.calc__bar-block:nth-child(8) { background: color-mix(in srgb, var(--wl-paper) 42%, var(--wl-ink)); }
.calc__bar-block:nth-child(9) { background: color-mix(in srgb, var(--wl-paper) 34%, var(--wl-ink)); }
.calc__bar-block:nth-child(10) { background: color-mix(in srgb, var(--wl-paper) 26%, var(--wl-ink)); }

/* Active decile highlighted in red */
.calc__bar-block--active {
  background: var(--wl-red) !important;
  border-color: var(--wl-red-deep);
  color: #fff;
}

.calc__bar-label {
  font-family: var(--wl-mono);
  font-size: 12px;
  font-weight: 600;
  color: var(--wl-ink-muted);
}
.calc__bar-block:nth-child(n+6) .calc__bar-label {
  color: var(--wl-paper);
}
.calc__bar-block--active .calc__bar-label {
  color: #fff;
}

.calc__bar-marker {
  position: absolute;
  top: -16px;
  font-size: 14px;
  color: var(--wl-red);
  line-height: 1;
}

/* Range labels beneath bars */
.calc__bar-ranges {
  display: flex;
  gap: 2px;
  margin-top: 4px;
}

.calc__bar-range {
  flex: 1;
  font-family: var(--wl-mono);
  font-size: 9px;
  color: var(--wl-ink-faint);
  text-align: center;
  line-height: 1.3;
  padding: 4px 1px;
  overflow: hidden;
  text-overflow: ellipsis;
}
.calc__bar-range--active {
  color: var(--wl-red);
  font-weight: 600;
}

.calc__bar-legend {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-family: var(--wl-mono);
  font-size: 10px;
  color: var(--wl-ink-muted);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

/* ============================================================ */
/* COMPARISON STATS                                              */
/* ============================================================ */
.calc__comparisons {
  margin: 32px 0;
}

.calc__comparisons-heading {
  font-family: var(--wl-serif);
  font-size: 24px;
  font-weight: 600;
  color: var(--wl-ink);
  margin: 0 0 16px;
}

.calc__stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1px;
  background: var(--wl-rule);
  border: 1px solid var(--wl-ink);
}

.calc__stat {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 16px 20px;
  background: var(--wl-card);
}

.calc__stat-label {
  font-family: var(--wl-mono);
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--wl-ink-muted);
}

.calc__stat-value {
  font-size: 22px;
  font-weight: 600;
  color: var(--wl-ink);
}

/* ============================================================ */
/* CONTEXT MESSAGE                                               */
/* ============================================================ */
.calc__context {
  margin: 28px 0;
  padding: 24px 28px;
  border-top: 4px solid var(--wl-red);
  border-bottom: 1px solid var(--wl-rule);
  background: var(--wl-paper-tint);
}

.calc__context-text {
  font-family: var(--wl-serif);
  font-size: 18px;
  line-height: 1.6;
  color: var(--wl-ink);
  margin: 0;
  font-style: italic;
}

/* ============================================================ */
/* SOURCE CITATION                                               */
/* ============================================================ */
.calc__source {
  margin: 24px 0;
}

.calc__source-detail {
  font-family: var(--wl-mono);
  font-size: 11px;
  color: var(--wl-ink-muted);
  margin: 8px 0 0;
}
.calc__source-detail a {
  color: var(--wl-red);
  text-decoration: none;
  border-bottom: 1px solid var(--wl-red);
}
.calc__source-detail a:hover {
  text-decoration: none;
  border-bottom-width: 2px;
}
.calc__source-detail a:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: 2px;
}

/* ============================================================ */
/* RESET BUTTON                                                  */
/* ============================================================ */
.calc__reset {
  margin-top: 16px;
}

/* ============================================================ */
/* RESPONSIVE                                                    */
/* ============================================================ */
@media (max-width: 768px) {
  .calc {
    padding: 32px 16px 64px;
  }

  .calc__input-row {
    flex-direction: column;
    max-width: 100%;
  }

  .calc__currency {
    border-right: 1px solid var(--wl-ink);
    border-bottom: none;
    border-radius: var(--wl-radius) var(--wl-radius) 0 0;
    justify-content: center;
    padding: 8px;
  }

  .calc__input {
    border-left: 1px solid var(--wl-ink);
    border-right: 1px solid var(--wl-ink);
  }

  .calc__btn {
    border-radius: 0 0 var(--wl-radius) var(--wl-radius);
    height: 48px;
  }

  .calc__bar-ranges {
    display: none;
  }

  .calc__stat-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 480px) {
  .calc__stat-grid {
    grid-template-columns: 1fr;
  }

  .calc__presets {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
