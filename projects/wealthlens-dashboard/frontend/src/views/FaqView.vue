<script setup lang="ts">
import Accordion from "@/components/Accordion.vue";

interface GlossaryEntry {
  term: string;
  definition: string;
}

const faqs = [
  {
    question: "Where does the data come from?",
    answer:
      "All data comes from official government publications: the Office for National Statistics (ONS), HM Revenue & Customs (HMRC), the World Inequality Database (WID.world), and the Bank of England. Every chart cites its primary source with a URL and access date.",
  },
  {
    question: "How often is the data updated?",
    answer:
      "It depends on the dataset. ONS Wealth and Assets Survey publishes roughly every two years. HMRC statistics are annual. Bank of England rates are updated monthly. Each chart shows when its data was last refreshed.",
  },
  {
    question: "Why do wealth figures differ between sources?",
    answer:
      "Different organisations measure wealth differently. The ONS Wealth and Assets Survey uses household surveys (which tend to under-report the very wealthy). The World Inequality Database uses tax records and national accounts to estimate top wealth shares. We show which source each chart uses.",
  },
  {
    question: "Is this site affiliated with a political party?",
    answer:
      "No. WealthLens UK is independent and non-partisan. We present data from official sources and let the numbers speak for themselves. We do not endorse any political party or policy position.",
  },
  {
    question: "Can I use these charts in my own work?",
    answer:
      "Yes. All code is MIT-licensed and all charts are available under CC-BY 4.0. You can embed, screenshot, or adapt any chart as long as you credit WealthLens UK and the original data source.",
  },
  {
    question: "How can I contribute?",
    answer:
      "WealthLens UK is open-source. You can contribute code, data pipelines, accessibility improvements, or new chart ideas via GitHub. See our Contributing page for details.",
  },
  {
    question: "Why does the wealth data only go up to 2020?",
    answer:
      "The most recent ONS Wealth and Assets Survey covers April 2018 to March 2020 (Round 7). Round 8 data collection was delayed by COVID-19. We update charts as new rounds are published.",
  },
  {
    question: "What does 'real terms' mean on wage charts?",
    answer:
      "Real terms means adjusted for inflation (using CPI). A wage figure 'in real terms' shows what the money is actually worth in today's purchasing power, removing the effect of price increases over time.",
  },
] as const;

const glossary: GlossaryEntry[] = [
  { term: "Decile", definition: "One-tenth of a population when sorted by a measure (e.g., wealth). The bottom decile is the poorest 10%, the top decile is the richest 10%." },
  { term: "Percentile", definition: "One-hundredth of a population. Being in the 90th percentile means you have more than 90% of the population." },
  { term: "Net wealth", definition: "Total assets (property, pensions, savings, possessions) minus total debts (mortgages, loans, credit cards)." },
  { term: "Household wealth", definition: "The combined net wealth of everyone living in a household. Most UK wealth surveys measure at the household level." },
  { term: "Median", definition: "The middle value when all values are sorted. Half the population is above, half below. Less affected by extreme values than the mean." },
  { term: "Gini coefficient", definition: "A measure of inequality from 0 (perfect equality) to 1 (one person owns everything). The UK's wealth Gini is approximately 0.63." },
  { term: "CPI (Consumer Price Index)", definition: "A measure of inflation tracking the cost of a basket of goods and services. Used to convert nominal values to real terms." },
  { term: "Capital gains", definition: "Profit from selling an asset (property, shares, etc.) for more than you paid. Taxed at lower rates than income in the UK." },
  { term: "Inheritance Tax (IHT)", definition: "A 40% tax on estates above £325,000 (with a £175,000 residence nil-rate band). Only about 4-5% of deaths result in an IHT charge." },
  { term: "Wealth and Assets Survey (WAS)", definition: "The ONS's main survey measuring household wealth in Great Britain. Covers financial, property, pension, and physical wealth." },
  { term: "WID (World Inequality Database)", definition: "An academic database combining tax records and national accounts to estimate wealth and income distributions globally." },
  { term: "ASHE", definition: "Annual Survey of Hours and Earnings. The ONS's main source for earnings data, covering 1% of all UK employees via PAYE records." },
];
</script>

<template>
  <article class="max-w-3xl mx-auto px-6 py-12">
    <h1 class="text-3xl font-bold tracking-tight mb-2 dark:text-gray-100">FAQ & Glossary</h1>
    <p class="text-gray-600 dark:text-gray-400 mb-10">
      Common questions about the data and key terms used across the site.
    </p>

    <!-- FAQ Section -->
    <section class="mb-14">
      <h2 class="text-xl font-semibold mb-6 dark:text-gray-100">Frequently Asked Questions</h2>
      <div class="divide-y divide-gray-200 dark:divide-gray-700 border-t border-gray-200 dark:border-gray-700">
        <Accordion
          v-for="(item, index) in faqs"
          :key="index"
          :title="item.question"
        >
          <p class="leading-relaxed">{{ item.answer }}</p>
        </Accordion>
      </div>
    </section>

    <!-- Glossary Section -->
    <section>
      <h2 class="text-xl font-semibold mb-6 dark:text-gray-100">Glossary</h2>
      <dl class="space-y-4">
        <div
          v-for="entry in glossary"
          :key="entry.term"
          class="border-l-4 border-gray-300 dark:border-gray-600 pl-4"
        >
          <dt class="font-semibold text-gray-900 dark:text-gray-100">{{ entry.term }}</dt>
          <dd class="text-gray-700 dark:text-gray-400 text-sm leading-relaxed mt-1">
            {{ entry.definition }}
          </dd>
        </div>
      </dl>
    </section>
  </article>
</template>
