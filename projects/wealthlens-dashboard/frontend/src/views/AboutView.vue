<script setup lang="ts">
/**
 * AboutView — project methodology, data sources, and limitations.
 * Provides transparency about where the data comes from and how it is used.
 */
import { usePageMeta } from "@/composables/usePageMeta"

usePageMeta({
  title: "About",
  description:
    "About WealthLens UK — our mission, data sources, methodology, limitations, and open-source commitment.",
  url: "https://chris0jeky.github.io/wealthlens-hq/about",
  image: "https://chris0jeky.github.io/wealthlens-hq/og/og-landing.png",
  imageAlt: "WealthLens UK — About the project",
})
</script>

<template>
  <article class="max-w-3xl mx-auto px-6 py-12">
    <h1 class="text-3xl font-bold tracking-tight mb-8">About WealthLens UK</h1>

    <!-- Mission -->
    <section class="mb-10">
      <h2 class="text-xl font-semibold mb-3">Mission</h2>
      <p class="text-gray-700 leading-relaxed">
        WealthLens UK is an open-source project making UK wealth inequality data visible,
        interactive, and impossible to ignore. We believe public data should be publicly accessible
        — not buried in spreadsheets or hidden behind paywalls.
      </p>
    </section>

    <!-- Data Sources -->
    <section class="mb-10">
      <h2 class="text-xl font-semibold mb-3">Data Sources</h2>
      <p class="text-gray-700 leading-relaxed mb-4">
        All data is sourced from official government and academic publications. Key datasets are
        cited below; the full
        <RouterLink to="/data-sources" class="text-blue-600 underline">Data Sources</RouterLink>
        page lists every dataset with its source URL and the date it was accessed.
      </p>
      <ul class="space-y-4">
        <li class="border-l-4 border-blue-500 pl-4">
          <p class="font-medium">World Inequality Database (WID.world)</p>
          <p class="text-sm text-gray-600">
            Provides: Top 1% and top 10% wealth shares in Great Britain
          </p>
          <p class="text-sm text-gray-600">
            URL:
            <a
              href="https://wid.world/"
              target="_blank"
              rel="noopener"
              class="text-blue-600 hover:underline"
              >https://wid.world/</a
            >
          </p>
          <p class="text-sm text-gray-500">Accessed: 2026-05-14</p>
        </li>
        <li class="border-l-4 border-blue-500 pl-4">
          <p class="font-medium">ONS — Housing Affordability</p>
          <p class="text-sm text-gray-600">
            Provides: House price to workplace-based earnings ratio by region (lower quartile and
            median)
          </p>
          <p class="text-sm text-gray-600">
            URL:
            <a
              href="https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/ratioofhousepricetoworkplacebasedearningslowerquartileandmedian"
              target="_blank"
              rel="noopener"
              class="text-blue-600 hover:underline"
              >ons.gov.uk &mdash; Housing affordability</a
            >
          </p>
          <p class="text-sm text-gray-500">Accessed: 2026-05-14</p>
        </li>
        <li class="border-l-4 border-blue-500 pl-4">
          <p class="font-medium">ONS — Wealth and Assets Survey</p>
          <p class="text-sm text-gray-600">Provides: Total net wealth by decile in Great Britain</p>
          <p class="text-sm text-gray-600">
            URL:
            <a
              href="https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/datasets/totalwealthwealthingreatbritain"
              target="_blank"
              rel="noopener"
              class="text-blue-600 hover:underline"
              >ons.gov.uk &mdash; Total Wealth in Great Britain</a
            >
          </p>
          <p class="text-sm text-gray-500">Accessed: 2026-05-14</p>
        </li>
        <li class="border-l-4 border-blue-500 pl-4">
          <p class="font-medium">HMRC — Capital Gains Tax Statistics</p>
          <p class="text-sm text-gray-600">Provides: Capital gains concentration by size of gain</p>
          <p class="text-sm text-gray-600">
            URL:
            <a
              href="https://www.gov.uk/government/statistics/capital-gains-tax-statistics"
              target="_blank"
              rel="noopener"
              class="text-blue-600 hover:underline"
              >gov.uk &mdash; Capital Gains Tax Statistics</a
            >
          </p>
          <p class="text-sm text-gray-500">Accessed: 2026-05-14</p>
        </li>
      </ul>
    </section>

    <!-- Methodology -->
    <section class="mb-10">
      <h2 class="text-xl font-semibold mb-3">Methodology</h2>
      <p class="text-gray-700 leading-relaxed">
        Data is sourced directly from official government and academic publications. Raw datasets
        are downloaded and processed into clean CSV files via reproducible Python scripts. The
        backend API serves this processed data to the frontend, which renders interactive charts.
        Most charts present the published figures as-is; where a chart applies inflation adjustment
        (real terms), clearly-marked projections, or an illustrative composite while live data is
        unavailable, that is stated in the chart's own methodology section.
      </p>
    </section>

    <!-- Limitations -->
    <section class="mb-10">
      <h2 class="text-xl font-semibold mb-3">Limitations</h2>
      <ul class="list-disc pl-5 space-y-2 text-gray-700">
        <li>
          Data coverage varies between sources — some datasets cover Great Britain only, others
          England and Wales.
        </li>
        <li>
          Survey-based data (such as the Wealth and Assets Survey) is subject to sampling
          limitations and may understate extreme wealth.
        </li>
        <li>
          Wealth can be hidden, held offshore, or structured through trusts, meaning official
          figures likely underestimate true concentration.
        </li>
        <li>Time periods differ between datasets; not all sources update at the same frequency.</li>
        <li>
          This project presents data, not policy recommendations. Interpretation is left to the
          reader.
        </li>
      </ul>
    </section>

    <!-- Open Source -->
    <section class="mb-10">
      <h2 class="text-xl font-semibold mb-3">Open Source</h2>
      <p class="text-gray-700 leading-relaxed">
        WealthLens UK is fully open source. All code, data pipelines, and documentation are
        available on GitHub.
      </p>
      <p class="mt-3">
        <a
          href="https://github.com/Chris0Jeky/wealthlens-hq"
          target="_blank"
          rel="noopener"
          class="inline-flex items-center gap-2 text-blue-600 hover:underline font-medium"
        >
          github.com/Chris0Jeky/wealthlens-hq
        </a>
      </p>
      <p class="text-sm text-gray-500 mt-2">
        Contributions, corrections, and suggestions are welcome.
      </p>
    </section>
  </article>
</template>
