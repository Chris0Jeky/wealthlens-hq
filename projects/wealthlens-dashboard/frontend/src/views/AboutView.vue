<script setup lang="ts">
/**
 * AboutView — Broadsheet-style About page for WealthLens UK.
 *
 * Presents the project mission, values, team, data partners,
 * open-source invitation, and contact details in a layout that
 * matches the newspaper aesthetic used throughout the dashboard.
 */
</script>

<template>
  <div class="about-page">
    <!-- Breadcrumb -->
    <nav class="crumb" aria-label="Breadcrumb">
      <ol class="crumb__list">
        <li class="crumb__item">
          <router-link to="/" class="crumb__link">Home</router-link>
          <span class="crumb__sep" aria-hidden="true">/</span>
        </li>
        <li class="crumb__item">
          <span class="crumb__current" aria-current="page">About</span>
        </li>
      </ol>
    </nav>

    <!-- Page headline -->
    <header class="page-header">
      <span class="wl-eyebrow">About</span>
      <h1 class="page-header__title">
        About WealthLens <em>UK</em>
      </h1>
      <hr class="wl-rule-red" />
    </header>

    <!-- Mission section -->
    <section class="content-section" aria-labelledby="mission-heading">
      <h2 id="mission-heading" class="section-heading">Our mission</h2>
      <div class="section-body">
        <p class="lede">
          WealthLens UK is an open-source project making UK wealth inequality
          data <strong>visible</strong>, <strong>interactive</strong>, and
          <strong>impossible to ignore</strong>.
        </p>
        <p>
          We believe that wealth inequality is the defining issue of our time in
          the United Kingdom, yet the data that proves it is scattered across
          dozens of government spreadsheets, academic databases, and paywalled
          reports. WealthLens brings it together in one place with
          source-backed, interactive charts that anyone can explore.
        </p>
        <p>
          We collaborate with organisations such as
          <a
            href="https://www.taxjustice.org.uk/"
            target="_blank"
            rel="noopener"
          >Tax Justice UK</a>,
          <a
            href="https://www.patrioticmillionaires.uk/"
            target="_blank"
            rel="noopener"
          >Patriotic Millionaires UK</a>, and
          <a
            href="https://equalitytrust.org.uk/"
            target="_blank"
            rel="noopener"
          >The Equality Trust</a>
          to ensure the data reaches the people and policymakers who need it.
        </p>
      </div>
    </section>

    <hr class="wl-rule" />

    <!-- Values section -->
    <section class="content-section" aria-labelledby="values-heading">
      <h2 id="values-heading" class="section-heading">Our values</h2>
      <div class="values-grid">
        <div class="value-card">
          <h3 class="value-card__title">Data first, opinion second</h3>
          <p class="value-card__text">
            Every chart cites its source with a URL and access date. We present
            the data and let it speak for itself. No editorialising without
            evidence.
          </p>
        </div>
        <div class="value-card">
          <h3 class="value-card__title">Open source always</h3>
          <p class="value-card__text">
            All code, data pipelines, and methodology are public. Anyone can
            inspect, reproduce, or improve our work.
          </p>
        </div>
        <div class="value-card">
          <h3 class="value-card__title">Accessible by default</h3>
          <p class="value-card__text">
            Charts are mobile-responsive and meet WCAG AA accessibility
            standards. Data should be understandable by everyone, not just
            researchers.
          </p>
        </div>
        <div class="value-card">
          <h3 class="value-card__title">Independent and non-partisan</h3>
          <p class="value-card__text">
            We are not affiliated with any political party. We present facts
            from official sources and let citizens draw their own conclusions.
          </p>
        </div>
      </div>
    </section>

    <hr class="wl-rule" />

    <!-- The Team section -->
    <section class="content-section" aria-labelledby="team-heading">
      <h2 id="team-heading" class="section-heading">The team</h2>
      <div class="section-body">
        <div class="team-card">
          <div class="team-card__info">
            <h3 class="team-card__name">Chris</h3>
            <p class="team-card__role">Founder &amp; Lead Developer</p>
            <p>
              London-based software engineer with a BSc in Computer Science
              (First Class Honours, Middlesex University). Chris has worked in
              DevSecOps and CI/CD at GE Digital, published research on
              multi-agent systems (Springer, SGAI-AI 2025), and currently works
              in Widening Participation outreach at Middlesex University.
            </p>
            <p>
              WealthLens grew out of a frustration: the data proving UK wealth
              inequality exists, but it is buried in spreadsheets that nobody
              outside academia and government ever reads. This project aims to
              change that.
            </p>
          </div>
        </div>
        <div class="contributors-note">
          <p class="wl-eyebrow">Open to contributors</p>
          <p>
            WealthLens UK is currently a solo project, but contributions are
            welcome. Whether you are a developer, designer, data analyst, or
            just someone who cares about making inequality data visible, there
            is a place for you.
            <a
              href="https://github.com/Chris0Jeky/wealthlens-hq/issues"
              target="_blank"
              rel="noopener"
            >Browse open issues</a>
            to find a good first contribution.
          </p>
        </div>
      </div>
    </section>

    <hr class="wl-rule" />

    <!-- Data Partners section -->
    <section class="content-section" aria-labelledby="partners-heading">
      <h2 id="partners-heading" class="section-heading">Data sources</h2>
      <p class="section-intro">
        WealthLens draws on official, publicly licensed data from these
        organisations. Every chart cites its specific source.
      </p>
      <div class="partners-grid">
        <div class="partner-card">
          <h3 class="partner-card__name">Office for National Statistics (ONS)</h3>
          <p class="partner-card__data">
            Housing affordability ratios, Wealth and Assets Survey,
            regional gross disposable household income, earnings data, and
            household wealth by decile.
          </p>
          <p class="partner-card__licence">
            <span class="wl-eyebrow">Licence</span> Open Government Licence v3.0
          </p>
        </div>
        <div class="partner-card">
          <h3 class="partner-card__name">World Inequality Database (WID)</h3>
          <p class="partner-card__data">
            Long-run wealth share series for the UK (1820 to present), income
            distributions, and cross-country comparisons using harmonised
            DINA methodology.
          </p>
          <p class="partner-card__licence">
            <span class="wl-eyebrow">Licence</span> Creative Commons Attribution 4.0
          </p>
        </div>
        <div class="partner-card">
          <h3 class="partner-card__name">HM Revenue &amp; Customs (HMRC)</h3>
          <p class="partner-card__data">
            Capital gains tax statistics showing concentration by size of gain,
            inheritance tax data, personal income distributions, and tax
            receipts composition.
          </p>
          <p class="partner-card__licence">
            <span class="wl-eyebrow">Licence</span> Open Government Licence v3.0
          </p>
        </div>
        <div class="partner-card">
          <h3 class="partner-card__name">HM Land Registry</h3>
          <p class="partner-card__data">
            UK House Price Index, price paid data for property transactions, and
            overseas company ownership data for property held in England and
            Wales.
          </p>
          <p class="partner-card__licence">
            <span class="wl-eyebrow">Licence</span> Open Government Licence v3.0
          </p>
        </div>
      </div>
      <p class="partners-more">
        For the full list of datasets and their provenance, see the
        <router-link to="/methodology">Methodology</router-link> page.
      </p>
    </section>

    <hr class="wl-rule" />

    <!-- Open Source section -->
    <section class="content-section" aria-labelledby="opensource-heading">
      <h2 id="opensource-heading" class="section-heading">Open source</h2>
      <div class="section-body">
        <p>
          WealthLens UK is open-source software released under the
          <strong>MIT Licence</strong>. The entire codebase, including data
          pipelines, API, frontend, and documentation, is available on GitHub.
        </p>
        <div class="cta-row">
          <a
            href="https://github.com/Chris0Jeky/wealthlens-hq"
            target="_blank"
            rel="noopener"
            class="wl-btn"
          >
            View on GitHub
          </a>
          <a
            href="https://github.com/Chris0Jeky/wealthlens-hq/blob/main/CONTRIBUTING.md"
            target="_blank"
            rel="noopener"
            class="wl-btn wl-btn--ghost"
          >
            Contributing guide
          </a>
        </div>
      </div>
    </section>

    <hr class="wl-rule" />

    <!-- Contact section -->
    <section class="content-section" aria-labelledby="contact-heading">
      <h2 id="contact-heading" class="section-heading">Get in touch</h2>
      <div class="section-body">
        <div class="contact-grid">
          <div class="contact-item">
            <p class="wl-eyebrow">Email</p>
            <p>
              <a href="mailto:jeky.tck@gmail.com" class="contact-link">
                jeky.tck@gmail.com
              </a>
            </p>
          </div>
          <div class="contact-item">
            <p class="wl-eyebrow">Bug reports &amp; feature requests</p>
            <p>
              <a
                href="https://github.com/Chris0Jeky/wealthlens-hq/issues"
                target="_blank"
                rel="noopener"
                class="contact-link"
              >
                GitHub Issues
              </a>
            </p>
          </div>
          <div class="contact-item">
            <p class="wl-eyebrow">Source code</p>
            <p>
              <a
                href="https://github.com/Chris0Jeky/wealthlens-hq"
                target="_blank"
                rel="noopener"
                class="contact-link"
              >
                github.com/Chris0Jeky/wealthlens-hq
              </a>
            </p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* ============================================================ */
/* LAYOUT                                                        */
/* ============================================================ */
.about-page {
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
  color: var(--wl-red);
  font-weight: 600;
}
.section-body a {
  color: var(--wl-red);
  text-decoration: none;
  border-bottom: 1px solid var(--wl-red);
}
.section-body a:hover {
  border-color: var(--wl-red-deep);
}
.section-body a:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: 2px;
}

.lede {
  font-size: 22px !important;
  line-height: 1.5 !important;
  max-width: 55ch;
  margin-bottom: 24px !important;
}

/* ============================================================ */
/* VALUES GRID                                                   */
/* ============================================================ */
.values-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}
.value-card {
  background: var(--wl-card);
  border: 1px solid var(--wl-rule-strong);
  padding: 28px;
}
.value-card__title {
  font-family: var(--wl-serif);
  font-size: 20px;
  font-weight: 600;
  color: var(--wl-ink);
  margin: 0 0 12px;
  line-height: 1.2;
}
.value-card__text {
  font-size: 15px;
  line-height: 1.6;
  color: var(--wl-ink-body);
  margin: 0;
}

/* ============================================================ */
/* TEAM CARD                                                     */
/* ============================================================ */
.team-card {
  background: var(--wl-card);
  border: 1px solid var(--wl-rule-strong);
  padding: 32px;
  margin-bottom: 24px;
}
.team-card__name {
  font-family: var(--wl-serif);
  font-size: 24px;
  font-weight: 600;
  color: var(--wl-ink);
  margin: 0 0 4px;
}
.team-card__role {
  font-family: var(--wl-mono);
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--wl-red);
  font-weight: 500;
  margin: 0 0 18px;
}

.contributors-note {
  background: var(--wl-paper-tint);
  border-top: 4px solid var(--wl-red);
  padding: 24px 28px;
}
.contributors-note .wl-eyebrow {
  margin-bottom: 8px;
  color: var(--wl-red);
}
.contributors-note p {
  font-size: 15px;
  line-height: 1.6;
  color: var(--wl-ink-body);
  margin: 0 0 8px;
}
.contributors-note p:last-child {
  margin-bottom: 0;
}
.contributors-note a {
  color: var(--wl-red);
  text-decoration: none;
  border-bottom: 1px solid var(--wl-red);
}
.contributors-note a:hover {
  border-color: var(--wl-red-deep);
}
.contributors-note a:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: 2px;
}

/* ============================================================ */
/* DATA PARTNERS                                                 */
/* ============================================================ */
.partners-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}
.partner-card {
  background: var(--wl-card);
  border: 1px solid var(--wl-rule-strong);
  padding: 28px;
}
.partner-card__name {
  font-family: var(--wl-serif);
  font-size: 18px;
  font-weight: 600;
  color: var(--wl-ink);
  margin: 0 0 12px;
  line-height: 1.2;
}
.partner-card__data {
  font-size: 15px;
  line-height: 1.6;
  color: var(--wl-ink-body);
  margin: 0 0 14px;
}
.partner-card__licence {
  font-size: 13px;
  color: var(--wl-ink-muted);
  margin: 0;
}
.partner-card__licence .wl-eyebrow {
  margin-right: 6px;
}

.partners-more {
  margin-top: 24px;
  font-size: 15px;
  color: var(--wl-ink-muted);
}
.partners-more a {
  color: var(--wl-red);
  text-decoration: none;
  border-bottom: 1px solid var(--wl-red);
}
.partners-more a:hover {
  border-color: var(--wl-red-deep);
}
.partners-more a:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: 2px;
}

/* ============================================================ */
/* CTA ROW                                                       */
/* ============================================================ */
.cta-row {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-top: 8px;
}

/* ============================================================ */
/* CONTACT GRID                                                  */
/* ============================================================ */
.contact-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}
.contact-item .wl-eyebrow {
  margin-bottom: 4px;
}
.contact-item p {
  font-size: 15px !important;
  margin: 0 !important;
}
.contact-link {
  color: var(--wl-red);
  text-decoration: none;
  border-bottom: 1px solid var(--wl-red);
}
.contact-link:hover {
  border-color: var(--wl-red-deep);
}
.contact-link:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: 2px;
}

/* ============================================================ */
/* HORIZONTAL RULES                                              */
/* ============================================================ */
.about-page > .wl-rule {
  margin: 48px 32px 0;
}
.about-page > .wl-rule-red {
  margin: 0 0 0;
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

  .about-page > .wl-rule {
    margin-left: 16px;
    margin-right: 16px;
  }

  .values-grid,
  .partners-grid {
    grid-template-columns: 1fr;
  }

  .contact-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .page-header__title {
    font-size: clamp(32px, 8vw, 48px);
  }

  .section-body p,
  .lede {
    font-size: 16px !important;
  }
}
</style>
