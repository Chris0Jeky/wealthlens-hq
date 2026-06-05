<script setup lang="ts">
/**
 * ProvenancePanel — renders the provenance behind a scenario's figures: the
 * modelling assumptions (with citation links) and the population data sources.
 *
 * This is the user-facing payoff of the registry citation URLs: every published
 * figure traces to a peer-reviewed paper or official statistic, and the reader can
 * follow the link. Citations open via {@link ExternalLink} (safe-href guard,
 * `rel="noopener noreferrer"`, an accessible "opens in new tab" hint).
 */
import { computed, useId } from 'vue'
import ExternalLink from '@/components/ExternalLink.vue'
import type {
  ConsumedAssumption,
  PopulationProvenanceEntry,
} from '@/types/simulator'

const props = defineProps<{
  // Optional: callers pass the (possibly absent) provenance.assumptions_consumed
  // and population_provenance; the computeds below guard undefined so a partial
  // payload never throws.
  assumptions?: ConsumedAssumption[]
  populationSources?: PopulationProvenanceEntry[]
}>()

// Stable, deterministic order by id. Robust to an absent/empty list.
const sorted = computed(() =>
  [...(props.assumptions ?? [])].sort((a, b) =>
    a.assumption_id.localeCompare(b.assumption_id),
  ),
)

// Only registered data sources are citable (they carry a URL); synthetic
// generation parameters are id-only config inputs and are not listed. A blank-ish
// URL (whitespace only) is dropped too — it would render as an inert "#" link.
const dataSources = computed(() =>
  (props.populationSources ?? []).filter(
    (s): s is PopulationProvenanceEntry & { url: string } => Boolean(s.url?.trim()),
  ),
)

// Unique id so multiple panels on one page never collide on the heading id.
const headingId = useId()

interface CitationLink {
  url: string
  label: string
}

/**
 * Concise, distinct labels for a source's citation links. Each label is the host
 * without a leading `www.`; when two URLs in the SAME source share a host the last
 * path segment is appended so each link has a distinct accessible name (WCAG
 * 2.4.4). Robust to a malformed URL.
 */
function citationLinks(urls: string[] | undefined): CitationLink[] {
  const parsed = (urls ?? []).map((url) => {
    try {
      const u = new URL(url)
      const host = u.hostname.replace(/^www\./, '')
      const segs = u.pathname.split('/').filter(Boolean)
      return { url, host, lastSeg: segs.length ? segs[segs.length - 1] : '' }
    } catch {
      return { url, host: url, lastSeg: '' }
    }
  })
  const hostCounts = parsed.reduce<Record<string, number>>((acc, p) => {
    acc[p.host] = (acc[p.host] ?? 0) + 1
    return acc
  }, {})
  return parsed.map((p) => ({
    url: p.url,
    label: hostCounts[p.host] > 1 && p.lastSeg ? `${p.host}/${p.lastSeg}` : p.host,
  }))
}

/** The single host label for one data-source URL. */
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
    v-if="sorted.length || dataSources.length"
    :aria-labelledby="headingId"
    class="mt-8 border-t border-wl-rule pt-6"
  >
    <h2 :id="headingId" class="text-base font-semibold text-wl-ink">
      Sources &amp; assumptions
    </h2>

    <template v-if="sorted.length">
      <h3 class="mt-4 text-sm font-semibold text-wl-ink">Modelling assumptions</h3>
      <p class="mt-1 text-sm text-wl-ink-muted">
        Each linked to its original source — a peer-reviewed paper or official
        statistics.
      </p>
      <ul class="mt-3 space-y-3">
        <li v-for="a in sorted" :key="a.assumption_id" class="text-sm">
          <p class="text-wl-ink">{{ a.source }}</p>
          <ul
            v-if="(a.source_urls ?? []).length"
            class="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1"
          >
            <li v-for="link in citationLinks(a.source_urls)" :key="link.url">
              <ExternalLink :href="link.url" class="text-xs">
                {{ link.label }}
              </ExternalLink>
            </li>
          </ul>
          <p v-else class="mt-1 text-xs text-wl-ink-muted">
            No public link available for this source.
          </p>
        </li>
      </ul>
    </template>

    <template v-if="dataSources.length">
      <h3 class="mt-5 text-sm font-semibold text-wl-ink">
        Population data sources
      </h3>
      <p class="mt-1 text-sm text-wl-ink-muted">
        The official datasets the synthetic population is calibrated to.
      </p>
      <ul class="mt-2 space-y-2">
        <li v-for="s in dataSources" :key="s.url" class="text-sm">
          <p class="text-wl-ink">{{ s.name || s.id }}</p>
          <p class="mt-0.5 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs">
            <ExternalLink :href="s.url">{{ hostLabel(s.url) }}</ExternalLink>
            <span v-if="s.access_date" class="text-wl-ink-muted">
              accessed {{ s.access_date }}
            </span>
            <span v-if="s.licence" class="text-wl-ink-muted">
              <span aria-hidden="true">·</span> {{ s.licence }}
            </span>
          </p>
        </li>
      </ul>
    </template>
  </section>
</template>
