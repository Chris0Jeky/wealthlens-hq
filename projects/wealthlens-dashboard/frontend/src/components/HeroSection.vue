<script setup lang="ts">
/**
 * HeroSection — the "front page" hero for WealthLens UK.
 *
 * Displays a rotating serif headline, sub-paragraph with rich text,
 * action buttons, and a source citation. The right column hosts the
 * WealthFlowSankey visualisation.
 *
 * Headline rotation: cycles through five data-driven headlines on a
 * 12-second interval. The current index is exposed so parent components
 * or tweaks panels can override it.
 *
 * Data sources cited inline per headline.
 */
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import WealthFlowSankey from './WealthFlowSankey.vue'

/* ------------------------------------------------------------------ */
/* Headline data — second-order consequences, not just facts.         */
/* ------------------------------------------------------------------ */

/** A segment of the headline: plain string or italic emphasis. */
interface HeadlineSegment {
  text: string
  italic?: boolean
}

interface Headline {
  label: string
  segments: HeadlineSegment[]
  sub: string
  source: string
}

const HEADLINES: Headline[] = [
  {
    label: 'Cascade',
    segments: [
      { text: 'Everything in your life is ' },
      { text: 'ten years late', italic: true },
      { text: '.' },
    ],
    sub: `Your parents bought a house at 24. Had you at 27. You'll be lucky to buy at 36 — if at all. So the family waits. The retirement waits. And in that twelve‑year gap, roughly <strong>£180,000 of your wages becomes someone else's mortgage</strong>. <span class="hero-sub-red">The clock didn't break. It was moved.</span>`,
    source: 'Source: UK Finance first‑time buyer age · ONS House Price Index · IFS 2024',
  },
  {
    label: 'Rent',
    segments: [
      { text: "You'll pay for " },
      { text: 'three houses', italic: true },
      { text: ". You'll own none." },
    ],
    sub: `Forty years of renting in a UK city ≈ <strong>£540,000</strong> in today's money. That's three average UK homes. It doesn't disappear — it becomes someone else's pension, someone else's holiday villa, someone else's child's deposit. <span class="hero-sub-red">Renting isn't a service. It's a transfer.</span>`,
    source: 'Source: ONS Private Rental Market 2024 · HM Land Registry',
  },
  {
    label: 'Wages',
    segments: [
      { text: 'Your job pays what it did in ' },
      { text: '2008', italic: true },
      { text: ". Life doesn't." },
    ],
    sub: `Real wages haven't grown in 16 years — Britain is the <strong>only G7 economy</strong> where this happened. Rent didn't sit still. Childcare didn't. Energy didn't. <span class="hero-sub-red">You're not bad with money. The maths was rewritten while you weren't looking.</span>`,
    source: 'Source: ONS AWE deflated by CPIH · IFS Living Standards 2024',
  },
  {
    label: 'Inheritance',
    segments: [
      { text: 'By 2040, Britain will be ' },
      { text: 'inherited', italic: true },
      { text: ', not earned.' },
    ],
    sub: `£100 billion a year transferred through estates — and rising. If your parents own, you're set. If they don't, you're not, no matter the hours. <strong>Only 4–5% of estates pay any tax</strong> — the threshold hasn't moved since 2009. <span class="hero-sub-red">"Hard work pays" used to be a promise. It's a lottery ticket.</span>`,
    source: 'Source: HMRC IHT statistics · Resolution Foundation 2024',
  },
  {
    label: 'Tax',
    segments: [
      { text: 'Britain taxes the ' },
      { text: 'alarm clock', italic: true },
      { text: '. Not the inheritance.' },
    ],
    sub: `Wages from work: up to <strong>47%</strong>. Capital gains: 10–28%. Inheritance under £325k: <strong>0%</strong>. The system charges you most for the one thing you actually control — your time. <span class="hero-sub-red">Effort is taxed. Luck is not.</span>`,
    source: 'Source: HMRC · IFS Tax Analysis 2024',
  },
]

/* ------------------------------------------------------------------ */
/* Headline rotation                                                   */
/* ------------------------------------------------------------------ */

const currentIndex = ref(0)
let rotationTimer: ReturnType<typeof setInterval> | null = null

const headline = computed(() => HEADLINES[currentIndex.value])

function nextHeadline() {
  currentIndex.value = (currentIndex.value + 1) % HEADLINES.length
}

onMounted(() => {
  rotationTimer = setInterval(nextHeadline, 12_000)
})

onUnmounted(() => {
  if (rotationTimer) clearInterval(rotationTimer)
})
</script>

<template>
  <section class="hero" aria-labelledby="hero-heading">
    <div class="hero-inner">
      <!-- Left column: text -->
      <div class="hero-text">
        <p class="hero-byline">
          <span class="hero-byline-red" aria-hidden="true">&#x25CF;</span>
          <span class="hero-byline-red"> The front page</span>
          <span class="hero-byline-sep" aria-hidden="true"></span>
          <span>Britain &middot; 2026</span>
          <span class="hero-byline-sep" aria-hidden="true"></span>
          <span>By the numbers</span>
        </p>

        <h1 id="hero-heading" class="hero-headline">
          <template v-for="(seg, i) in headline.segments" :key="i">
            <em v-if="seg.italic">{{ seg.text }}</em>
            <template v-else>{{ seg.text }}</template>
          </template>
        </h1>

        <!-- eslint-disable-next-line vue/no-v-html -- trusted static content -->
        <p class="hero-sub" v-html="headline.sub"></p>

        <div class="hero-actions">
          <RouterLink to="/charts/wealth-shares" class="wl-btn wl-btn--red">
            See where it went &rarr;
          </RouterLink>
          <a href="#gut" class="wl-btn wl-btn--ghost">
            Take the gut&#x2011;feeling test
          </a>
        </div>

        <div class="hero-meta">
          <span>{{ headline.source }}</span>
        </div>
      </div>

      <!-- Right column: wealth flow Sankey -->
      <WealthFlowSankey />
    </div>
  </section>
</template>

<style scoped>
/* ============================================================
   HERO — the front page
   ============================================================ */
.hero {
  position: relative;
  padding: 64px 0 0;
  border-bottom: 1px solid var(--wl-ink);
  overflow: hidden;
}

.hero-inner {
  max-width: var(--wl-max);
  margin: 0 auto;
  padding: 0 32px;
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 56px;
  align-items: start;
}

/* --- Byline ------------------------------------------------- */
.hero-byline {
  font-family: var(--wl-mono);
  font-size: 11px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--wl-ink-muted);
  margin: 0 0 18px;
  display: flex;
  gap: 18px;
  align-items: center;
  flex-wrap: wrap;
}

.hero-byline-red {
  color: var(--wl-red);
  font-weight: 600;
  letter-spacing: 0.18em;
}

.hero-byline-sep {
  width: 4px;
  height: 4px;
  background: var(--wl-rule-strong);
  border-radius: 50%;
}

/* --- Headline ----------------------------------------------- */
.hero-headline {
  font-family: var(--wl-serif);
  font-size: clamp(48px, 6.2vw, 92px);
  line-height: 0.96;
  letter-spacing: -0.028em;
  font-weight: 600;
  color: var(--wl-ink);
  margin: 0 0 28px;
  max-width: 14ch;
  text-wrap: balance;
}

.hero-headline em {
  font-style: italic;
  color: var(--wl-red);
  font-weight: 500;
}

/* --- Sub-paragraph ------------------------------------------ */
.hero-sub {
  font-size: 19px;
  line-height: 1.5;
  color: var(--wl-ink-body);
  max-width: 44ch;
  margin: 0 0 36px;
  font-weight: 400;
}

/* v-html injects these class names */
.hero-sub :deep(strong) {
  color: var(--wl-ink);
  font-weight: 600;
  background: var(--wl-red-soft);
  padding: 1px 4px;
}

.hero-sub :deep(.hero-sub-red) {
  color: var(--wl-red);
  font-weight: 600;
}

/* --- Action buttons ----------------------------------------- */
.hero-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
  padding-bottom: 36px;
}

/* --- Source citation ----------------------------------------- */
.hero-meta {
  margin-top: 28px;
  padding-top: 18px;
  border-top: 1px solid var(--wl-rule);
  font-family: var(--wl-mono);
  font-size: 11px;
  color: var(--wl-ink-muted);
  letter-spacing: 0.04em;
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

/* --- Responsive --------------------------------------------- */
@media (max-width: 768px) {
  .hero {
    padding: 36px 0 0;
  }

  .hero-inner {
    grid-template-columns: 1fr;
    gap: 32px;
    padding: 0 16px;
  }

  .hero-headline {
    font-size: clamp(36px, 8vw, 56px);
    max-width: none;
  }

  .hero-sub {
    font-size: 16px;
    max-width: none;
  }

  .hero-byline {
    font-size: 10px;
    gap: 10px;
  }
}
</style>
