<script setup lang="ts">
/**
 * TaxRateCalculator — "Compare Your Effective Tax Rate to a Billionaire"
 *
 * Interactive calculator that shows how much tax a UK employee pays
 * on their salary vs how much a billionaire pays on their wealth gains.
 * The key insight: unrealised gains (the majority of billionaire wealth
 * growth) are taxed at 0%.
 *
 * All calculation is client-side. No personal data is stored or transmitted.
 *
 * Source: HMRC Income Tax rates and allowances 2024-25
 * URL: https://www.gov.uk/income-tax-rates
 * Accessed: 2026-05-16
 */
import { ref, computed } from "vue";
import {
  calculateEmployeeTax,
  calculateBillionaireTax,
  formatPercentage,
  formatGBP,
  TAX_SOURCE,
} from "@/utils/taxCalculator";

/** Default billionaire gain for comparison (£1 billion) */
const BILLIONAIRE_GAIN = 1_000_000_000;

/** Raw text input from the user */
const salaryInput = ref("");

/** Whether the user has triggered a calculation */
const hasCalculated = ref(false);

/** Parse the input, stripping £, commas, and whitespace */
const parsedSalary = computed(() => {
  const cleaned = salaryInput.value.replace(/[£,\s]/g, "");
  const num = Number(cleaned);
  return Number.isFinite(num) && num > 0 ? num : null;
});

/** Whether the current input is valid */
const isValid = computed(() => parsedSalary.value !== null);

/** Employee tax result */
const employeeResult = computed(() =>
  parsedSalary.value !== null
    ? calculateEmployeeTax(parsedSalary.value)
    : null,
);

/** Billionaire tax result */
const billionaireResult = computed(() =>
  calculateBillionaireTax(BILLIONAIRE_GAIN),
);

/**
 * Multiplier showing how many times more the employee's effective
 * rate is compared to the billionaire's.
 */
const rateMultiplier = computed(() => {
  if (!employeeResult.value || billionaireResult.value.effectiveRate === 0) {
    return null;
  }
  return employeeResult.value.effectiveRate / billionaireResult.value.effectiveRate;
});

/**
 * Maximum bar width percentage — the larger of the two effective rates
 * is shown at 100% width, the other proportionally.
 */
const maxRate = computed(() => {
  if (!employeeResult.value) return 1;
  return Math.max(
    employeeResult.value.effectiveRate,
    billionaireResult.value.effectiveRate,
  );
});

/** Apply a preset value to the input */
function applyPreset(value: number) {
  salaryInput.value = value.toLocaleString("en-GB");
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
  salaryInput.value = "";
  hasCalculated.value = false;
}

/** Format bar width as a percentage of the max rate */
function barWidth(rate: number): string {
  if (maxRate.value === 0) return "0%";
  return `${Math.max(2, (rate / maxRate.value) * 100)}%`;
}
</script>

<template>
  <div class="tax">
    <!-- Header -->
    <header class="tax__header">
      <p class="wl-eyebrow">Interactive tool</p>
      <h1 class="tax__title">
        Compare your tax rate
        <em>to a billionaire&rsquo;s</em>
      </h1>
      <p class="tax__lede">
        Enter your annual salary and see how your effective tax rate compares
        to a billionaire whose wealth grows by &pound;1&nbsp;billion. The
        result may surprise you.
      </p>
      <p class="tax__privacy">
        All calculation happens in your browser. No data is stored or
        transmitted.
      </p>
    </header>

    <!-- Input section -->
    <section class="tax__input-section" aria-label="Salary input">
      <label for="salary-input" class="tax__label">
        Your annual gross salary
      </label>
      <p id="salary-input-help" class="tax__help">
        Enter your gross (before tax) annual salary. We calculate
        <strong>Income Tax</strong> and <strong>employee NICs</strong> using
        HMRC 2024-25 rates for the rest of the UK (not Scotland).
      </p>

      <div class="tax__input-row">
        <span class="tax__currency" aria-hidden="true">&pound;</span>
        <input
          id="salary-input"
          v-model="salaryInput"
          type="text"
          inputmode="numeric"
          class="tax__input"
          placeholder="e.g. 35,000"
          aria-describedby="salary-input-help"
          :aria-invalid="salaryInput.length > 0 && !isValid ? 'true' : undefined"
          @keydown="onKeydown"
        />
        <button
          class="wl-btn wl-btn--red tax__btn"
          :disabled="!isValid"
          @click="calculate"
        >
          Calculate
        </button>
      </div>

      <p
        v-if="salaryInput.length > 0 && !isValid"
        class="tax__error"
        role="alert"
      >
        Please enter a valid positive salary.
      </p>

      <!-- Quick presets -->
      <div class="tax__presets" role="group" aria-label="Salary presets">
        <p class="tax__presets-label">Quick examples:</p>
        <button
          class="wl-btn wl-btn--ghost wl-btn--sm"
          @click="applyPreset(30_000)"
        >
          &pound;30k
        </button>
        <button
          class="wl-btn wl-btn--ghost wl-btn--sm"
          @click="applyPreset(50_000)"
        >
          &pound;50k
        </button>
        <button
          class="wl-btn wl-btn--ghost wl-btn--sm"
          @click="applyPreset(80_000)"
        >
          &pound;80k
        </button>
        <button
          class="wl-btn wl-btn--ghost wl-btn--sm"
          @click="applyPreset(125_000)"
        >
          &pound;125k
        </button>
      </div>
    </section>

    <!-- Results section -->
    <section
      v-if="hasCalculated && employeeResult"
      class="tax__results"
      aria-live="polite"
      aria-label="Tax comparison results"
    >
      <hr class="wl-rule-red" />

      <!-- Your Tax Breakdown -->
      <div class="tax__breakdown">
        <h2 class="tax__section-heading">Your tax breakdown</h2>
        <p class="tax__section-sub">
          On a salary of
          <span class="wl-num">{{ formatGBP(employeeResult.salary) }}</span>
        </p>

        <div class="tax__stat-grid">
          <div class="tax__stat">
            <span class="tax__stat-label">Income Tax</span>
            <span class="tax__stat-value wl-num">
              {{ formatGBP(employeeResult.incomeTax) }}
            </span>
          </div>
          <div class="tax__stat">
            <span class="tax__stat-label">Employee NICs</span>
            <span class="tax__stat-value wl-num">
              {{ formatGBP(employeeResult.nics) }}
            </span>
          </div>
          <div class="tax__stat tax__stat--highlight">
            <span class="tax__stat-label">Total Tax</span>
            <span class="tax__stat-value wl-num">
              {{ formatGBP(employeeResult.totalTax) }}
            </span>
          </div>
          <div class="tax__stat tax__stat--highlight">
            <span class="tax__stat-label">Your effective rate</span>
            <span class="tax__stat-value wl-num">
              {{ formatPercentage(employeeResult.effectiveRate) }}
            </span>
          </div>
        </div>

        <!-- Band breakdown -->
        <details class="tax__band-details">
          <summary class="tax__band-summary">
            See band-by-band breakdown
          </summary>
          <table class="tax__band-table" aria-label="Income tax bands">
            <thead>
              <tr>
                <th scope="col">Band</th>
                <th scope="col" class="wl-num">Taxable</th>
                <th scope="col" class="wl-num">Rate</th>
                <th scope="col" class="wl-num">Tax</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="band in employeeResult.bands" :key="band.name">
                <td>{{ band.name }}</td>
                <td class="wl-num">{{ formatGBP(band.taxableAmount) }}</td>
                <td class="wl-num">{{ formatPercentage(band.rate) }}</td>
                <td class="wl-num">{{ formatGBP(band.tax) }}</td>
              </tr>
            </tbody>
          </table>
        </details>
      </div>

      <!-- Billionaire Comparison -->
      <div class="tax__breakdown">
        <h2 class="tax__section-heading">Billionaire comparison</h2>
        <p class="tax__section-sub">
          On &pound;1bn of wealth gains (assumes
          <span class="wl-num">{{ formatPercentage(billionaireResult.realisationRate) }}</span>
          realised)
        </p>

        <div class="tax__stat-grid">
          <div class="tax__stat">
            <span class="tax__stat-label">Realised gains</span>
            <span class="tax__stat-value wl-num">
              {{ formatGBP(billionaireResult.realisedGains) }}
            </span>
          </div>
          <div class="tax__stat">
            <span class="tax__stat-label">Unrealised gains (0% tax)</span>
            <span class="tax__stat-value wl-num">
              {{ formatGBP(billionaireResult.unrealisedGains) }}
            </span>
          </div>
          <div class="tax__stat">
            <span class="tax__stat-label">CGT paid (20%)</span>
            <span class="tax__stat-value wl-num">
              {{ formatGBP(billionaireResult.cgtPaid) }}
            </span>
          </div>
          <div class="tax__stat tax__stat--highlight">
            <span class="tax__stat-label">Effective rate on all gains</span>
            <span class="tax__stat-value wl-num">
              {{ formatPercentage(billionaireResult.effectiveRate) }}
            </span>
          </div>
        </div>

        <p class="tax__assumption">
          <strong>Assumption:</strong> Only 20% of a billionaire&rsquo;s
          wealth gains are realised (sold) in a given year. The remaining
          80% grows as unrealised gains, taxed at 0% under current UK law.
          The actual proportion varies, but the structural advantage is real.
        </p>
      </div>

      <!-- The Comparison — side-by-side bars -->
      <div class="tax__comparison">
        <h2 class="tax__section-heading">The comparison</h2>

        <div class="tax__bars" role="img" :aria-label="`Your effective tax rate of ${formatPercentage(employeeResult.effectiveRate)} compared to a billionaire's effective rate of ${formatPercentage(billionaireResult.effectiveRate)}`">
          <!-- Your rate bar -->
          <div class="tax__bar-row">
            <span class="tax__bar-label">You</span>
            <div class="tax__bar-track">
              <div
                class="tax__bar-fill tax__bar-fill--you"
                :style="{ width: barWidth(employeeResult.effectiveRate) }"
              >
                <span class="tax__bar-value wl-num">
                  {{ formatPercentage(employeeResult.effectiveRate) }}
                </span>
              </div>
            </div>
          </div>

          <!-- Billionaire rate bar -->
          <div class="tax__bar-row">
            <span class="tax__bar-label">Billionaire</span>
            <div class="tax__bar-track">
              <div
                class="tax__bar-fill tax__bar-fill--billionaire"
                :style="{ width: barWidth(billionaireResult.effectiveRate) }"
              >
                <span class="tax__bar-value wl-num">
                  {{ formatPercentage(billionaireResult.effectiveRate) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Key Insight -->
      <div class="tax__insight">
        <p class="wl-eyebrow">Key insight</p>
        <p class="tax__insight-text">
          You pay
          <strong class="tax__insight-rate">{{ formatPercentage(employeeResult.effectiveRate) }}</strong>
          effective tax on your salary. A billionaire pays approximately
          <strong class="tax__insight-rate">{{ formatPercentage(billionaireResult.effectiveRate) }}</strong>
          effective tax on their wealth gains.
          <template v-if="rateMultiplier !== null && rateMultiplier > 1">
            That means you pay
            <strong class="tax__insight-rate">{{ rateMultiplier.toFixed(1) }}x</strong>
            the effective rate.
          </template>
        </p>
        <p class="tax__insight-why">
          The difference exists because most billionaire wealth grows through
          rising share prices — gains that are only taxed when sold. Under
          current UK tax law, unrealised gains are taxed at 0%, no matter
          how large they are.
        </p>
      </div>

      <!-- Source citation -->
      <div class="tax__source">
        <span class="wl-source">
          {{ TAX_SOURCE.name }}
        </span>
        <p class="tax__source-detail">
          <a :href="TAX_SOURCE.url" target="_blank" rel="noopener">
            Income Tax rates
          </a>
          &middot;
          <a :href="TAX_SOURCE.nicUrl" target="_blank" rel="noopener">
            NIC rates
          </a>
          &middot;
          <a :href="TAX_SOURCE.cgtUrl" target="_blank" rel="noopener">
            CGT rates
          </a>
          &middot; Accessed {{ TAX_SOURCE.accessed }}
        </p>
      </div>

      <!-- Reset -->
      <button class="wl-btn wl-btn--ghost tax__reset" @click="reset">
        Try another salary
      </button>
    </section>
  </div>
</template>

<style scoped>
/* ============================================================ */
/* CALCULATOR LAYOUT                                             */
/* ============================================================ */
.tax {
  max-width: 860px;
  margin: 0 auto;
  padding: 48px 32px 96px;
}

/* ============================================================ */
/* HEADER                                                        */
/* ============================================================ */
.tax__header {
  margin-bottom: 40px;
  border-bottom: 2px solid var(--wl-ink);
  padding-bottom: 32px;
}

.tax__title {
  font-family: var(--wl-serif);
  font-size: clamp(32px, 5vw, 56px);
  font-weight: 600;
  line-height: 1.05;
  letter-spacing: -0.025em;
  color: var(--wl-ink);
  margin: 12px 0 20px;
}
.tax__title em {
  font-style: italic;
  color: var(--wl-red);
  font-weight: 500;
}

.tax__lede {
  font-size: 18px;
  line-height: 1.6;
  color: var(--wl-ink-body);
  max-width: 56ch;
  margin: 0 0 12px;
}

.tax__privacy {
  font-family: var(--wl-mono);
  font-size: 11px;
  color: var(--wl-ink-faint);
  letter-spacing: 0.04em;
  margin: 0;
}

/* ============================================================ */
/* INPUT SECTION                                                 */
/* ============================================================ */
.tax__input-section {
  margin-bottom: 40px;
}

.tax__label {
  display: block;
  font-family: var(--wl-serif);
  font-size: 22px;
  font-weight: 600;
  color: var(--wl-ink);
  margin-bottom: 8px;
}

.tax__help {
  font-size: 14px;
  color: var(--wl-ink-muted);
  margin: 0 0 16px;
  max-width: 56ch;
  line-height: 1.5;
}
.tax__help strong {
  color: var(--wl-ink);
  font-weight: 600;
}

.tax__input-row {
  display: flex;
  align-items: stretch;
  gap: 0;
  max-width: 480px;
}

.tax__currency {
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

.tax__input {
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
.tax__input:focus {
  box-shadow: inset 0 0 0 2px var(--wl-red);
}
.tax__input::placeholder {
  color: var(--wl-ink-faint);
}

.tax__btn {
  border-radius: 0 var(--wl-radius) var(--wl-radius) 0;
  white-space: nowrap;
}
.tax__btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.tax__error {
  color: var(--wl-red);
  font-size: 13px;
  margin: 8px 0 0;
}

/* ============================================================ */
/* PRESETS                                                       */
/* ============================================================ */
.tax__presets {
  margin-top: 20px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.tax__presets-label {
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
.tax__results {
  animation: taxFadeIn 0.3s ease-out;
}

@keyframes taxFadeIn {
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
/* TAX BREAKDOWN SECTIONS                                        */
/* ============================================================ */
.tax__breakdown {
  margin: 36px 0;
}

.tax__section-heading {
  font-family: var(--wl-serif);
  font-size: 24px;
  font-weight: 600;
  color: var(--wl-ink);
  margin: 0 0 8px;
}

.tax__section-sub {
  font-size: 14px;
  color: var(--wl-ink-muted);
  margin: 0 0 20px;
}

.tax__stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1px;
  background: var(--wl-rule);
  border: 1px solid var(--wl-ink);
}

.tax__stat {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 16px 20px;
  background: var(--wl-card);
}

.tax__stat--highlight {
  background: var(--wl-red);
}
.tax__stat--highlight .tax__stat-label {
  color: rgba(255, 255, 255, 0.75);
}
.tax__stat--highlight .tax__stat-value {
  color: #fff;
}

.tax__stat-label {
  font-family: var(--wl-mono);
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--wl-ink-muted);
}

.tax__stat-value {
  font-size: 22px;
  font-weight: 600;
  color: var(--wl-ink);
}

/* ============================================================ */
/* BAND-BY-BAND BREAKDOWN TABLE                                  */
/* ============================================================ */
.tax__band-details {
  margin-top: 16px;
}

.tax__band-summary {
  font-family: var(--wl-mono);
  font-size: 12px;
  color: var(--wl-ink-muted);
  cursor: pointer;
  padding: 8px 0;
  letter-spacing: 0.04em;
}
.tax__band-summary:hover {
  color: var(--wl-red);
}
.tax__band-summary:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: 2px;
}

.tax__band-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 8px;
  font-size: 14px;
}

.tax__band-table th {
  font-family: var(--wl-mono);
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--wl-ink-muted);
  text-align: left;
  padding: 8px 12px;
  border-bottom: 2px solid var(--wl-ink);
  font-weight: 500;
}

.tax__band-table td {
  padding: 8px 12px;
  border-bottom: 1px solid var(--wl-rule);
  color: var(--wl-ink-body);
}

.tax__band-table th.wl-num,
.tax__band-table td.wl-num {
  text-align: right;
}

/* ============================================================ */
/* ASSUMPTION NOTE                                               */
/* ============================================================ */
.tax__assumption {
  font-size: 13px;
  color: var(--wl-ink-muted);
  line-height: 1.6;
  margin: 16px 0 0;
  padding: 12px 16px;
  border-left: 3px solid var(--wl-rule-strong);
  background: var(--wl-paper-tint);
}
.tax__assumption strong {
  color: var(--wl-ink);
}

/* ============================================================ */
/* COMPARISON BARS                                               */
/* ============================================================ */
.tax__comparison {
  margin: 40px 0;
}

.tax__bars {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 20px;
}

.tax__bar-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.tax__bar-label {
  font-family: var(--wl-mono);
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--wl-ink);
  min-width: 100px;
  text-align: right;
}

.tax__bar-track {
  flex: 1;
  height: 48px;
  background: var(--wl-paper-tint);
  border: 1px solid var(--wl-rule);
  position: relative;
  overflow: hidden;
}

.tax__bar-fill {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 12px;
  transition: width 0.6s ease-out;
  min-width: 60px;
}

.tax__bar-fill--you {
  background: var(--wl-red);
}

.tax__bar-fill--billionaire {
  background: var(--wl-ink);
}

.tax__bar-value {
  font-family: var(--wl-mono);
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  white-space: nowrap;
}

/* ============================================================ */
/* KEY INSIGHT                                                   */
/* ============================================================ */
.tax__insight {
  margin: 36px 0;
  padding: 28px 32px;
  border-top: 4px solid var(--wl-red);
  border-bottom: 1px solid var(--wl-rule);
  background: var(--wl-paper-tint);
}

.tax__insight-text {
  font-family: var(--wl-serif);
  font-size: 20px;
  line-height: 1.6;
  color: var(--wl-ink);
  margin: 12px 0 0;
}

.tax__insight-rate {
  color: var(--wl-red);
  font-weight: 700;
}

.tax__insight-why {
  font-size: 15px;
  color: var(--wl-ink-body);
  line-height: 1.6;
  margin: 16px 0 0;
}

/* ============================================================ */
/* SOURCE CITATION                                               */
/* ============================================================ */
.tax__source {
  margin: 24px 0;
}

.tax__source-detail {
  font-family: var(--wl-mono);
  font-size: 11px;
  color: var(--wl-ink-muted);
  margin: 8px 0 0;
}
.tax__source-detail a {
  color: var(--wl-red);
  text-decoration: none;
  border-bottom: 1px solid var(--wl-red);
}
.tax__source-detail a:hover {
  border-bottom-width: 2px;
}
.tax__source-detail a:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: 2px;
}

/* ============================================================ */
/* RESET BUTTON                                                  */
/* ============================================================ */
.tax__reset {
  margin-top: 16px;
}

/* ============================================================ */
/* RESPONSIVE                                                    */
/* ============================================================ */
@media (max-width: 768px) {
  .tax {
    padding: 32px 16px 64px;
  }

  .tax__input-row {
    flex-direction: column;
    max-width: 100%;
  }

  .tax__currency {
    border-right: 1px solid var(--wl-ink);
    border-bottom: none;
    border-radius: var(--wl-radius) var(--wl-radius) 0 0;
    justify-content: center;
    padding: 8px;
  }

  .tax__input {
    border-left: 1px solid var(--wl-ink);
    border-right: 1px solid var(--wl-ink);
  }

  .tax__btn {
    border-radius: 0 0 var(--wl-radius) var(--wl-radius);
    height: 48px;
  }

  .tax__stat-grid {
    grid-template-columns: 1fr 1fr;
  }

  .tax__bar-label {
    min-width: 80px;
    font-size: 10px;
  }

  .tax__bar-track {
    height: 40px;
  }

  .tax__insight {
    padding: 20px;
  }
}

@media (max-width: 480px) {
  .tax__stat-grid {
    grid-template-columns: 1fr;
  }

  .tax__presets {
    flex-direction: column;
    align-items: flex-start;
  }

  .tax__bar-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .tax__bar-label {
    text-align: left;
    min-width: auto;
  }

  .tax__bar-track {
    width: 100%;
  }
}
</style>
