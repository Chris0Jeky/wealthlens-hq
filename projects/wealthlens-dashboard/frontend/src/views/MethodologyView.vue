<script setup lang="ts">
/**
 * MethodologyView — transparency page explaining data pipeline, sources,
 * quality checks, limitations, update schedule, verification, and privacy.
 *
 * Route: /methodology
 */

import { DATASET_PROVENANCE } from "@/constants/datasetProvenance"
import { usePageMeta } from "@/composables/usePageMeta"
import { SITE_URL } from "@/constants/site"

usePageMeta({
  title: "Methodology",
  description:
    "How WealthLens UK collects, validates, and presents UK wealth inequality data. Every number on this site cites its source with a URL and access date.",
  url: `${SITE_URL}/methodology`,
})

/** Dataset source citation used in the template. */
interface DatasetSource {
  name: string
  description: string
  source: string
  sourceUrl: string
  accessDate: string
  updateFrequency: string
}

/**
 * Descriptive citation fields per dataset (one per routed chart). The update
 * cadence is intentionally omitted here and injected from the shared
 * DATASET_PROVENANCE map below, so this page and the Data Sources table can
 * never disagree on a dataset's frequency.
 */
const DATASET_CITATIONS: Omit<DatasetSource, "updateFrequency">[] = [
  {
    name: "wealth-shares",
    description: "Top 1%/10% wealth shares in GB",
    source: "World Inequality Database",
    sourceUrl: "https://wid.world/",
    accessDate: "2026-05-14",
  },
  {
    name: "housing-affordability",
    description: "House price to earnings ratio by region",
    source: "ONS",
    sourceUrl:
      "https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/ratioofhousepricetoworkplacebasedearningslowerquartileandmedian",
    accessDate: "2026-05-14",
  },
  {
    name: "wealth-by-decile",
    description: "Total net wealth by decile",
    source: "ONS Wealth and Assets Survey",
    sourceUrl:
      "https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/datasets/totalwealthwealthingreatbritain",
    accessDate: "2026-05-14",
  },
  {
    name: "cgt-concentration",
    description: "Capital gains by size of gain",
    source: "HMRC",
    sourceUrl: "https://www.gov.uk/government/statistics/capital-gains-tax-statistics",
    accessDate: "2026-05-14",
  },
  {
    name: "productivity-pay",
    description: "UK productivity vs. real pay, indexed to 100 at 1997",
    source: "ONS Labour Productivity (LZVD) & ONS AWE (KAB9) deflated by CPIH (L55O)",
    sourceUrl:
      "https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/labourproductivity/timeseries/lzvd/prdy",
    accessDate: "2026-05-16",
  },
  {
    name: "gdhi-by-region",
    description: "Gross disposable household income per head by region",
    source: "ONS Regional GDHI",
    sourceUrl:
      "https://www.ons.gov.uk/economy/regionalaccounts/grossdisposablehouseholdincome/datasets/regionalgrossdisposablehouseholdincomegdhi",
    accessDate: "2026-05-16",
  },
  {
    name: "tax-composition",
    description: "UK tax revenue composition: work taxes vs wealth taxes",
    source: "HMRC Tax and NIC Receipts",
    sourceUrl: "https://www.gov.uk/government/statistics/hmrc-tax-and-nics-receipts-for-the-uk",
    accessDate: "2026-05-16",
  },
  {
    name: "boe-rates",
    description: "Bank Rate and CPI annual inflation",
    source: "Bank of England Interactive Analytical Database",
    sourceUrl: "https://www.bankofengland.co.uk/boeapps/database/",
    accessDate: "2026-05-16",
  },
  {
    name: "child-poverty",
    description: "Child poverty rates by UK region (after housing costs)",
    source: "DWP/HMRC Children in Low Income Families",
    sourceUrl:
      "https://www.gov.uk/government/statistics/children-in-low-income-families-local-area-statistics-2014-to-2023",
    accessDate: "2026-05-16",
  },
  {
    name: "generational-wealth",
    description: "Median household wealth by generation at equivalent ages",
    source: "Resolution Foundation / ONS Wealth and Assets Survey",
    sourceUrl: "https://www.resolutionfoundation.org/publications/",
    accessDate: "2026-05-16",
  },
  {
    name: "wage-stagnation",
    description: "Real (CPI-adjusted, 2024 prices) median weekly pay (£/week)",
    source: "ONS Annual Survey of Hours and Earnings (ASHE)",
    sourceUrl:
      "https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/ashe1702",
    accessDate: "2026-05-16",
  },
  {
    name: "inheritance-tax",
    description: "Estates notified and liable to inheritance tax",
    source: "HMRC Inheritance Tax Statistics",
    sourceUrl: "https://www.gov.uk/government/statistics/inheritance-tax-statistics",
    accessDate: "2026-05-16",
  },
]

/**
 * Full citations with the update cadence merged in from the shared source of
 * truth. Falls back to an em dash if a slug ever lacks a provenance entry (the
 * datasetProvenance.test.ts keyset guard prevents that in practice).
 */
const datasets: DatasetSource[] = DATASET_CITATIONS.map((d) => ({
  ...d,
  updateFrequency: DATASET_PROVENANCE[d.name]?.updateFrequency ?? "—",
}))
</script>

<template>
  <div class="methodology-page">
    <!-- Breadcrumb -->
    <nav class="crumb" aria-label="Breadcrumb">
      <ol class="crumb__list">
        <li class="crumb__item">
          <router-link to="/" class="crumb__link">Home</router-link>
          <span class="crumb__sep" aria-hidden="true">/</span>
        </li>
        <li class="crumb__item">
          <span class="crumb__current" aria-current="page">Methodology</span>
        </li>
      </ol>
    </nav>

    <article class="methodology-content">
      <header class="methodology-header">
        <h1 class="methodology-title">Methodology</h1>
        <p class="methodology-subtitle">
          How we collect, validate, and present UK wealth inequality data. Every number on this site
          traces back to a named, dated, publicly available source.
        </p>
      </header>

      <hr class="wl-rule-thick" />

      <!-- 1. Data Pipeline Process -->
      <section class="methodology-section" aria-labelledby="pipeline-heading">
        <span class="wl-eyebrow">How it works</span>
        <h2 id="pipeline-heading" class="section-heading">Data Pipeline Process</h2>
        <p class="section-body">
          Data flows through five stages from official source to rendered chart:
        </p>
        <ol class="pipeline-steps">
          <li class="pipeline-step">
            <strong class="step-label">Fetch</strong>
            <span class="step-desc">
              Automated Python scripts download raw data files from government and academic sources
              (ONS, HMRC, WID, BoE, Resolution Foundation).
            </span>
          </li>
          <li class="pipeline-step">
            <strong class="step-label">Validate</strong>
            <span class="step-desc">
              Column presence, data types, and expected ranges are checked. Malformed or missing
              files halt the pipeline with a clear error.
            </span>
          </li>
          <li class="pipeline-step">
            <strong class="step-label">Process</strong>
            <span class="step-desc">
              Raw data is cleaned, normalised, and written to standardised CSV files. Beyond
              standard normalisation (e.g. rebasing to an index or converting to real terms), no
              modelling or extrapolation is applied; where live data is temporarily unavailable the
              pipeline substitutes clearly-labelled illustrative values.
            </span>
          </li>
          <li class="pipeline-step">
            <strong class="step-label">Serve</strong>
            <span class="step-desc">
              The FastAPI backend reads processed CSVs and exposes them as paginated JSON endpoints
              with full metadata and source citations.
            </span>
          </li>
          <li class="pipeline-step">
            <strong class="step-label">Render</strong>
            <span class="step-desc">
              The Vue 3 frontend fetches data from the API and renders interactive, accessible,
              mobile-responsive charts.
            </span>
          </li>
        </ol>
      </section>

      <hr class="wl-rule" />

      <!-- 2. Source Citations -->
      <section class="methodology-section" aria-labelledby="sources-heading">
        <span class="wl-eyebrow">Provenance</span>
        <h2 id="sources-heading" class="section-heading">Source Citations</h2>
        <p class="section-body">
          All 12 datasets are sourced from official government and academic publications. Each entry
          below documents the source name, URL, access date, and update frequency.
        </p>
        <div class="sources-grid">
          <article v-for="ds in datasets" :key="ds.name" class="source-card">
            <h3 class="source-card__name">{{ ds.name }}</h3>
            <p class="source-card__desc">{{ ds.description }}</p>
            <dl class="source-card__meta">
              <div class="source-card__row">
                <dt>Source</dt>
                <dd>{{ ds.source }}</dd>
              </div>
              <div class="source-card__row">
                <dt>URL</dt>
                <dd>
                  <a
                    :href="ds.sourceUrl"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="source-card__link"
                    >{{ ds.sourceUrl }}</a
                  >
                </dd>
              </div>
              <div class="source-card__row">
                <dt>Accessed</dt>
                <dd class="source-card__date">{{ ds.accessDate }}</dd>
              </div>
              <div class="source-card__row">
                <dt>Updates</dt>
                <dd>{{ ds.updateFrequency }}</dd>
              </div>
            </dl>
          </article>
        </div>
      </section>

      <hr class="wl-rule" />

      <!-- 3. Data Quality -->
      <section class="methodology-section" aria-labelledby="quality-heading">
        <span class="wl-eyebrow">Integrity</span>
        <h2 id="quality-heading" class="section-heading">Data Quality</h2>
        <p class="section-body">
          Every dataset passes automated quality checks before it reaches the API:
        </p>
        <ul class="quality-list">
          <li>
            <strong>Column validation</strong> — expected columns must be present with correct
            names. Missing or renamed columns halt the pipeline.
          </li>
          <li>
            <strong>NaN handling</strong> — null and missing values are explicitly detected. They
            are preserved as <code>null</code> in JSON responses rather than silently dropped or
            filled.
          </li>
          <li>
            <strong>Type enforcement</strong> — numeric columns are verified as numeric; date
            columns as valid dates. Type mismatches are logged and rejected.
          </li>
          <li>
            <strong>Row count checks</strong> — datasets with zero rows or unexpectedly low row
            counts trigger warnings.
          </li>
          <li>
            <strong>Encoding safety</strong> — all files are read as UTF-8. Encoding errors are
            caught and reported rather than producing garbled output.
          </li>
        </ul>
      </section>

      <hr class="wl-rule" />

      <!-- 4. Limitations -->
      <section class="methodology-section" aria-labelledby="limitations-heading">
        <span class="wl-eyebrow">Caveats</span>
        <h2 id="limitations-heading" class="section-heading">Limitations</h2>
        <p class="section-body">
          No dataset is perfect. Users should be aware of the following limitations when
          interpreting the charts:
        </p>
        <ul class="limitations-list">
          <li>
            <strong>Survey sample sizes</strong> — the Wealth and Assets Survey samples
            approximately 20,000 households. Extreme wealth is systematically underrepresented
            because the very wealthy are less likely to respond. The WAS also lost accredited
            official statistics status in June 2025 after its response rate fell from 66% to 41%.
          </li>
          <li>
            <strong>Time lag</strong> — official statistics are published months or years after the
            period they cover. The most recent data point may be 1-3 years old.
          </li>
          <li>
            <strong>Wealth measurement difficulties</strong> — wealth held in trusts, offshore
            accounts, or complex structures may not appear in survey or administrative data.
          </li>
          <li>
            <strong>Self-reported data biases</strong> — household surveys rely on self-reporting.
            Respondents may underestimate or overestimate their assets and liabilities.
          </li>
          <li>
            <strong>Geographic coverage varies</strong> — some datasets cover Great Britain only
            (excluding Northern Ireland), others cover the full United Kingdom, and some are England
            and Wales only.
          </li>
          <li>
            <strong>Definitional differences</strong> — "wealth" is defined differently across
            sources (net financial wealth vs. total wealth including property and pensions).
          </li>
        </ul>
      </section>

      <hr class="wl-rule" />

      <!-- 5. Update Schedule -->
      <section class="methodology-section" aria-labelledby="schedule-heading">
        <span class="wl-eyebrow">Freshness</span>
        <h2 id="schedule-heading" class="section-heading">Update Schedule</h2>
        <p class="section-body">
          The data pipeline runs automatically every week via GitHub Actions. Each run fetches the
          latest available data from these sources, validates it, and updates the processed CSV
          files. If a source has not published new data since the last run, the existing file is
          retained unchanged.
        </p>
        <p class="section-body">
          Pipeline run logs are publicly visible in the repository's Actions tab. Failed runs
          trigger alerts and do not update any data files, ensuring stale-but-correct data is always
          preferred over fresh-but-broken data.
        </p>
      </section>

      <hr class="wl-rule" />

      <!-- 6. Verification -->
      <section class="methodology-section" aria-labelledby="verification-heading">
        <span class="wl-eyebrow">Trust but verify</span>
        <h2 id="verification-heading" class="section-heading">Verification</h2>
        <p class="section-body">Every claim on this site can be independently verified:</p>
        <ul class="verification-list">
          <li>
            <strong>Check the source data</strong> — every chart links to the original government or
            academic publication. Click through and compare the numbers yourself.
          </li>
          <li>
            <strong>Read the pipeline code</strong> — all data processing scripts are open source at
            <a
              href="https://github.com/Chris0Jeky/wealthlens-hq/tree/main/automation/data-pipelines"
              target="_blank"
              rel="noopener noreferrer"
              class="inline-link"
              >github.com/Chris0Jeky/wealthlens-hq/automation/data-pipelines</a
            >.
          </li>
          <li>
            <strong>Download the processed data</strong> — every dataset is published as static CSV
            and JSON files alongside the site (linked from the home-page cards and each chart's
            toolbar). Compare our processed output against the raw source.
          </li>
          <li>
            <strong>Run it yourself</strong> — clone the repository and run the pipeline locally.
            The entire stack is reproducible with standard Python and Node.js tooling.
          </li>
        </ul>
      </section>

      <hr class="wl-rule" />

      <!-- 7. Privacy -->
      <section class="methodology-section" aria-labelledby="privacy-heading">
        <span class="wl-eyebrow">Your data</span>
        <h2 id="privacy-heading" class="section-heading">Privacy</h2>
        <p class="section-body">WealthLens UK does not collect personal data. Specifically:</p>
        <ul class="privacy-list">
          <li>No personal data is collected, stored, or processed.</li>
          <li>No cookies are used for tracking or advertising.</li>
          <li>
            No third-party tracking scripts are loaded unless privacy-respecting, aggregate
            analytics are explicitly enabled for a deployment.
          </li>
          <li>
            Analytics, if enabled, are privacy-respecting and aggregated — no individual user
            profiles are created.
          </li>
          <li>
            All datasets contain only aggregate, publicly available statistics. No individual-level
            data is used.
          </li>
        </ul>
      </section>
    </article>
  </div>
</template>

<style scoped>
.methodology-page {
  max-width: var(--wl-max);
  margin: 0 auto;
}

/* --- Breadcrumb --- */
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

/* --- Content --- */
.methodology-content {
  padding: 32px 32px 64px;
}

.methodology-header {
  margin-bottom: 32px;
}

.methodology-title {
  font-family: var(--wl-serif);
  font-size: clamp(36px, 5vw, 56px);
  line-height: 1;
  letter-spacing: -0.02em;
  font-weight: 600;
  color: var(--wl-ink);
  margin: 0 0 12px;
}

.methodology-subtitle {
  font-size: 17px;
  line-height: 1.6;
  color: var(--wl-ink-muted);
  max-width: 640px;
  margin: 0;
}

/* --- Sections --- */
.methodology-section {
  padding: 40px 0;
}

.section-heading {
  font-family: var(--wl-serif);
  font-size: clamp(24px, 3vw, 32px);
  line-height: 1.15;
  letter-spacing: -0.01em;
  font-weight: 600;
  color: var(--wl-ink);
  margin: 8px 0 16px;
}

.section-body {
  font-size: 16px;
  line-height: 1.7;
  color: var(--wl-ink-body);
  max-width: 720px;
  margin: 0 0 16px;
}

/* --- Pipeline steps --- */
.pipeline-steps {
  list-style: none;
  padding: 0;
  margin: 24px 0 0;
  counter-reset: step;
}

.pipeline-step {
  display: flex;
  gap: 16px;
  align-items: baseline;
  padding: 12px 0;
  border-bottom: 1px solid var(--wl-rule);
  counter-increment: step;
}

.pipeline-step::before {
  content: counter(step);
  font-family: var(--wl-mono);
  font-size: 13px;
  font-weight: 600;
  color: var(--wl-red);
  flex-shrink: 0;
  width: 24px;
  text-align: center;
}

.step-label {
  font-weight: 600;
  color: var(--wl-ink);
  min-width: 80px;
}

.step-desc {
  color: var(--wl-ink-body);
  line-height: 1.6;
}

/* --- Source cards --- */
.sources-grid {
  display: grid;
  gap: 16px;
  margin-top: 24px;
}

.source-card {
  background: var(--wl-card);
  border: 1px solid var(--wl-rule);
  border-radius: var(--wl-radius);
  padding: 20px 24px;
  box-shadow: var(--wl-shadow-sm);
}

.source-card__name {
  font-family: var(--wl-mono);
  font-size: 14px;
  font-weight: 600;
  color: var(--wl-ink);
  margin: 0 0 4px;
  letter-spacing: -0.01em;
}

.source-card__desc {
  font-size: 15px;
  color: var(--wl-ink-body);
  margin: 0 0 12px;
  line-height: 1.5;
}

.source-card__meta {
  margin: 0;
}

.source-card__row {
  display: flex;
  gap: 12px;
  padding: 4px 0;
  font-size: 13px;
  line-height: 1.5;
}

.source-card__row dt {
  font-weight: 600;
  color: var(--wl-ink-muted);
  min-width: 72px;
  flex-shrink: 0;
}

.source-card__row dd {
  margin: 0;
  color: var(--wl-ink-body);
  word-break: break-all;
}

.source-card__link {
  color: var(--wl-red);
  text-decoration: none;
  font-family: var(--wl-mono);
  font-size: 12px;
}
.source-card__link:hover {
  text-decoration: underline;
}
.source-card__link:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: 2px;
}
.source-card__date {
  font-family: var(--wl-mono);
  font-size: 12px;
  color: var(--wl-ink-muted);
}

/* --- Lists (quality, limitations, verification, privacy) --- */
.quality-list,
.limitations-list,
.verification-list,
.privacy-list {
  list-style: none;
  padding: 0;
  margin: 16px 0 0;
}

.quality-list li,
.limitations-list li,
.verification-list li,
.privacy-list li {
  position: relative;
  padding: 8px 0 8px 20px;
  line-height: 1.7;
  color: var(--wl-ink-body);
}

.quality-list li::before,
.limitations-list li::before,
.verification-list li::before,
.privacy-list li::before {
  content: "";
  position: absolute;
  left: 0;
  top: 16px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--wl-red);
}

.quality-list li code {
  font-family: var(--wl-mono);
  font-size: 13px;
  background: var(--wl-paper-tint);
  padding: 1px 6px;
  border-radius: 2px;
}

.inline-link {
  color: var(--wl-red);
  text-decoration: none;
}
.inline-link:hover {
  text-decoration: underline;
}
.inline-link:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: 2px;
}

/* --- Responsive --- */
@media (max-width: 768px) {
  .crumb {
    padding-left: 16px;
    padding-right: 16px;
  }

  .methodology-content {
    padding: 24px 16px 48px;
  }

  .pipeline-step {
    flex-direction: column;
    gap: 4px;
  }

  .step-label {
    min-width: unset;
  }

  .source-card__row {
    flex-direction: column;
    gap: 2px;
  }

  .source-card__row dt {
    min-width: unset;
  }
}

@media (max-width: 480px) {
  .methodology-title {
    font-size: 28px;
  }

  .section-heading {
    font-size: 22px;
  }

  .methodology-section {
    padding: 28px 0;
  }

  .source-card {
    padding: 16px;
  }
}
</style>
