<script setup lang="ts">
/**
 * HealthStatus — compact footer widget showing backend connectivity.
 *
 * Polls /api/version on mount, on visibility change, and every 60 seconds.
 * Shows a green dot when connected (with version + dataset count), or a
 * red dot when the backend is unreachable.
 */
import { ref, onMounted, onUnmounted, computed } from "vue"

interface VersionInfo {
  version: string
  datasets_available: number
}

type ConnectionState = "connected" | "disconnected" | "checking"

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"
const POLL_INTERVAL_MS = 60_000

const state = ref<ConnectionState>("checking")
const versionInfo = ref<VersionInfo | null>(null)

let pollTimer: ReturnType<typeof setInterval> | null = null
let abortController: AbortController | null = null

const statusLabel = computed(() => {
  if (state.value === "checking") return "Checking API..."
  if (state.value === "disconnected") return "API offline"
  if (versionInfo.value) {
    return `v${versionInfo.value.version} · ${versionInfo.value.datasets_available} datasets`
  }
  return "Connected"
})

const dotClass = computed(() => {
  switch (state.value) {
    case "connected":
      return "bg-green-500"
    case "disconnected":
      return "bg-red-500"
    default:
      return "bg-gray-400"
  }
})

async function checkHealth(): Promise<void> {
  // Abort any in-flight request before starting a new one
  abortController?.abort()
  abortController = new AbortController()
  try {
    const res = await fetch(`${BASE_URL}/api/version`, {
      signal: abortController.signal,
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const json: VersionInfo = await res.json()
    versionInfo.value = json
    state.value = "connected"
  } catch (err) {
    // Ignore aborted requests — component may have unmounted
    if (err instanceof DOMException && err.name === "AbortError") return
    state.value = "disconnected"
    versionInfo.value = null
  }
}

function handleVisibilityChange(): void {
  if (document.visibilityState === "visible") {
    checkHealth()
  }
}

onMounted(() => {
  checkHealth()
  pollTimer = setInterval(checkHealth, POLL_INTERVAL_MS)
  document.addEventListener("visibilitychange", handleVisibilityChange)
})

onUnmounted(() => {
  abortController?.abort()
  abortController = null
  if (pollTimer !== null) {
    clearInterval(pollTimer)
    pollTimer = null
  }
  document.removeEventListener("visibilitychange", handleVisibilityChange)
})
</script>

<template>
  <span class="health-status" role="status" :aria-label="`Backend status: ${state}`">
    <span
      class="health-dot"
      :class="[dotClass, { 'motion-safe:animate-pulse': state === 'checking' }]"
      aria-hidden="true"
    />
    <span class="health-label">{{ statusLabel }}</span>
  </span>
</template>

<style scoped>
.health-status {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: var(--wl-mono, ui-monospace, monospace);
  font-size: 11px;
  color: var(--wl-ink-muted, #6b7280);
}

.health-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.health-label {
  white-space: nowrap;
}
</style>
