<script setup lang="ts">
/**
 * ContributeView — ways to contribute to WealthLens UK.
 *
 * Shows contribution categories (code, data, design, content, research),
 * getting started steps, current needs, project values, and contact info.
 * Route: /contribute
 */
</script>

<template>
  <div class="contribute-page">
    <!-- Breadcrumb -->
    <nav class="crumb" aria-label="Breadcrumb">
      <ol class="crumb__list">
        <li class="crumb__item">
          <router-link to="/" class="crumb__link">Home</router-link>
          <span class="crumb__sep" aria-hidden="true">/</span>
        </li>
        <li class="crumb__item">
          <span class="crumb__current" aria-current="page">Contribute</span>
        </li>
      </ol>
    </nav>

    <div class="contribute-content">
      <!-- Welcome -->
      <section class="contribute-hero" aria-labelledby="contribute-heading">
        <span class="wl-eyebrow">Get Involved</span>
        <h1 id="contribute-heading" class="wl-h2">Contribute to WealthLens UK</h1>
        <p class="contribute-hero__intro">
          WealthLens is open-source and community-driven. Whether you write code,
          crunch data, design charts, or simply care about making wealth inequality
          visible, there is a way to help.
        </p>
      </section>

      <!-- Ways to Contribute -->
      <section class="contribute-ways" aria-labelledby="ways-heading">
        <span class="wl-eyebrow">Ways to Contribute</span>
        <h2 id="ways-heading" class="wl-h3">Pick what suits you</h2>

        <div class="ways-grid" role="list">
          <!-- Code -->
          <article class="way-card" role="listitem">
            <h3 class="way-card__title">Code</h3>
            <p class="way-card__body">
              The dashboard is built with Vue 3, TypeScript, and FastAPI (Python).
              Fix bugs, add features, improve performance, or write tests.
            </p>
            <ul class="way-card__links">
              <li>
                <a
                  href="https://github.com/Chris0Jeky/wealthlens-hq"
                  target="_blank"
                  rel="noopener"
                  class="way-card__link"
                >GitHub Repository</a>
              </li>
              <li>
                <a
                  href="https://github.com/Chris0Jeky/wealthlens-hq/blob/main/CONTRIBUTING.md"
                  target="_blank"
                  rel="noopener"
                  class="way-card__link"
                >CONTRIBUTING.md</a>
              </li>
            </ul>
          </article>

          <!-- Data -->
          <article class="way-card" role="listitem">
            <h3 class="way-card__title">Data</h3>
            <p class="way-card__body">
              Suggest new data sources, verify existing sources for accuracy,
              or help with Freedom of Information requests to uncover hidden datasets.
            </p>
            <ul class="way-card__links">
              <li>
                <a
                  href="https://github.com/Chris0Jeky/wealthlens-hq/issues/new?labels=data"
                  target="_blank"
                  rel="noopener"
                  class="way-card__link"
                >Suggest a data source</a>
              </li>
            </ul>
          </article>

          <!-- Design -->
          <article class="way-card" role="listitem">
            <h3 class="way-card__title">Design</h3>
            <p class="way-card__body">
              Help with chart design, accessibility testing, mobile UX improvements,
              or the overall visual identity of the project.
            </p>
            <ul class="way-card__links">
              <li>
                <a
                  href="https://github.com/Chris0Jeky/wealthlens-hq/issues/new?labels=design"
                  target="_blank"
                  rel="noopener"
                  class="way-card__link"
                >Open a design issue</a>
              </li>
            </ul>
          </article>

          <!-- Content -->
          <article class="way-card" role="listitem">
            <h3 class="way-card__title">Content</h3>
            <p class="way-card__body">
              Write analysis pieces, help with social media posts, suggest chart
              narratives, or improve documentation and copy.
            </p>
            <ul class="way-card__links">
              <li>
                <a
                  href="https://github.com/Chris0Jeky/wealthlens-hq/issues/new?labels=content"
                  target="_blank"
                  rel="noopener"
                  class="way-card__link"
                >Suggest content</a>
              </li>
            </ul>
          </article>

          <!-- Research -->
          <article class="way-card" role="listitem">
            <h3 class="way-card__title">Research</h3>
            <p class="way-card__body">
              Contribute academic sources, policy documents, fact-checking,
              or analysis of existing wealth data.
            </p>
            <ul class="way-card__links">
              <li>
                <a
                  href="https://github.com/Chris0Jeky/wealthlens-hq/issues/new?labels=research"
                  target="_blank"
                  rel="noopener"
                  class="way-card__link"
                >Share research</a>
              </li>
            </ul>
          </article>
        </div>
      </section>

      <hr class="wl-rule" />

      <!-- Getting Started -->
      <section class="contribute-started" aria-labelledby="started-heading">
        <span class="wl-eyebrow">Getting Started</span>
        <h2 id="started-heading" class="wl-h3">Your first contribution</h2>
        <ol class="started-steps">
          <li class="started-steps__item">
            <span class="started-steps__num">1</span>
            <div>
              <strong>Fork the repository</strong>
              <p>
                Clone
                <a
                  href="https://github.com/Chris0Jeky/wealthlens-hq"
                  target="_blank"
                  rel="noopener"
                >github.com/Chris0Jeky/wealthlens-hq</a>
                and set up your local environment.
              </p>
            </div>
          </li>
          <li class="started-steps__item">
            <span class="started-steps__num">2</span>
            <div>
              <strong>Read CONTRIBUTING.md</strong>
              <p>
                Covers branch naming, commit style, testing, and the review process.
              </p>
            </div>
          </li>
          <li class="started-steps__item">
            <span class="started-steps__num">3</span>
            <div>
              <strong>Pick a good first issue</strong>
              <p>
                Look for issues labelled
                <a
                  href="https://github.com/Chris0Jeky/wealthlens-hq/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22"
                  target="_blank"
                  rel="noopener"
                >good first issue</a>
                on GitHub.
              </p>
            </div>
          </li>
          <li class="started-steps__item">
            <span class="started-steps__num">4</span>
            <div>
              <strong>Open a pull request</strong>
              <p>
                Keep PRs small and focused. Every contribution is reviewed and appreciated.
              </p>
            </div>
          </li>
        </ol>
      </section>

      <hr class="wl-rule" />

      <!-- Current Needs -->
      <section class="contribute-needs" aria-labelledby="needs-heading">
        <span class="wl-eyebrow">Current Needs</span>
        <h2 id="needs-heading" class="wl-h3">Where help is most needed</h2>
        <ul class="needs-list">
          <li>Accessibility audit of existing charts (WCAG AA compliance)</li>
          <li>Mobile responsiveness testing on real devices</li>
          <li>Additional ONS and HMRC data sources for new chart pages</li>
          <li>Social media graphics and shareable chart images</li>
          <li>Documentation improvements and onboarding guides</li>
        </ul>
      </section>

      <hr class="wl-rule" />

      <!-- Values -->
      <section class="contribute-values" aria-labelledby="values-heading">
        <span class="wl-eyebrow">Our Values</span>
        <h2 id="values-heading" class="wl-h3">What we stand for</h2>
        <ul class="values-list">
          <li>
            <strong>Open source always</strong> — all code, data pipelines, and documentation are public.
          </li>
          <li>
            <strong>Data first, opinion second</strong> — we present sourced data, not party-political positions.
          </li>
          <li>
            <strong>Accessible by default</strong> — charts meet WCAG AA, content is plain-language, mobile-first.
          </li>
          <li>
            <strong>Independent and non-partisan</strong> — we serve the public interest, not any political party.
          </li>
        </ul>
      </section>

      <hr class="wl-rule" />

      <!-- Code of Conduct -->
      <section class="contribute-conduct" aria-labelledby="conduct-heading">
        <span class="wl-eyebrow">Community</span>
        <h2 id="conduct-heading" class="wl-h3">Code of Conduct</h2>
        <p>
          We are committed to providing a welcoming and respectful environment for
          everyone. All participants are expected to behave professionally and
          treat others with dignity. See our
          <a
            href="https://github.com/Chris0Jeky/wealthlens-hq/blob/main/CODE_OF_CONDUCT.md"
            target="_blank"
            rel="noopener"
          >Code of Conduct</a>
          for full details.
        </p>
      </section>

      <hr class="wl-rule" />

      <!-- Contact -->
      <section class="contribute-contact" aria-labelledby="contact-heading">
        <span class="wl-eyebrow">Get in Touch</span>
        <h2 id="contact-heading" class="wl-h3">Contact</h2>
        <p>
          Have questions, suggestions, or want to discuss a contribution?
        </p>
        <ul class="contact-list">
          <li>
            <strong>GitHub Issues</strong> —
            <a
              href="https://github.com/Chris0Jeky/wealthlens-hq/issues"
              target="_blank"
              rel="noopener"
            >Open an issue</a>
            for bugs, feature requests, or data suggestions.
          </li>
          <li>
            <strong>Email</strong> —
            <a href="mailto:contribute@wealthlens.uk">contribute@wealthlens.uk</a>
            for partnership enquiries or private matters.
          </li>
        </ul>

        <div class="contribute-cta">
          <a
            href="https://github.com/Chris0Jeky/wealthlens-hq"
            target="_blank"
            rel="noopener"
            class="wl-btn wl-btn--red"
          >
            View on GitHub
          </a>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.contribute-page {
  max-width: var(--wl-max);
  margin: 0 auto;
}

/* Breadcrumb */
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

/* Content */
.contribute-content {
  padding: 32px;
}

/* Hero */
.contribute-hero {
  margin-bottom: 48px;
}
.contribute-hero__intro {
  max-width: 640px;
  color: var(--wl-ink-body);
  font-size: 18px;
  line-height: 1.7;
  margin-top: 12px;
}

/* Ways to contribute grid */
.contribute-ways {
  margin-bottom: 48px;
}
.ways-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-top: 24px;
}
.way-card {
  background: var(--wl-card);
  border: 1px solid var(--wl-rule);
  border-radius: var(--wl-radius);
  padding: 24px;
  transition: box-shadow 0.15s ease;
}
.way-card:hover {
  box-shadow: var(--wl-shadow-lg);
}
.way-card__title {
  font-family: var(--wl-serif);
  font-size: 20px;
  font-weight: 600;
  color: var(--wl-ink);
  margin: 0 0 8px;
}
.way-card__body {
  color: var(--wl-ink-body);
  font-size: 14px;
  line-height: 1.6;
  margin: 0 0 12px;
}
.way-card__links {
  list-style: none;
  margin: 0;
  padding: 0;
}
.way-card__links li + li {
  margin-top: 6px;
}
.way-card__link {
  color: var(--wl-red);
  font-size: 13px;
  font-weight: 500;
  text-decoration: none;
}
.way-card__link:hover {
  text-decoration: underline;
}
.way-card__link:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: 2px;
}

/* Getting Started */
.contribute-started {
  margin: 48px 0;
}
.started-steps {
  list-style: none;
  margin: 24px 0 0;
  padding: 0;
}
.started-steps__item {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  padding: 16px 0;
  border-bottom: 1px solid var(--wl-rule);
}
.started-steps__item:last-child {
  border-bottom: none;
}
.started-steps__num {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  min-width: 32px;
  background: var(--wl-red);
  color: #fff;
  font-family: var(--wl-mono);
  font-size: 14px;
  font-weight: 600;
  border-radius: 50%;
}
.started-steps__item p {
  margin: 4px 0 0;
  color: var(--wl-ink-muted);
  font-size: 14px;
  line-height: 1.5;
}
.started-steps__item a {
  color: var(--wl-red);
  text-decoration: none;
}
.started-steps__item a:hover {
  text-decoration: underline;
}

/* Current Needs */
.contribute-needs {
  margin: 48px 0;
}
.needs-list {
  margin: 16px 0 0;
  padding-left: 20px;
  color: var(--wl-ink-body);
  font-size: 15px;
  line-height: 1.8;
}

/* Values */
.contribute-values {
  margin: 48px 0;
}
.values-list {
  list-style: none;
  margin: 16px 0 0;
  padding: 0;
}
.values-list li {
  padding: 10px 0;
  border-bottom: 1px solid var(--wl-rule);
  color: var(--wl-ink-body);
  font-size: 15px;
  line-height: 1.6;
}
.values-list li:last-child {
  border-bottom: none;
}

/* Code of Conduct */
.contribute-conduct {
  margin: 48px 0;
}
.contribute-conduct p {
  color: var(--wl-ink-body);
  font-size: 15px;
  line-height: 1.7;
  margin-top: 8px;
}
.contribute-conduct a {
  color: var(--wl-red);
  text-decoration: none;
}
.contribute-conduct a:hover {
  text-decoration: underline;
}

/* Contact */
.contribute-contact {
  margin: 48px 0;
}
.contribute-contact p {
  color: var(--wl-ink-body);
  font-size: 15px;
  line-height: 1.7;
  margin-top: 8px;
}
.contact-list {
  list-style: none;
  margin: 16px 0 0;
  padding: 0;
}
.contact-list li {
  padding: 8px 0;
  font-size: 15px;
  color: var(--wl-ink-body);
}
.contact-list a {
  color: var(--wl-red);
  text-decoration: none;
}
.contact-list a:hover {
  text-decoration: underline;
}
.contribute-cta {
  margin-top: 32px;
}

/* Section spacing for headings */
.contribute-content .wl-h3 {
  margin: 8px 0 0;
}
.contribute-content .wl-eyebrow {
  display: block;
}

/* Responsive */
@media (max-width: 768px) {
  .crumb {
    padding-left: 16px;
    padding-right: 16px;
  }
  .contribute-content {
    padding: 24px 16px;
  }
  .ways-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .contribute-hero__intro {
    font-size: 16px;
  }
  .way-card {
    padding: 16px;
  }
}
</style>
