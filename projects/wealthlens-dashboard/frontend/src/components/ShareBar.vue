<script setup lang="ts">
/**
 * ShareBar — Row of share/download/social buttons below the chart.
 *
 * Every control is real (reality-check F7 — these were 8 dead buttons):
 * - Copy link / Copy embed: Clipboard API with visible + live-region feedback
 * - PNG / SVG: emitted up to ChartView, which owns the chart ref and calls
 *   useChartExport (same path as ExportButton)
 * - CSV: direct link to the static data mirror (RFC-001a); hidden for the
 *   NC-ND-restricted dataset until ACTION-REQUIRED #10 is decided
 * - Bluesky / LinkedIn / X: share-intent URLs (same builder as SharePanel)
 *
 * @example
 * <ShareBar chart-name="wealth-shares" chart-title="Who owns wealth in the UK?"
 *           chart-id="WL-W-001" @export="onExport" />
 */
import { ref, computed, onBeforeUnmount } from "vue"
import { CHARTS_BASE_URL, SITE_BASE_URL } from "@/constants/urls"
import { csvDownloadUrl, hasCsvDownload } from "@/constants/downloads"
import { buildEmbedSnippet } from "@/utils/embedSnippet"
import { buildShareLinks, openShareIntent } from "@/utils/shareIntents"

const props = defineProps<{
  chartName: string
  chartTitle: string
  chartId?: string
}>()

const emit = defineEmits<{
  export: [format: "png" | "svg"]
}>()

const chartUrl = computed(() => `${CHARTS_BASE_URL}/${props.chartName}`)
const shareLinks = computed(() => buildShareLinks(chartUrl.value, props.chartTitle))
const csvAvailable = computed(() => hasCsvDownload(props.chartName))
const csvUrl = computed(() => csvDownloadUrl(props.chartName))

/* ---- clipboard feedback (link + embed share one live region) ---- */
type CopyState = "idle" | "copied" | "error"
const linkState = ref<CopyState>("idle")
const embedState = ref<CopyState>("idle")
let timeoutId: ReturnType<typeof setTimeout> | null = null

function flash(state: { value: CopyState }, value: CopyState): void {
  state.value = value
  if (timeoutId) clearTimeout(timeoutId)
  timeoutId = setTimeout(() => {
    linkState.value = "idle"
    embedState.value = "idle"
    timeoutId = null
  }, 2000)
}

async function copyText(text: string, state: { value: CopyState }): Promise<void> {
  if (typeof navigator === "undefined" || !navigator.clipboard) {
    flash(state, "error")
    return
  }
  try {
    await navigator.clipboard.writeText(text)
    flash(state, "copied")
  } catch {
    flash(state, "error")
  }
}

const copyLink = () => copyText(chartUrl.value, linkState)
const copyEmbed = () =>
  copyText(buildEmbedSnippet(SITE_BASE_URL, props.chartName, props.chartTitle), embedState)

const liveMessage = computed(() => {
  if (linkState.value === "copied") return "Chart link copied to clipboard"
  if (embedState.value === "copied") return "Embed code copied to clipboard"
  if (linkState.value === "error" || embedState.value === "error")
    return "Copy failed — try selecting the address bar instead"
  return ""
})

onBeforeUnmount(() => {
  if (timeoutId) clearTimeout(timeoutId)
})
</script>

<template>
  <div class="share-bar" role="toolbar" aria-label="Share and download">
    <!-- Share section -->
    <span class="share-bar__label">Share</span>
    <button
      class="share-bar__btn"
      type="button"
      :aria-label="linkState === 'copied' ? 'Link copied' : 'Copy link to chart'"
      @click="copyLink"
    >
      <!-- clipboard icon -->
      <svg
        viewBox="0 0 16 16"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
        aria-hidden="true"
      >
        <rect x="5" y="5" width="8" height="9" rx="1" />
        <path d="M3 11V3a1 1 0 0 1 1-1h6" />
      </svg>
      {{ linkState === "copied" ? "Copied!" : linkState === "error" ? "Copy failed" : "Copy link" }}
    </button>
    <button
      class="share-bar__btn"
      type="button"
      :aria-label="embedState === 'copied' ? 'Embed code copied' : 'Copy embed code'"
      @click="copyEmbed"
    >
      <!-- code icon -->
      <svg
        viewBox="0 0 16 16"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
        aria-hidden="true"
      >
        <path d="M5 4L1 8l4 4M11 4l4 4-4 4" />
      </svg>
      {{ embedState === "copied" ? "Copied!" : embedState === "error" ? "Copy failed" : "Embed" }}
    </button>

    <!-- Download section -->
    <span class="share-bar__label share-bar__label--sep">Download</span>
    <button
      class="share-bar__btn"
      type="button"
      aria-label="Download PNG"
      @click="emit('export', 'png')"
    >
      <svg
        viewBox="0 0 16 16"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
        aria-hidden="true"
      >
        <path d="M8 2v8m0 0L5 7m3 3l3-3M2 12v1a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1v-1" />
      </svg>
      PNG
    </button>
    <button
      class="share-bar__btn"
      type="button"
      aria-label="Download SVG"
      @click="emit('export', 'svg')"
    >
      <svg
        viewBox="0 0 16 16"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
        aria-hidden="true"
      >
        <path d="M8 2v8m0 0L5 7m3 3l3-3M2 12v1a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1v-1" />
      </svg>
      SVG
    </button>
    <a
      v-if="csvAvailable"
      class="share-bar__btn"
      :href="csvUrl"
      download
      :aria-label="`Download ${chartName} data as CSV`"
    >
      <svg
        viewBox="0 0 16 16"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
        aria-hidden="true"
      >
        <path d="M8 2v8m0 0L5 7m3 3l3-3M2 12v1a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1v-1" />
      </svg>
      CSV
    </a>

    <!-- Spacer -->
    <div class="share-bar__grow"></div>

    <!-- Social -->
    <button
      class="share-bar__btn"
      type="button"
      aria-label="Share on Bluesky"
      @click="openShareIntent(shareLinks.bluesky)"
    >
      &rarr; Bluesky
    </button>
    <button
      class="share-bar__btn"
      type="button"
      aria-label="Share on LinkedIn"
      @click="openShareIntent(shareLinks.linkedin)"
    >
      &rarr; LinkedIn
    </button>
    <button
      class="share-bar__btn"
      type="button"
      aria-label="Share on X"
      @click="openShareIntent(shareLinks.twitter)"
    >
      &rarr; X
    </button>

    <!-- Live region for copy feedback -->
    <span role="status" aria-live="polite" class="sr-only">{{ liveMessage }}</span>

    <!-- Append slot for additional toolbar controls -->
    <slot name="append" />
  </div>
</template>

<style scoped>
.share-bar {
  max-width: 1320px;
  margin: 24px auto 0;
  padding: 16px 24px;
  background: var(--wl-card);
  border: 1px solid var(--wl-ink);
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.share-bar__label {
  font-family: var(--wl-mono);
  font-size: 10px;
  color: var(--wl-ink-muted);
  text-transform: uppercase;
  letter-spacing: 0.14em;
  padding-right: 12px;
  border-right: 1px solid var(--wl-rule);
  margin-right: 4px;
  font-weight: 500;
}

.share-bar__label--sep {
  border-left: 1px solid var(--wl-rule);
  padding-left: 12px;
  margin-left: 4px;
}

.share-bar__btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 12px;
  background: var(--wl-card);
  border: 1px solid var(--wl-rule-strong);
  font-family: var(--wl-mono);
  font-size: 11px;
  color: var(--wl-ink-body);
  cursor: pointer;
  text-decoration: none;
  letter-spacing: 0.04em;
}
.share-bar__btn:hover {
  background: var(--wl-ink);
  color: var(--wl-paper);
  border-color: var(--wl-ink);
}
.share-bar__btn:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: 2px;
}
.share-bar__btn svg {
  width: 14px;
  height: 14px;
}

.share-bar__grow {
  flex: 1;
}

@media (max-width: 640px) {
  .share-bar {
    padding: 12px 16px;
  }
  .share-bar__grow {
    flex-basis: 100%;
  }
}
</style>
