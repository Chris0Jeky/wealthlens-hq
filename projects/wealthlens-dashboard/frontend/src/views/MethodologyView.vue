<script setup lang="ts">
/**
 * MethodologyView — Broadsheet-style Methodology page for WealthLens UK.
 *
 * Documents every data source with URL, licence, access date format,
 * update frequency, and processing notes. Explains the pipeline
 * architecture, citation format, known limitations, and update cadence.
 */

/** Data source descriptor for rendering the source table. */
interface DataSource {
  name: string
  organisation: string
  url: string
  licence: string
  licenceUrl?: string
  updateFrequency: string
  processing: string
}

const dataSources: DataSource[] = [
  {
    name: 'Net personal wealth shares (top 1%, top 10%, bottom 50%)',
    organisation: 'World Inequality Database (WID)',
    url: 'https://wid.world/country/united-kingdom/',
    licence: 'Creative Commons Attribution 4.0 (CC BY 4.0)',
    licenceUrl: 'https://creativecommons.org/licenses/by/4.0/',
    updateFrequency: 'Annual (irregular)',
    processing:
      'Fetched via WID API. Filtered to UK net personal wealth percentile series. Pivoted to year rows with columns per percentile group. Missing years are not interpolated.',
  },
  {
    name: 'Housing affordability ratios (price-to-earnings)',
    organisation: 'Office for National Statistics (ONS)',
    url: 'https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/ratioofhousepricetoworkplacebasedearningslowerquartileandmedian',
    licence: 'Open Government Licence v3.0 (OGL v3.0)',
    licenceUrl: 'https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/',
    updateFrequency: 'Annual',
    processing:
      'Downloaded XLSX from ONS. Extracted median price-to-earnings ratios by region. Transposed to tidy CSV with year, region, and ratio columns. Regions mapped to standard ONS ITL1 codes.',
  },
  {
    name: 'Capital gains tax concentration by size of gain',
    organisation: 'HM Revenue & Customs (HMRC)',
    url: 'https://www.gov.uk/government/statistics/capital-gains-tax-statistics',
    licence: 'Open Government Licence v3.0 (OGL v3.0)',
    licenceUrl: 'https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/',
    updateFrequency: 'Annual (July/August)',
    processing:
      'Downloaded ODS/XLSX from HMRC statistical release. Extracted gains by size band. Calculated cumulative share of total gains by band. Suppressed bands where HMRC redacts taxpayer counts.',
  },
  {
    name: 'Total household wealth by decile group',
    organisation: 'Office for National Statistics (ONS)',
    url: 'https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/bulletins/totalwealthingreatbritain/latest',
    licence: 'Open Government Licence v3.0 (OGL v3.0)',
    licenceUrl: 'https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/',
    updateFrequency: 'Biennial (currently suspended)',
    processing:
      'Downloaded from ONS Wealth and Assets Survey bulletin. Extracted total net wealth by decile group. Converted to tidy CSV. Note: WAS lost accredited official statistics status in June 2025; response rates fell from 66% to 41%.',
  },
  {
    name: 'UK House Price Index',
    organisation: 'HM Land Registry',
    url: 'https://www.gov.uk/government/statistical-data-sets/uk-house-price-index',
    licence: 'Open Government Licence v3.0 (OGL v3.0)',
    licenceUrl: 'https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/',
    updateFrequency: 'Monthly',
    processing:
      'Downloaded CSV from Land Registry. Filtered to aggregate UK and regional series. Indexed to baseline year for comparability.',
  },
  {
    name: 'HMRC Tax Receipts and National Insurance Contributions',
    organisation: 'HM Revenue & Customs (HMRC)',
    url: 'https://www.gov.uk/government/statistics/hmrc-tax-receipts-and-national-insurance-contributions-for-the-uk',
    licence: 'Open Government Licence v3.0 (OGL v3.0)',
    licenceUrl: 'https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/',
    updateFrequency: 'Annual + monthly updates',
    processing:
      'Downloaded ODS from HMRC. Extracted tax receipts by category. Calculated percentage shares of total receipts. Used for tax composition treemap and time-series.',
  },
]
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

    <!-- Page headline -->
    <header class="page-header">
      <span class="wl-eyebrow">Methodology</span>
      <h1 class="page-header__title">
        Our <em>Methodology</em>
      </h1>
      <hr class="wl-rule-red" />
    </header>

    <!-- Intro -->
    <section class="content-section" aria-labelledby="intro-heading">
      <h2 id="intro-heading" class="sr-only">Introduction</h2>
      <div class="section-body">
        <p class="lede">
          Every chart on WealthLens UK is backed by a cited, publicly licensed
          data source. This page documents where our data comes from, how we
          process it, and what its limitations are.
        </p>
      </div>
    </section>

    <hr class="wl-rule" />

    <!-- Data Sources -->
    <section class="content-section" aria-labelledby="sources-heading">
      <h2 id="sources-heading" class="section-heading">Data sources</h2>
      <p class="section-intro">
        The table below lists every dataset currently used by WealthLens,
        with its publisher, licence, update frequency, and a summary of how
        we process it. Access dates are recorded per-fetch in each
        pipeline's <code>.meta.json</code> sidecar file.
      </p>

      <div class="source-cards">
        <article
          v-for="(source, i) in dataSources"
          :key="i"
          class="source-card"
        >
          <h3 class="source-card__name">{{ source.name }}</h3>
          <dl class="source-card__meta">
            <div class="source-card__row">
              <dt>Organisation</dt>
              <dd>{{ source.organisation }}</dd>
            </div>
            <div class="source-card__row">
              <dt>URL</dt>
              <dd>
                <a
                  :href="source.url"
                  target="_blank"
                  rel="noopener"
                  class="source-card__link"
                >
                  {{ source.url }}
                </a>
              </dd>
            </div>
            <div class="source-card__row">
              <dt>Licence</dt>
              <dd>
                <a
                  v-if="source.licenceUrl"
                  :href="source.licenceUrl"
                  target="_blank"
                  rel="noopener"
                  class="source-card__link"
                >
                  {{ source.licence }}
                </a>
                <span v-else>{{ source.licence }}</span>
              </dd>
            </div>
            <div class="source-card__row">
              <dt>Access date</dt>
              <dd>Recorded per-fetch in YYYY-MM-DD format</dd>
            </div>
            <div class="source-card__row">
              <dt>Update frequency</dt>
              <dd>{{ source.updateFrequency }}</dd>
            </div>
            <div class="source-card__row">
              <dt>Processing</dt>
              <dd>{{ source.processing }}</dd>
            </div>
          </dl>
        </article>
      </div>
    </section>

    <hr class="wl-rule" />

    <!-- Processing Pipeline -->
    <section class="content-section" aria-labelledby="pipeline-heading">
      <h2 id="pipeline-heading" class="section-heading">Processing pipeline</h2>
      <div class="section-body">
        <p>
          All data processing is handled by Python scripts in
          <code>automation/data-pipelines/</code>. Each pipeline follows a
          consistent four-stage pattern:
        </p>

        <div class="pipeline-stages">
          <div class="pipeline-stage">
            <span class="pipeline-stage__number">1</span>
            <div>
              <h3 class="pipeline-stage__title">Fetch</h3>
              <p class="pipeline-stage__text">
                Download the raw data from the source URL. HTTP requests include
                timeouts, retries, and user-agent headers. If the source API is
                unavailable, the pipeline falls back to cached or illustrative
                data (clearly marked as such).
              </p>
            </div>
          </div>
          <div class="pipeline-stage">
            <span class="pipeline-stage__number">2</span>
            <div>
              <h3 class="pipeline-stage__title">Validate</h3>
              <p class="pipeline-stage__text">
                Check the downloaded data for expected structure: required
                columns, plausible value ranges, and no unexpected nulls.
                Validation failures are logged and halt the pipeline rather than
                producing silently bad output.
              </p>
            </div>
          </div>
          <div class="pipeline-stage">
            <span class="pipeline-stage__number">3</span>
            <div>
              <h3 class="pipeline-stage__title">Process</h3>
              <p class="pipeline-stage__text">
                Transform the data into tidy CSV format suitable for
                visualisation. This includes pivoting, filtering, calculating
                derived metrics (e.g. percentage shares), and mapping region
                codes to human-readable names.
              </p>
            </div>
          </div>
          <div class="pipeline-stage">
            <span class="pipeline-stage__number">4</span>
            <div>
              <h3 class="pipeline-stage__title">Output</h3>
              <p class="pipeline-stage__text">
                Write the processed CSV to <code>data/processed/</code>
                alongside a <code>.meta.json</code> sidecar file that records
                the source URL, access date, row count, column names, and a
                SHA-256 hash of the output for integrity checking.
              </p>
            </div>
          </div>
        </div>

        <div class="fallback-note">
          <p class="wl-eyebrow">Illustrative data</p>
          <p>
            When a source API is unavailable or returns an error, some pipelines
            generate illustrative data based on previously observed values. This
            data is always clearly marked with an
            <code>is_illustrative: true</code> flag in the sidecar metadata and
            displayed with a visual warning on the chart.
          </p>
        </div>
      </div>
    </section>

    <hr class="wl-rule" />

    <!-- Citation Format -->
    <section class="content-section" aria-labelledby="citation-heading">
      <h2 id="citation-heading" class="section-heading">How to cite</h2>
      <div class="section-body">
        <p>
          If you use WealthLens charts or data in your own work, please cite
          both WealthLens and the original data source:
        </p>
        <div class="citation-box">
          <p class="citation-box__example">
            WealthLens UK (2026). "<em>[Chart title]</em>".
            Available at: https://chris0jeky.github.io/wealthlens-hq/.
            Data source: <em>[Original source and URL]</em>.
            Accessed: <em>[YYYY-MM-DD]</em>.
          </p>
        </div>
        <p>
          Each chart page includes a source bar at the bottom with the full
          citation details, including chart ID, data source, licence, and
          access date.
        </p>
      </div>
    </section>

    <hr class="wl-rule" />

    <!-- Limitations -->
    <section class="content-section" aria-labelledby="limitations-heading">
      <h2 id="limitations-heading" class="section-heading">Limitations</h2>
      <div class="section-body">
        <p>
          We believe in being honest about what our data does and does not show.
          Key limitations include:
        </p>
        <ul class="limitations-list">
          <li>
            <strong>Top-tail undercounting.</strong> Survey-based wealth data
            (like the ONS Wealth and Assets Survey) systematically undercounts
            wealth at the very top of the distribution. The very wealthy are
            less likely to respond to surveys, and their assets are harder to
            measure. WID addresses this partly through rich-list calibration,
            but gaps remain.
          </li>
          <li>
            <strong>Offshore wealth.</strong> Wealth held offshore or in opaque
            structures (trusts, shell companies) is largely invisible to UK
            statistical collection. Estimates suggest this could be significant,
            meaning our charts may understate true inequality.
          </li>
          <li>
            <strong>Pension wealth.</strong> The inclusion or exclusion of
            pension wealth significantly affects distribution measures.
            Defined-benefit pension entitlements are excluded from some WID
            series but included in ONS WAS data. We note the treatment on each
            chart.
          </li>
          <li>
            <strong>Historical comparability.</strong> Long-run series
            (e.g. wealth shares from 1820) combine different estimation methods
            across different eras. Pre-1900 estimates rely on estate-multiplier
            methods with moderate confidence. We show the methodology used for
            each time period where available.
          </li>
          <li>
            <strong>Survey suspension.</strong> The ONS Wealth and Assets Survey
            lost its accredited official statistics designation in June 2025,
            and response rates have fallen from 66% to 41%. This affects the
            reliability of recent wealth-by-decile data.
          </li>
          <li>
            <strong>Geographic coverage.</strong> Some datasets cover the UK,
            others cover Great Britain or England and Wales only. We note the
            geographic scope on each chart.
          </li>
        </ul>
      </div>
    </section>

    <hr class="wl-rule" />

    <!-- Updates -->
    <section class="content-section" aria-labelledby="updates-heading">
      <h2 id="updates-heading" class="section-heading">Data updates</h2>
      <div class="section-body">
        <p>
          WealthLens data is refreshed through a combination of automated and
          manual processes:
        </p>
        <ul class="updates-list">
          <li>
            <strong>Weekly automated check.</strong> A GitHub Actions workflow
            runs all data pipelines weekly to detect new releases from source
            organisations.
          </li>
          <li>
            <strong>Manual review.</strong> When new data is detected, it is
            reviewed before being published to ensure quality and consistency
            with existing series.
          </li>
          <li>
            <strong>Version tracking.</strong> Every data update is tracked
            through git commits and <code>.meta.json</code> sidecar files,
            providing a full audit trail of what changed and when.
          </li>
        </ul>
        <p>
          The access date shown on each chart reflects the most recent
          successful fetch from the source. If a source has not been updated
          by its publisher, the access date will still advance on each
          successful check.
        </p>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* ============================================================ */
/* LAYOUT                                                        */
/* ============================================================ */
.methodology-page {
  max-width: 1320px;
  margin: 0 auto;
  padding-bottom: 96px;
}

/* ============================================================ */
/* BREADCRUMB                                                    */
/* ============================================================ */
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

/* ============================================================ */
/* PAGE HEADER                                                   */
/* ============================================================ */
.page-header {
  padding: 32px 32px 0;
}
.page-header__title {
  font-family: var(--wl-serif);
  font-size: clamp(40px, 6vw, 72px);
  font-weight: 600;
  line-height: 0.96;
  letter-spacing: -0.025em;
  color: var(--wl-ink);
  margin: 12px 0 28px;
}
.page-header__title em {
  font-style: italic;
  color: var(--wl-red);
  font-weight: 500;
}

/* ============================================================ */
/* CONTENT SECTIONS                                              */
/* ============================================================ */
.content-section {
  padding: 48px 32px 0;
}

.section-heading {
  font-family: var(--wl-serif);
  font-size: clamp(28px, 3.5vw, 40px);
  font-weight: 600;
  letter-spacing: -0.018em;
  color: var(--wl-ink);
  margin: 0 0 24px;
  line-height: 1.1;
}

.section-intro {
  font-size: 18px;
  color: var(--wl-ink-body);
  line-height: 1.6;
  max-width: 65ch;
  margin: 0 0 32px;
}
.section-intro code {
  font-family: var(--wl-mono);
  font-size: 0.9em;
  background: var(--wl-paper-tint);
  padding: 2px 6px;
  border: 1px solid var(--wl-rule);
}

.section-body {
  max-width: 760px;
}

.section-body p {
  font-size: 18px;
  line-height: 1.7;
  color: var(--wl-ink-body);
  margin: 0 0 18px;
}
.section-body p strong {
  color: var(--wl-ink);
  font-weight: 600;
}
.section-body code {
  font-family: var(--wl-mono);
  font-size: 0.9em;
  background: var(--wl-paper-tint);
  padding: 2px 6px;
  border: 1px solid var(--wl-rule);
}

.lede {
  font-size: 22px !important;
  line-height: 1.5 !important;
  max-width: 55ch;
  margin-bottom: 24px !important;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

/* ============================================================ */
/* SOURCE CARDS                                                  */
/* ============================================================ */
.source-cards {
  display: grid;
  gap: 24px;
}
.source-card {
  background: var(--wl-card);
  border: 1px solid var(--wl-rule-strong);
  padding: 28px;
}
.source-card__name {
  font-family: var(--wl-serif);
  font-size: 20px;
  font-weight: 600;
  color: var(--wl-ink);
  margin: 0 0 18px;
  line-height: 1.2;
}
.source-card__meta {
  margin: 0;
}
.source-card__row {
  display: grid;
  grid-template-columns: 140px 1fr;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid var(--wl-rule);
  font-size: 14px;
  line-height: 1.5;
}
.source-card__row:last-child {
  border-bottom: none;
}
.source-card__row dt {
  font-family: var(--wl-mono);
  font-size: 11px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--wl-ink-muted);
  padding-top: 2px;
}
.source-card__row dd {
  margin: 0;
  color: var(--wl-ink-body);
}
.source-card__link {
  color: var(--wl-red);
  text-decoration: none;
  word-break: break-all;
}
.source-card__link:hover {
  border-bottom: 1px solid var(--wl-red);
}
.source-card__link:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: 2px;
}

/* ============================================================ */
/* PIPELINE STAGES                                               */
/* ============================================================ */
.pipeline-stages {
  display: grid;
  gap: 0;
  margin: 24px 0 32px;
}
.pipeline-stage {
  display: flex;
  gap: 20px;
  padding: 24px 0;
  border-bottom: 1px solid var(--wl-rule);
}
.pipeline-stage:last-child {
  border-bottom: none;
}
.pipeline-stage__number {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--wl-ink);
  color: var(--wl-paper);
  font-family: var(--wl-mono);
  font-size: 14px;
  font-weight: 600;
}
.pipeline-stage__title {
  font-family: var(--wl-serif);
  font-size: 20px;
  font-weight: 600;
  color: var(--wl-ink);
  margin: 0 0 8px;
  line-height: 1.2;
}
.pipeline-stage__text {
  font-size: 15px;
  line-height: 1.6;
  color: var(--wl-ink-body);
  margin: 0;
}
.pipeline-stage__text code {
  font-family: var(--wl-mono);
  font-size: 0.9em;
  background: var(--wl-paper-tint);
  padding: 2px 6px;
  border: 1px solid var(--wl-rule);
}

/* Fallback note */
.fallback-note {
  background: var(--wl-paper-tint);
  border-top: 4px solid var(--wl-red);
  padding: 24px 28px;
  margin-top: 8px;
}
.fallback-note .wl-eyebrow {
  margin-bottom: 8px;
  color: var(--wl-red);
}
.fallback-note p {
  font-size: 15px !important;
  line-height: 1.6;
  margin: 0 0 8px;
}
.fallback-note p:last-child {
  margin-bottom: 0;
}
.fallback-note code {
  font-family: var(--wl-mono);
  font-size: 0.9em;
  background: var(--wl-card);
  padding: 2px 6px;
  border: 1px solid var(--wl-rule);
}

/* ============================================================ */
/* CITATION BOX                                                  */
/* ============================================================ */
.citation-box {
  background: var(--wl-card);
  border: 1px solid var(--wl-ink);
  padding: 24px 28px;
  margin: 16px 0 24px;
}
.citation-box__example {
  font-family: var(--wl-mono);
  font-size: 13px !important;
  line-height: 1.7;
  color: var(--wl-ink-body);
  margin: 0 !important;
}
.citation-box__example em {
  color: var(--wl-red);
  font-style: italic;
  font-family: var(--wl-serif);
}

/* ============================================================ */
/* LIMITATIONS & UPDATES LISTS                                   */
/* ============================================================ */
.limitations-list,
.updates-list {
  padding-left: 0;
  list-style: none;
  margin: 16px 0 0;
}
.limitations-list li,
.updates-list li {
  position: relative;
  padding: 14px 0 14px 24px;
  border-bottom: 1px solid var(--wl-rule);
  font-size: 16px;
  line-height: 1.65;
  color: var(--wl-ink-body);
}
.limitations-list li:last-child,
.updates-list li:last-child {
  border-bottom: none;
}
.limitations-list li::before,
.updates-list li::before {
  content: "";
  position: absolute;
  left: 0;
  top: 22px;
  width: 8px;
  height: 8px;
  background: var(--wl-red);
}
.limitations-list li strong,
.updates-list li strong {
  color: var(--wl-ink);
  font-weight: 600;
}

/* ============================================================ */
/* HORIZONTAL RULES                                              */
/* ============================================================ */
.methodology-page > .wl-rule {
  margin: 48px 32px 0;
}
.methodology-page > .wl-rule-red {
  margin: 0;
}

/* ============================================================ */
/* RESPONSIVE                                                    */
/* ============================================================ */
@media (max-width: 768px) {
  .crumb,
  .page-header,
  .content-section {
    padding-left: 16px;
    padding-right: 16px;
  }

  .methodology-page > .wl-rule {
    margin-left: 16px;
    margin-right: 16px;
  }

  .page-header__title {
    font-size: clamp(32px, 8vw, 48px);
  }

  .section-body p,
  .lede {
    font-size: 16px !important;
  }

  .source-card__row {
    grid-template-columns: 1fr;
    gap: 4px;
  }
}
</style>
