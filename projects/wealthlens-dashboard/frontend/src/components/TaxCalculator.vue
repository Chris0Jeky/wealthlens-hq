<script setup lang="ts">
/**
 * TaxCalculator — "What's Your Real Tax Rate?"
 *
 * Interactive calculator showing effective income tax + NI rates,
 * with a comparison to capital gains tax to highlight the disparity
 * between how earned income and investment gains are taxed in the UK.
 *
 * Source: HMRC Income Tax rates and National Insurance rates 2024-25
 * URL: https://www.gov.uk/income-tax-rates
 * Accessed: 2026-05-16
 */
import { ref, computed } from "vue";
import {
  calculateEffectiveRate,
  formatPercent,
  type EffectiveRates,
} from "@/utils/taxCalculator";

const salaryInput = ref("");
const hasCalculated = ref(false);

const parsedSalary = computed(() => {
  const cleaned = salaryInput.value.replace(/[£,\s]/g, "");
  if (cleaned === "") return null;
  const num = Number(cleaned);
  return Number.isFinite(num) && num >= 0 ? num : null;
});

const isValid = computed(() => parsedSalary.value !== null);

const results = computed((): EffectiveRates | null => {
  if (!hasCalculated.value || parsedSalary.value === null) return null;
  return calculateEffectiveRate(parsedSalary.value);
});

function applyPreset(value: number) {
  salaryInput.value = value.toLocaleString("en-GB");
  hasCalculated.value = false;
}

function calculate() {
  if (isValid.value) {
    hasCalculated.value = true;
  }
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === "Enter") {
    calculate();
  }
}

function reset() {
  salaryInput.value = "";
  hasCalculated.value = false;
}

function formatGBP(value: number): string {
  const abs = Math.abs(value);
  const formatted = abs.toLocaleString("en-GB", { maximumFractionDigits: 0 });
  return `${value < 0 ? "-" : ""}£${formatted}`;
}
</script>

<template>
  <div class="calc">
    <!-- Header -->
    <header class="calc__header">
      <p class="wl-eyebrow">Interactive tool</p>
      <h1 class="calc__title">
        What's your real
        <em>tax rate?</em>
      </h1>
      <p class="calc__lede">
        Enter your annual gross salary to see your effective income tax and
        National Insurance rates — and how they compare to capital gains tax
        rates paid on investment profits.
      </p>
      <p class="calc__privacy">
        All calculation happens in your browser. No data is stored or
        transmitted.
      </p>
    </header>

    <!-- Input section -->
    <section class="calc__input-section" aria-label="Salary input">
      <label for="salary-input" class="calc__label">
        Your annual gross salary
      </label>
      <p id="salary-input-help" class="calc__help">
        Enter your total annual salary before tax. This calculates
        <strong>employee</strong> income tax and Class 1 National Insurance.
      </p>

      <div class="calc__input-row">
        <span class="calc__currency" aria-hidden="true">&pound;</span>
        <input
          id="salary-input"
          v-model="salaryInput"
          type="text"
          inputmode="numeric"
          class="calc__input"
          placeholder="e.g. 50,000"
          aria-describedby="salary-input-help"
          :aria-invalid="salaryInput.length > 0 && !isValid ? 'true' : undefined"
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
        v-if="salaryInput.length > 0 && !isValid"
        class="calc__error"
        role="alert"
      >
        Please enter a valid positive number.
      </p>

      <!-- Quick presets -->
      <div class="calc__presets" role="group" aria-label="Salary presets">
        <p class="calc__presets-label">Quick estimates:</p>
        <button
          class="wl-btn wl-btn--ghost wl-btn--sm"
          @click="applyPreset(25_000)"
        >
          &pound;25,000
        </button>
        <button
          class="wl-btn wl-btn--ghost wl-btn--sm"
          @click="applyPreset(50_000)"
        >
          &pound;50,000
        </button>
        <button
          class="wl-btn wl-btn--ghost wl-btn--sm"
          @click="applyPreset(80_000)"
        >
          &pound;80,000
        </button>
        <button
          class="wl-btn wl-btn--ghost wl-btn--sm"
          @click="applyPreset(150_000)"
        >
          &pound;150,000
        </button>
      </div>
    </section>

    <!-- Results section -->
    <section
      v-if="results"
      class="calc__results"
      aria-live="polite"
      aria-label="Tax calculation results"
    >
      <hr class="wl-rule-red" />

      <!-- Headline rates -->
      <div class="calc__position">
        <p class="wl-eyebrow">Your effective rates</p>
        <div class="calc__rates-row">
          <div class="calc__rate-card">
            <span class="calc__rate-label">Income Tax</span>
            <span class="calc__rate-value wl-num">
              {{ formatPercent(results.incomeTax.effectiveRate) }}
            </span>
          </div>
          <div class="calc__rate-card">
            <span class="calc__rate-label">Combined (Tax + NI)</span>
            <span class="calc__rate-value calc__rate-value--primary wl-num">
              {{ formatPercent(results.combinedRate) }}
            </span>
          </div>
          <div class="calc__rate-card">
            <span class="calc__rate-label">Take-home pay</span>
            <span class="calc__rate-value wl-num">
              {{ formatGBP(results.takeHomePay) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Tax breakdown table -->
      <div class="calc__breakdown">
        <h2 class="calc__breakdown-heading">Income tax breakdown</h2>
        <div class="calc__table-wrap" role="region" aria-label="Income tax bands table" tabindex="0">
          <table class="calc__table">
            <thead>
              <tr>
                <th scope="col">Band</th>
                <th scope="col">Rate</th>
                <th scope="col">Taxable amount</th>
                <th scope="col">Tax paid</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="band in results.incomeTax.bands" :key="band.name">
                <td>{{ band.name }}</td>
                <td class="wl-num">{{ formatPercent(band.rate) }}</td>
                <td class="wl-num">{{ formatGBP(band.to - band.from) }}</td>
                <td class="wl-num">{{ formatGBP(band.taxPaid) }}</td>
              </tr>
            </tbody>
            <tfoot>
              <tr>
                <td colspan="3"><strong>Total income tax</strong></td>
                <td class="wl-num"><strong>{{ formatGBP(results.incomeTax.totalTax) }}</strong></td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>

      <!-- NI breakdown -->
      <div class="calc__breakdown">
        <h2 class="calc__breakdown-heading">National Insurance breakdown</h2>
        <div class="calc__table-wrap" role="region" aria-label="National Insurance bands table" tabindex="0">
          <table class="calc__table">
            <thead>
              <tr>
                <th scope="col">Band</th>
                <th scope="col">Rate</th>
                <th scope="col">Earnings in band</th>
                <th scope="col">NI paid</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="band in results.nationalInsurance.bands" :key="band.name">
                <td>{{ band.name }}</td>
                <td class="wl-num">{{ formatPercent(band.rate) }}</td>
                <td class="wl-num">{{ formatGBP(band.to - band.from) }}</td>
                <td class="wl-num">{{ formatGBP(band.niPaid) }}</td>
              </tr>
            </tbody>
            <tfoot>
              <tr>
                <td colspan="3"><strong>Total National Insurance</strong></td>
                <td class="wl-num"><strong>{{ formatGBP(results.nationalInsurance.totalNI) }}</strong></td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>

      <!-- Capital gains comparison -->
      <div class="calc__comparison">
        <h2 class="calc__comparison-heading">The income vs. capital gains gap</h2>
        <div class="calc__comparison-card">
          <p class="calc__comparison-text">
            If this {{ formatGBP(parsedSalary ?? 0) }} were received as
            <strong>capital gains</strong> instead of earned income, you'd pay
            an effective rate of just
            <span class="calc__comparison-rate wl-num">
              {{ formatPercent(results.capitalGainsComparison.effectiveRate) }}
            </span>
            — compared to your combined income tax + NI rate of
            <span class="calc__comparison-rate wl-num">
              {{ formatPercent(results.combinedRate) }}
            </span>.
          </p>
          <p class="calc__comparison-note">
            Capital gains tax (2024-25): 10% basic rate / 20% higher rate,
            with a £3,000 annual exempt amount. This comparison uses general
            asset rates (not residential property).
          </p>
        </div>
      </div>

      <!-- Source citation -->
      <div class="calc__source">
        <span class="wl-source">
          HMRC Income Tax rates, National Insurance rates, and Capital Gains
          Tax rates for the 2024-25 tax year.
        </span>
        <p class="calc__source-detail">
          <a
            href="https://www.gov.uk/income-tax-rates"
            target="_blank"
            rel="noopener"
          >
            Income Tax rates
          </a>
          &middot;
          <a
            href="https://www.gov.uk/national-insurance-rates-letters"
            target="_blank"
            rel="noopener"
          >
            NI rates
          </a>
          &middot;
          <a
            href="https://www.gov.uk/capital-gains-tax/rates"
            target="_blank"
            rel="noopener"
          >
            CGT rates
          </a>
          &middot; Accessed 2026-05-16
        </p>
      </div>

      <!-- Reset -->
      <button class="wl-btn wl-btn--ghost calc__reset" @click="reset">
        Try another salary
      </button>
    </section>
  </div>
</template>

<style scoped>
.calc {
  max-width: 860px;
  margin: 0 auto;
  padding: 48px 32px 96px;
}

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

.calc__position {
  text-align: center;
  padding: 36px 0 32px;
}

.calc__rates-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1px;
  background: var(--wl-rule);
  border: 1px solid var(--wl-ink);
  margin-top: 24px;
}

.calc__rate-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 20px 24px;
  background: var(--wl-card);
  text-align: center;
}

.calc__rate-label {
  font-family: var(--wl-mono);
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--wl-ink-muted);
}

.calc__rate-value {
  font-size: 28px;
  font-weight: 600;
  color: var(--wl-ink);
}

.calc__rate-value--primary {
  color: var(--wl-red);
  font-size: 36px;
}

.calc__breakdown {
  margin: 32px 0;
}

.calc__breakdown-heading {
  font-family: var(--wl-serif);
  font-size: 22px;
  font-weight: 600;
  color: var(--wl-ink);
  margin: 0 0 16px;
}

.calc__table-wrap {
  overflow-x: auto;
  border: 1px solid var(--wl-ink);
}

.calc__table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.calc__table th {
  font-family: var(--wl-mono);
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--wl-ink-muted);
  text-align: left;
  padding: 12px 16px;
  border-bottom: 1px solid var(--wl-ink);
  background: var(--wl-bg-muted);
}

.calc__table td {
  padding: 10px 16px;
  border-bottom: 1px solid var(--wl-rule);
  color: var(--wl-ink);
}

.calc__table tfoot td {
  border-bottom: none;
  border-top: 2px solid var(--wl-ink);
  padding: 12px 16px;
}

.calc__comparison {
  margin: 40px 0;
}

.calc__comparison-heading {
  font-family: var(--wl-serif);
  font-size: 22px;
  font-weight: 600;
  color: var(--wl-ink);
  margin: 0 0 16px;
}

.calc__comparison-card {
  padding: 24px 28px;
  border-top: 4px solid var(--wl-red);
  border-bottom: 1px solid var(--wl-rule);
  background: var(--wl-paper-tint);
}

.calc__comparison-text {
  font-family: var(--wl-serif);
  font-size: 18px;
  line-height: 1.6;
  color: var(--wl-ink);
  margin: 0 0 12px;
}

.calc__comparison-rate {
  color: var(--wl-red);
  font-weight: 700;
  font-size: 20px;
}

.calc__comparison-note {
  font-family: var(--wl-mono);
  font-size: 11px;
  color: var(--wl-ink-muted);
  margin: 0;
  line-height: 1.5;
}

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
  border-bottom-width: 2px;
}
.calc__source-detail a:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: 2px;
}

.calc__reset {
  margin-top: 16px;
}

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

  .calc__rates-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .calc__presets {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
