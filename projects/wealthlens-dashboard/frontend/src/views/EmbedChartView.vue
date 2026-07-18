<script setup lang="ts">
/**
 * EmbedChartView — chrome-free chart shell for third-party embedding
 * (RFC-001f; route /embed/:name, iframe-targeted by the copy-paste snippet
 * in EmbedCode/ShareBar).
 *
 * Renders ONLY: the chart, its title, a source + licence line, an honesty
 * caveat when the dataset is an illustrative composite, and a backlink to
 * the full article. App.vue suppresses the site header/footer for routes
 * with `meta.embed`. No cookies, no storage, no analytics (the snippet's
 * sandbox omits allow-same-origin, and this shell must keep working there).
 *
 * Height auto-resize: posts {source: "wealthlens-embed", chart, height} to
 * the parent window whenever the document height changes, so the snippet's
 * companion script can size the iframe. Posting to "*" is safe — the
 * message carries nothing but the public chart slug and a pixel height.
 */
import { computed, defineAsyncComponent, onMounted, onBeforeUnmount, ref } from "vue"
import { useRoute } from "vue-router"
import ChartSkeleton from "@/components/ChartSkeleton.vue"
import ChartLoadError from "@/components/ChartLoadError.vue"
import { CHART_COMPONENT_LOADERS } from "@/config/chartComponents"
import { chartConfigs, chartDisplayTitle } from "@/config/chartArticles"
import { DATASET_PROVENANCE } from "@/constants/datasetProvenance"
import { usePageMeta } from "@/composables/usePageMeta"
import { SITE_URL } from "@/constants/site"
import { EMBED_MESSAGE_SOURCE } from "@/utils/embedSnippet"
import { useDataStore } from "@/stores/data"

const route = useRoute()
const chartName = computed(() => route.params.name as string)

const title = computed(() => chartDisplayTitle(chartName.value))
const articleUrl = computed(() => `${SITE_URL}/charts/${chartName.value}`)

/** Route validation happens in the router's beforeEnter, so the map hit is safe. */
const ChartComponent = defineAsyncComponent({
  loader: CHART_COMPONENT_LOADERS[chartName.value] ?? (() => Promise.reject(new Error("unknown"))),
  loadingComponent: ChartSkeleton,
  errorComponent: ChartLoadError,
  delay: 200,
  timeout: 10000,
})

/* ---- source + licence line (single sources of truth) ---- */
const provenance = computed(() => DATASET_PROVENANCE[chartName.value])

// Full-config charts carry their source inline; the rest use the published
// static metadata (fetched through the static-aware store).
const store = useDataStore()
const fetchedSource = ref<{ name: string; url: string; accessed: string } | null>(null)

const source = computed(() => {
  const config = chartConfigs[chartName.value]
  if (config) {
    return { name: config.source.name, url: config.source.url, accessed: config.source.accessed }
  }
  return fetchedSource.value
})

/** Illustrative-composite honesty caveat — must travel with the artifact. */
const isIllustrative = ref(false)

/* ---- height auto-resize ---- */
let resizeObserver: ResizeObserver | null = null

function postHeight(): void {
  if (window.parent === window) return
  window.parent.postMessage(
    {
      source: EMBED_MESSAGE_SOURCE,
      chart: chartName.value,
      height: document.documentElement.scrollHeight,
    },
    "*",
  )
}

onMounted(async () => {
  if (typeof ResizeObserver !== "undefined") {
    resizeObserver = new ResizeObserver(postHeight)
    resizeObserver.observe(document.documentElement)
  }
  postHeight()

  try {
    const meta = await store.fetchMetadata(chartName.value)
    if (!chartConfigs[chartName.value]) {
      fetchedSource.value = { name: meta.source, url: meta.source_url, accessed: meta.access_date }
    }
    isIllustrative.value = meta.data_type === "illustrative_fallback"
  } catch {
    // Source line falls back to the backlink only — never fabricate a citation.
  }
})

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  resizeObserver = null
})

usePageMeta({
  title: computed(() => `${title.value} (embed)`),
  description: computed(() => `Embeddable chart: ${title.value}`),
  // Canonical points at the full article — the embed is a satellite of it.
  url: articleUrl,
  image: computed(() => `${SITE_URL}/og/${chartName.value}.png`),
  robots: "noindex",
})
</script>

<template>
  <div class="embed-shell">
    <p class="embed-title">{{ title }}</p>

    <ChartComponent />

    <p v-if="isIllustrative" class="embed-caveat" role="note">
      Illustrative composite — figures are worked examples, not published statistics. See the full
      article for caveats.
    </p>

    <footer class="embed-foot">
      <span class="embed-source">
        <template v-if="source">
          Source:
          <a :href="source.url" target="_blank" rel="noopener">{{ source.name }}</a>
          <template v-if="source.accessed"> · accessed {{ source.accessed }}</template>
          <template v-if="provenance"> · {{ provenance.licence }}</template>
        </template>
      </span>
      <a class="embed-backlink" :href="articleUrl" target="_blank" rel="noopener">
        Explore on WealthLens UK →
      </a>
    </footer>
  </div>
</template>

<style scoped>
.embed-shell {
  padding: 12px 16px 10px;
}

.embed-title {
  font-family: var(--wl-serif);
  font-size: 17px;
  font-weight: 700;
  color: var(--wl-ink);
  margin: 0 0 8px;
  line-height: 1.3;
}

.embed-caveat {
  font-family: var(--wl-mono);
  font-size: 11px;
  color: var(--wl-red-deep);
  margin: 8px 0 0;
}

.embed-foot {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 16px;
  flex-wrap: wrap;
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px solid var(--wl-rule);
}

.embed-source {
  font-family: var(--wl-mono);
  font-size: 11px;
  color: var(--wl-ink-muted);
}

.embed-source a {
  color: inherit;
  text-decoration: underline;
}

.embed-backlink {
  font-size: 12px;
  font-weight: 600;
  color: var(--wl-red);
  text-decoration: none;
  white-space: nowrap;
}

.embed-backlink:hover {
  color: var(--wl-red-deep);
}
</style>
