<script setup lang="ts">
/**
 * ShareBar — Row of share/download/social buttons below the chart.
 *
 * Buttons are currently non-functional placeholders. Future work:
 * - Copy link: use Clipboard API
 * - Embed: open modal with iframe snippet
 * - Download PNG/SVG/CSV: trigger chart export
 * - Social sharing: open share URLs
 *
 * @example
 * <ShareBar chart-id="WL-W-001" />
 */

defineProps<{
  chartId?: string
}>()
</script>

<template>
  <div class="share-bar" role="toolbar" aria-label="Share and download">
    <!-- Share section -->
    <span class="share-bar__label">Share</span>
    <button class="share-bar__btn" type="button" aria-label="Copy link to chart">
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
      Copy link
    </button>
    <button class="share-bar__btn" type="button" aria-label="Get embed code">
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
      Embed
    </button>

    <!-- Download section -->
    <span class="share-bar__label share-bar__label--sep">Download</span>
    <button class="share-bar__btn" type="button" aria-label="Download PNG">
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
    <button class="share-bar__btn" type="button" aria-label="Download SVG">
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
    <button class="share-bar__btn" type="button" aria-label="Download CSV data">
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
    </button>

    <!-- Spacer -->
    <div class="share-bar__grow"></div>

    <!-- Social -->
    <button class="share-bar__btn" type="button" aria-label="Share on Bluesky">
      &rarr; Bluesky
    </button>
    <button class="share-bar__btn" type="button" aria-label="Share on LinkedIn">
      &rarr; LinkedIn
    </button>
    <button class="share-bar__btn" type="button" aria-label="Share on X">&rarr; X</button>

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
