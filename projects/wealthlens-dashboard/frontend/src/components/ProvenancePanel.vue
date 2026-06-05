<script setup lang="ts">
/**
 * ProvenancePanel — renders the modelling assumptions a scenario consumed, with
 * their source label and clickable citation links.
 *
 * This is the user-facing payoff of the assumption-registry citation URLs: every
 * published figure traces to a peer-reviewed paper or official statistic, and the
 * reader can follow the link. Citations open via {@link ExternalLink} (safe-href
 * guard, `rel="noopener noreferrer"`, an accessible "opens in new tab" hint).
 */
import { computed } from 'vue'
import ExternalLink from '@/components/ExternalLink.vue'
import type { ConsumedAssumption } from '@/types/simulator'

const props = defineProps<{
  assumptions: ConsumedAssumption[]
}>()

// Stable, deterministic order by id. Robust to an absent/empty list so a partial
// payload never throws (the scenario page already guards malformed contracts).
const sorted = computed(() =>
  [...(props.assumptions ?? [])].sort((a, b) =>
    a.assumption_id.localeCompare(b.assumption_id),
  ),
)

/**
 * Concise label for a citation link: the host without a leading `www.`. The link
 * purpose is still clear from the source text it sits under (WCAG 2.4.4, in
 * context), so two links to the same host need no extra disambiguation.
 */
function hostLabel(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, '')
  } catch {
    return url
  }
}
</script>

<template>
  <section
    v-if="sorted.length"
    aria-labelledby="provenance-heading"
    class="mt-8 border-t border-wl-rule pt-6"
  >
    <h2 id="provenance-heading" class="text-base font-semibold text-wl-ink">
      Sources &amp; assumptions
    </h2>
    <p class="mt-1 text-sm text-wl-ink-muted">
      Every figure traces to the modelling assumptions below. Citations link to
      the original source — a peer-reviewed paper or official statistics.
    </p>
    <ul class="mt-3 space-y-3">
      <li v-for="a in sorted" :key="a.assumption_id" class="text-sm">
        <p class="text-wl-ink">{{ a.source }}</p>
        <p
          v-if="a.source_urls.length"
          class="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1"
        >
          <ExternalLink
            v-for="url in a.source_urls"
            :key="url"
            :href="url"
            class="text-xs"
          >
            {{ hostLabel(url) }}
          </ExternalLink>
        </p>
        <p v-else class="mt-1 text-xs text-wl-ink-faint">
          No public link available for this source.
        </p>
      </li>
    </ul>
  </section>
</template>
