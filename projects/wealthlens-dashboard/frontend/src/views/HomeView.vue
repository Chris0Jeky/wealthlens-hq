<script setup lang="ts">
/**
 * HomeView — the WealthLens UK front page.
 *
 * Composes all landing page sections in order:
 * 1. HeroSection — rotating headlines + wealth flow Sankey
 * 2. RentTicker — live rent counter
 * 3. GutFeelingTest — 8-card interactive reveal grid
 * 4. TwoBritains — perspective split comparison
 * 5. FivePillars — 5-column structural inequality grid
 * 6. FeaturedChart — wealth shares time series (raw SVG)
 * 7. SourcesStrip — data provenance band
 * 8. MissionSection — project identity and stats
 * 9. CtaSection — final call-to-action
 */
import HeroSection from '@/components/HeroSection.vue'
import RentTicker from '@/components/RentTicker.vue'
import GutFeelingTest from '@/components/GutFeelingTest.vue'
import TwoBritains from '@/components/TwoBritains.vue'
import FivePillars from '@/components/FivePillars.vue'
import FeaturedChart from '@/components/FeaturedChart.vue'
import SourcesStrip from '@/components/SourcesStrip.vue'
import MissionSection from '@/components/MissionSection.vue'
import CtaSection from '@/components/CtaSection.vue'
</script>

<template>
  <div>
    <HeroSection />
    <RentTicker />
    <GutFeelingTest />
    <TwoBritains />
    <FivePillars />
    <FeaturedChart />
    <SourcesStrip />
    <MissionSection />
    <CtaSection />
  </div>
</template>
