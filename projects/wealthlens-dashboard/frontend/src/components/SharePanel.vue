<script setup lang="ts">
/**
 * SharePanel — Social sharing + embed panel for chart pages.
 *
 * Provides:
 * - Share buttons: Twitter/X, LinkedIn, Bluesky, copy link
 * - Embed code section with copyable iframe snippet
 *
 * Each social button opens the respective share URL in a new window.
 * "Copy link" uses navigator.clipboard with success feedback.
 * Accessible: keyboard navigable, ARIA labels, live regions.
 *
 * @example
 * <SharePanel
 *   chart-name="wealth-shares"
 *   chart-title="Who owns wealth in the UK?"
 * />
 */
import { ref, computed, onBeforeUnmount } from "vue";
import EmbedCode from "@/components/EmbedCode.vue";
import { CHARTS_BASE_URL } from "@/constants/urls";

const props = defineProps<{
  chartName: string;
  chartTitle: string;
}>();

const chartUrl = computed(() => `${CHARTS_BASE_URL}/${props.chartName}`);
const encodedUrl = computed(() => encodeURIComponent(chartUrl.value));
const encodedTitle = computed(
  () => encodeURIComponent(`${props.chartTitle} — WealthLens UK`),
);

const shareLinks = computed(() => ({
  twitter: `https://twitter.com/intent/tweet?url=${encodedUrl.value}&text=${encodedTitle.value}`,
  linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl.value}`,
  bluesky: `https://bsky.app/intent/compose?text=${encodedTitle.value}+${encodedUrl.value}`,
}));

function openShare(platform: "twitter" | "linkedin" | "bluesky"): void {
  const win = window.open(shareLinks.value[platform], "_blank", "noopener,noreferrer");
  if (!win) {
    window.location.href = shareLinks.value[platform];
  }
}

const linkCopied = ref(false);
const copyError = ref(false);
let timeoutId: ReturnType<typeof setTimeout> | null = null;

function clearTimer(): void {
  if (timeoutId) {
    clearTimeout(timeoutId);
    timeoutId = null;
  }
}

const isClipboardSupported = computed(
  () => typeof navigator !== "undefined" && !!navigator.clipboard,
);

async function copyLink(): Promise<void> {
  if (!isClipboardSupported.value) {
    copyError.value = true;
    clearTimer();
    timeoutId = setTimeout(() => { copyError.value = false; timeoutId = null; }, 3000);
    return;
  }

  try {
    await navigator.clipboard.writeText(chartUrl.value);
    linkCopied.value = true;
    copyError.value = false;
    clearTimer();
    timeoutId = setTimeout(() => {
      linkCopied.value = false;
      timeoutId = null;
    }, 2000);
  } catch {
    copyError.value = true;
    clearTimer();
    timeoutId = setTimeout(() => { copyError.value = false; timeoutId = null; }, 3000);
  }
}

onBeforeUnmount(clearTimer);
</script>

<template>
  <section
    class="share-panel"
    aria-labelledby="share-panel-heading"
  >
    <h2 id="share-panel-heading" class="share-panel__heading">
      Share this chart
    </h2>

    <!-- Social share buttons -->
    <nav class="share-panel__buttons" aria-label="Share options">
      <!-- Twitter/X -->
      <button
        type="button"
        class="share-panel__btn"
        aria-label="Share on X (Twitter)"
        @click="openShare('twitter')"
      >
        <svg
          viewBox="0 0 16 16"
          fill="currentColor"
          aria-hidden="true"
          class="share-panel__icon"
        >
          <path d="M9.3 6.8L14.2 1h-1.2L8.8 6l-3.3-5H2l5.1 7.4L2 15h1.2l4.5-5.2 3.5 5.2H14L9.3 6.8zm-1.6 1.8l-.5-.7L3.6 2h1.7l3.2 4.6.5.7 4.2 6H11.5l-3.8-5.7z" />
        </svg>
        X / Twitter
      </button>

      <!-- LinkedIn -->
      <button
        type="button"
        class="share-panel__btn"
        aria-label="Share on LinkedIn"
        @click="openShare('linkedin')"
      >
        <svg
          viewBox="0 0 16 16"
          fill="currentColor"
          aria-hidden="true"
          class="share-panel__icon"
        >
          <path d="M4.3 2.5a1.4 1.4 0 1 1-2.8 0 1.4 1.4 0 0 1 2.8 0zM1.7 5h2.4v9H1.7V5zm4.3 0h2.3v1.2h0c.3-.6 1.1-1.4 2.3-1.4 2.5 0 3 1.6 3 3.7V14h-2.4V9c0-1.2 0-2.7-1.6-2.7-1.7 0-1.9 1.3-1.9 2.6v5.1H6V5z" />
        </svg>
        LinkedIn
      </button>

      <!-- Bluesky -->
      <button
        type="button"
        class="share-panel__btn"
        aria-label="Share on Bluesky"
        @click="openShare('bluesky')"
      >
        <svg
          viewBox="0 0 16 16"
          fill="currentColor"
          aria-hidden="true"
          class="share-panel__icon"
        >
          <path d="M8 2.5c1.5 1.3 3.1 3.9 3.6 5.3.7 2 .3 3.5-.8 3.9-1 .3-2-.3-2.5-1.1-.1-.1-.2-.3-.3-.5-.1.2-.2.4-.3.5-.5.8-1.5 1.4-2.5 1.1-1.1-.4-1.5-1.9-.8-3.9.5-1.4 2.1-4 3.6-5.3z" />
        </svg>
        Bluesky
      </button>

      <!-- Copy link -->
      <button
        type="button"
        class="share-panel__btn"
        :class="{ 'share-panel__btn--success': linkCopied, 'share-panel__btn--error': copyError }"
        :aria-label="copyError ? 'Copy failed — try again' : linkCopied ? 'Link copied to clipboard' : 'Copy chart link'"
        @click="copyLink"
      >
        <svg
          v-if="!linkCopied && !copyError"
          viewBox="0 0 16 16"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
          aria-hidden="true"
          class="share-panel__icon"
        >
          <rect x="5" y="5" width="8" height="9" rx="1" />
          <path d="M3 11V3a1 1 0 0 1 1-1h6" />
        </svg>
        <svg
          v-else-if="linkCopied"
          viewBox="0 0 16 16"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          aria-hidden="true"
          class="share-panel__icon"
        >
          <path d="M3 8.5l3 3 7-7" />
        </svg>
        {{ copyError ? "Copy failed" : linkCopied ? "Copied!" : "Copy link" }}
      </button>
    </nav>

    <!-- Live region for copy confirmation -->
    <span role="status" aria-live="polite" class="sr-only">
      {{ copyError ? "Copy failed — try selecting the URL manually" : linkCopied ? "Chart link copied to clipboard" : "" }}
    </span>

    <!-- Embed code section -->
    <EmbedCode :chart-name="props.chartName" />
  </section>
</template>

<style scoped>
.share-panel {
  max-width: 1320px;
  margin: 16px auto 0;
  padding: 20px 24px;
  background: var(--wl-card);
  border: 1px solid var(--wl-ink);
}

.share-panel__heading {
  font-family: var(--wl-mono);
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.14em;
  color: var(--wl-ink-muted);
  text-transform: uppercase;
  margin: 0 0 14px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--wl-rule);
}

.share-panel__buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.share-panel__btn {
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
  letter-spacing: 0.04em;
  text-decoration: none;
}

.share-panel__btn:hover {
  background: var(--wl-ink);
  color: var(--wl-paper);
  border-color: var(--wl-ink);
}

.share-panel__btn:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: 2px;
}

.share-panel__btn--success {
  border-color: var(--wl-red);
  color: var(--wl-red);
}

.share-panel__btn--error {
  border-color: var(--wl-red);
  color: var(--wl-red);
}

.share-panel__icon {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

@media (max-width: 640px) {
  .share-panel {
    padding: 16px;
  }

  .share-panel__buttons {
    gap: 6px;
  }

  .share-panel__btn {
    padding: 6px 10px;
    font-size: 10px;
  }
}
</style>
