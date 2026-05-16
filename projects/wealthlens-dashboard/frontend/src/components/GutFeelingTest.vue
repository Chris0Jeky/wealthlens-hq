<script setup lang="ts">
/**
 * GutFeelingTest — interactive reveal grid of 8 inequality facts.
 *
 * Each card displays a relatable sentence (italic serif question) with
 * a "Tap to see the number" hint. On click or Enter/Space, the card
 * reveals the official statistic, an explanation, and a source citation.
 * The question text gets a strikethrough when revealed.
 *
 * All statistics are sourced from official UK data — see each card's
 * `src` field for the citation.
 */
import { reactive } from 'vue'

/* ------------------------------------------------------------------ */
/* Data types                                                          */
/* ------------------------------------------------------------------ */

/** A stat segment: plain string or a red-highlighted percentage/value. */
interface StatSegment {
  text: string
  pct?: boolean
}

interface GutCard {
  n: string
  q: string
  stat: StatSegment[]
  body: string
  src: string
}

/* ------------------------------------------------------------------ */
/* GUT_CARDS — all 8 entries with exact text from design reference     */
/* ------------------------------------------------------------------ */

const GUT_CARDS: GutCard[] = [
  {
    n: '01',
    q: 'Everyone I know is renting at thirty‑five.',
    stat: [{ text: '36 years.' }],
    body: 'Median age of a UK first‑time buyer in 2024 — up from 24 in 1981. Twelve extra years renting before you start to own anything. Twelve years of saving for a deposit while the deposit keeps moving. Roughly £180,000 paid to someone else.',
    src: 'Source: UK Finance · ONS Housing Survey',
  },
  {
    n: '02',
    q: 'I work full‑time. I still can’t save.',
    stat: [{ text: '16 years' }, { text: ' flat.', pct: true }],
    body: 'Real UK wages have not grown since 2008 — the only G7 economy where this is true. Your salary buys what your older sister’s did. Your rent does not. Your weekly shop does not. The deposit does not.',
    src: 'Source: ONS AWE, CPIH‑deflated · IFS Living Standards',
  },
  {
    n: '03',
    q: 'Money seems to be taxed less than work.',
    stat: [
      { text: '10%', pct: true },
      { text: ' vs ' },
      { text: '47%', pct: true },
      { text: '.' },
    ],
    body: 'Top capital‑gains rate vs top income‑tax rate. Inheriting £325,000 is taxed at 0%. Earning that same £325,000 is taxed at roughly £130,000. Britain prices effort higher than luck — by design.',
    src: 'Source: HMRC · Warwick Wealth Tax Commission 2020',
  },
  {
    n: '04',
    q: 'Half my pay goes on rent before I’ve eaten.',
    stat: [{ text: '41%', pct: true }, { text: ' on rent.' }],
    body: 'Pre‑tax income paid in rent by London renters aged 25‑34. The WHO calls anything over 30% “housing stress.” It’s also the deposit you’re not saving, the pension you’re not topping up, the year off you’ll never take, the family you keep postponing.',
    src: 'Source: ONS Private Rental Market 2024',
  },
  {
    n: '05',
    q: 'My future depends on whether my parents own a house.',
    stat: [{ text: '£100bn', pct: true }, { text: ' a year.' }],
    body: 'Forecast annual inheritance transfer in the UK by 2040. Only 4–5% of estates pay any tax — the threshold hasn’t moved since 2009. Britain is quietly becoming a hereditary economy. Whose parents you have decides whose life you get.',
    src: 'Source: HMRC IHT · Resolution Foundation 2024',
  },
  {
    n: '06',
    q: 'London might as well be a different country.',
    stat: [
      { text: '£79.5k', pct: true },
      { text: ' vs ' },
      { text: '£14.2k', pct: true },
      { text: '.' },
    ],
    body: 'Gross disposable income per head, Westminster vs Blackpool. Same currency. Same passport. Same NHS, in theory. Your postcode at 18 forecasts your retirement at 67 better than your A‑levels do.',
    src: 'Source: ONS Regional GDHI 2023',
  },
  {
    n: '07',
    q: 'I’ll still be paying rent when I retire.',
    stat: [{ text: '1 in 3' }, { text: ' renters at 70.', pct: true }],
    body: 'Projected share of UK pensioners in private rentals by 2040 — roughly triple today’s. Renting in your seventies, when your wages are gone but your landlord is not. The state pension does not stretch to a London tenancy.',
    src: 'Source: Resolution Foundation Housing Outlook 2024',
  },
  {
    n: '08',
    q: 'My kids will live with us until they’re thirty.',
    stat: [{ text: '4.9 million', pct: true }, { text: ' adults.' }],
    body: 'UK adults aged 20‑34 still living with parents — up 55% since 2000. Not because anyone is closer. Because the next flat costs three times what the spare room costs (£0), and the family they wanted gets paused with it.',
    src: 'Source: ONS Young Adults Living With Parents 2024',
  },
]

/* ------------------------------------------------------------------ */
/* Revealed state                                                      */
/* ------------------------------------------------------------------ */

const revealed = reactive<Record<string, boolean>>({})

function toggleCard(n: string): void {
  revealed[n] = !revealed[n]
}

function handleKeydown(event: KeyboardEvent, n: string): void {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault()
    toggleCard(n)
  }
}
</script>

<template>
  <section
    id="gut"
    class="gut"
    data-screen-label="01 Landing — Gut test"
    aria-labelledby="gut-heading"
  >
    <div class="gut-inner">
      <!-- Section header -->
      <div class="gut-head">
        <div>
          <p class="gut-eyebrow">&darr; The gut&#x2011;feeling test</p>
          <h2 id="gut-heading" class="gut-title">
            Eight sentences. Eight numbers.
            <em>Tap to see how right you are.</em>
          </h2>
        </div>
        <p class="gut-lead">
          Each card is a sentence you've probably said to a friend this year.
          Tap it. The official figure underneath &mdash; and the cost it carries
          forward &mdash; will not surprise you.
        </p>
      </div>

      <!-- Card grid -->
      <div class="gut-grid">
        <div
          v-for="card in GUT_CARDS"
          :key="card.n"
          class="gut-card"
          :class="{ revealed: revealed[card.n] }"
          role="button"
          :tabindex="0"
          :aria-expanded="revealed[card.n] ?? false"
          :aria-label="`Question ${card.n}: ${card.q}`"
          @click="toggleCard(card.n)"
          @keydown="handleKeydown($event, card.n)"
        >
          <span class="gut-card-num">{{ card.n }}</span>

          <p class="gut-card-q">{{ card.q }}</p>

          <!-- Answer (shown on reveal) -->
          <div class="gut-answer" :aria-hidden="!revealed[card.n]">
            <div class="gut-answer-stat">
              <template v-for="(seg, i) in card.stat" :key="i">
                <span v-if="seg.pct" class="pct">{{ seg.text }}</span>
                <template v-else>{{ seg.text }}</template>
              </template>
            </div>
            <p class="gut-answer-body">{{ card.body }}</p>
            <div class="gut-answer-src">{{ card.src }}</div>
          </div>

          <!-- Hint (hidden on reveal) -->
          <span class="gut-hint">&darr; Tap to see the number</span>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* ============================================================
   GUT-FEELING TEST — interactive reveal grid
   ============================================================ */
.gut {
  padding: 80px 0;
  background: var(--wl-bg);
  border-bottom: 1px solid var(--wl-ink);
}

.gut-inner {
  max-width: var(--wl-max);
  margin: 0 auto;
  padding: 0 32px;
}

/* --- Section header ----------------------------------------- */
.gut-head {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 24px;
  align-items: end;
  margin-bottom: 40px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--wl-rule);
}

.gut-eyebrow {
  font-family: var(--wl-mono);
  font-size: 11px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--wl-red);
  font-weight: 600;
  margin: 0 0 12px;
}

.gut-title {
  font-family: var(--wl-serif);
  font-size: clamp(36px, 4.5vw, 56px);
  line-height: 1.02;
  letter-spacing: -0.02em;
  font-weight: 600;
  color: var(--wl-ink);
  margin: 0;
  max-width: 22ch;
  text-wrap: balance;
}

.gut-title em {
  font-style: italic;
  color: var(--wl-red);
  font-weight: 500;
}

.gut-lead {
  font-size: 15px;
  color: var(--wl-ink-muted);
  max-width: 32ch;
  line-height: 1.5;
  margin: 0;
}

/* --- Card grid ---------------------------------------------- */
.gut-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1px;
  background: var(--wl-ink);
  border: 1px solid var(--wl-ink);
}

/* --- Individual card ---------------------------------------- */
.gut-card {
  background: var(--wl-card);
  padding: 32px;
  cursor: pointer;
  position: relative;
  min-height: 240px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  transition: background 0.2s ease;
}

.gut-card:hover {
  background: var(--wl-paper-tint);
}

.gut-card:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: -2px;
  z-index: 1;
}

.gut-card.revealed {
  background: var(--wl-paper-tint);
}

/* --- Card number -------------------------------------------- */
.gut-card-num {
  font-family: var(--wl-mono);
  font-size: 11px;
  letter-spacing: 0.14em;
  color: var(--wl-ink-muted);
}

/* --- Question text ------------------------------------------ */
.gut-card-q {
  font-family: var(--wl-serif);
  font-size: 26px;
  line-height: 1.2;
  letter-spacing: -0.012em;
  color: var(--wl-ink);
  font-weight: 500;
  font-style: italic;
  max-width: 24ch;
  margin: 0;
}

.gut-card.revealed .gut-card-q {
  color: var(--wl-ink-muted);
  text-decoration: line-through;
  text-decoration-color: var(--wl-rule-strong);
  text-decoration-thickness: 1px;
}

/* --- Hint (pre-reveal) -------------------------------------- */
.gut-hint {
  margin-top: auto;
  font-family: var(--wl-mono);
  font-size: 11px;
  color: var(--wl-red);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.gut-card.revealed .gut-hint {
  display: none;
}

/* --- Answer (post-reveal) ----------------------------------- */
.gut-answer {
  display: none;
  border-top: 1px solid var(--wl-rule);
  padding-top: 18px;
}

.gut-card.revealed .gut-answer {
  display: block;
  animation: gut-punch-in 0.45s cubic-bezier(0.22, 0.7, 0.18, 1);
}

@keyframes gut-punch-in {
  0% {
    transform: translateY(8px) scale(0.96);
    opacity: 0;
  }
  60% {
    transform: translateY(0) scale(1.015);
    opacity: 1;
  }
  100% {
    transform: translateY(0) scale(1);
    opacity: 1;
  }
}

.gut-answer-stat {
  font-family: var(--wl-serif);
  font-size: 36px;
  line-height: 1.05;
  letter-spacing: -0.02em;
  font-weight: 600;
  color: var(--wl-ink);
  margin: 0 0 8px;
}

.gut-answer-stat .pct {
  color: var(--wl-red);
}

.gut-answer-body {
  font-size: 14px;
  color: var(--wl-ink-body);
  line-height: 1.5;
  margin: 0;
}

.gut-answer-src {
  font-family: var(--wl-mono);
  font-size: 10px;
  color: var(--wl-ink-muted);
  letter-spacing: 0.06em;
  margin-top: 8px;
}

/* --- Responsive --------------------------------------------- */
@media (max-width: 768px) {
  .gut {
    padding: 48px 0;
  }

  .gut-inner {
    padding: 0 16px;
  }

  .gut-head {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .gut-lead {
    max-width: none;
  }

  .gut-grid {
    grid-template-columns: 1fr;
  }

  .gut-card {
    padding: 24px;
    min-height: 180px;
  }

  .gut-card-q {
    font-size: 22px;
    max-width: none;
  }

  .gut-answer-stat {
    font-size: 28px;
  }
}
</style>
