<script setup lang="ts">
/**
 * EmbedCode — Displays a copyable iframe embed snippet for a chart.
 *
 * Shows a pre-formatted iframe code block with a width selector (600px,
 * 800px, 100%) and a copy button with confirmation feedback.
 *
 * @example
 * <EmbedCode chart-name="wealth-shares" />
 */
import { ref, computed, onBeforeUnmount } from "vue"
import { SITE_BASE_URL } from "@/constants/urls"
import { buildEmbedSnippet } from "@/utils/embedSnippet"

const props = defineProps<{
  chartName: string
  /** Chart display title for the iframe's accessible name. */
  chartTitle?: string
}>()

const widthOptions = [
  { label: "600px", value: "600" },
  { label: "800px", value: "800" },
  { label: "100%", value: "100%" },
] as const

type EmbedWidth = (typeof widthOptions)[number]["value"]
const selectedWidth = ref<EmbedWidth>("100%")

// The snippet targets the chrome-free /embed shell (RFC-001f) — embedding
// the article page iframed the entire site chrome — and includes the
// auto-resize listener for the shell's height messages.
const embedSnippet = computed(() =>
  buildEmbedSnippet(
    SITE_BASE_URL,
    props.chartName,
    props.chartTitle ?? "Chart",
    selectedWidth.value === "100%" ? "100%" : selectedWidth.value,
  ),
)

const copied = ref(false)
const copyError = ref(false)
let timeoutId: ReturnType<typeof setTimeout> | null = null

function clearTimer(): void {
  if (timeoutId) {
    clearTimeout(timeoutId)
    timeoutId = null
  }
}

const isClipboardSupported = computed(
  () => typeof navigator !== "undefined" && !!navigator.clipboard,
)

async function copyEmbed(): Promise<void> {
  if (!isClipboardSupported.value) {
    copyError.value = true
    clearTimer()
    timeoutId = setTimeout(() => {
      copyError.value = false
      timeoutId = null
    }, 3000)
    return
  }

  try {
    await navigator.clipboard.writeText(embedSnippet.value)
    copied.value = true
    copyError.value = false
    clearTimer()
    timeoutId = setTimeout(() => {
      copied.value = false
      timeoutId = null
    }, 2000)
  } catch {
    copyError.value = true
    clearTimer()
    timeoutId = setTimeout(() => {
      copyError.value = false
      timeoutId = null
    }, 3000)
  }
}

onBeforeUnmount(clearTimer)
</script>

<template>
  <div class="embed-code" aria-labelledby="embed-code-heading">
    <h3 id="embed-code-heading" class="embed-code__heading">Embed this chart</h3>

    <!-- Width selector -->
    <fieldset class="embed-code__widths">
      <legend class="embed-code__legend">Width</legend>
      <label v-for="opt in widthOptions" :key="opt.value" class="embed-code__radio-label">
        <input
          v-model="selectedWidth"
          type="radio"
          name="embed-width"
          :value="opt.value"
          class="embed-code__radio"
        />
        {{ opt.label }}
      </label>
    </fieldset>

    <!-- Code block -->
    <div class="embed-code__block">
      <pre class="embed-code__pre"><code>{{ embedSnippet }}</code></pre>
    </div>

    <!-- Copy button -->
    <button
      type="button"
      class="embed-code__copy"
      :class="{ 'embed-code__copy--error': copyError }"
      :aria-label="
        copyError ? 'Copy failed — try again' : copied ? 'Embed code copied' : 'Copy embed code'
      "
      @click="copyEmbed"
    >
      <svg
        v-if="!copied && !copyError"
        viewBox="0 0 16 16"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
        aria-hidden="true"
        class="embed-code__icon"
      >
        <rect x="5" y="5" width="8" height="9" rx="1" />
        <path d="M3 11V3a1 1 0 0 1 1-1h6" />
      </svg>
      <svg
        v-else-if="copied"
        viewBox="0 0 16 16"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        aria-hidden="true"
        class="embed-code__icon"
      >
        <path d="M3 8.5l3 3 7-7" />
      </svg>
      {{ copyError ? "Copy failed" : copied ? "Copied!" : "Copy code" }}
    </button>

    <!-- Live region for screen readers -->
    <span role="status" aria-live="polite" class="sr-only">
      {{
        copyError
          ? "Copy failed — try selecting the code manually"
          : copied
            ? "Embed code copied to clipboard"
            : ""
      }}
    </span>
  </div>
</template>

<style scoped>
.embed-code {
  padding: 16px 0 0;
  border-top: 1px solid var(--wl-rule);
}

.embed-code__heading {
  font-family: var(--wl-mono);
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.14em;
  color: var(--wl-ink-muted);
  text-transform: uppercase;
  margin: 0 0 12px;
}

.embed-code__widths {
  border: none;
  padding: 0;
  margin: 0 0 12px;
  display: flex;
  gap: 16px;
  align-items: center;
}

.embed-code__legend {
  font-family: var(--wl-mono);
  font-size: 11px;
  color: var(--wl-ink-muted);
  margin-right: 8px;
}

.embed-code__radio-label {
  font-family: var(--wl-mono);
  font-size: 11px;
  color: var(--wl-ink-body);
  display: inline-flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
}

.embed-code__radio {
  accent-color: var(--wl-red);
}

.embed-code__block {
  background: var(--wl-bg-muted, #f5f5f5);
  border: 1px solid var(--wl-rule);
  padding: 12px 16px;
  overflow-x: auto;
  margin-bottom: 12px;
}

.embed-code__pre {
  margin: 0;
  font-family: var(--wl-mono);
  font-size: 11px;
  line-height: 1.5;
  color: var(--wl-ink-body);
  white-space: pre-wrap;
  word-break: break-all;
}

.embed-code__copy {
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
}

.embed-code__copy:hover {
  background: var(--wl-ink);
  color: var(--wl-paper);
  border-color: var(--wl-ink);
}

.embed-code__copy--error {
  border-color: var(--wl-red);
  color: var(--wl-red);
}

.embed-code__copy:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: 2px;
}

.embed-code__icon {
  width: 14px;
  height: 14px;
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
</style>
