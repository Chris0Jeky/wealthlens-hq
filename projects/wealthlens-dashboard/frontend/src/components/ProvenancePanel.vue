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
import { computed, useId } from 'vue'
import ExternalLink from '@/components/ExternalLink.vue'
import type { ConsumedAssumption } from '@/types/simulator'

// Optional: callers pass the (possibly absent) provenance.assumptions_consumed,
// and the computed below guards undefined so a partial payload never throws.
const props = defineProps<{
  assumptions?: ConsumedAssumption[]
}>()

// Stable, deterministic order by id. Robust to an absent/empty list so a partial
// payload never throws (the contract crosses an unvalidated JSON boundary).
const sorted = computed(() =>
  [...(props.assumptions ?? [])].sort((a, b) =>
    a.assumption_id.localeCompare(b.assumption_id),
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
 * without a leading `www.`; when two URLs in the SAME source share a host (e.g.
 * two ONS dataset files) the last path segment is appended so each link has a
 * distinct, meaningful accessible name (WCAG 2.4.4). Robust to a malformed URL.
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
</script>

<template>
  <section
    v-if="sorted.length"
    :aria-labelledby="headingId"
    class="mt-8 border-t border-wl-rule pt-6"
  >
    <h2 :id="headingId" class="text-base font-semibold text-wl-ink">
      Sources &amp; assumptions
    </h2>
    <p class="mt-1 text-sm text-wl-ink-muted">
      The modelling assumptions behind these figures, each linked to its original
      source — a peer-reviewed paper or official statistics.
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
        <p v-else class="mt-1 text-xs text-wl-ink-faint">
          No public link available for this source.
        </p>
      </li>
    </ul>
  </section>
</template>
