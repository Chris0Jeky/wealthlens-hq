<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'

type Status = 'healthy' | 'degraded' | 'unavailable' | 'loading' | 'error'

const status = ref<Status>('loading')
const availableCount = ref(0)
const totalCount = ref(0)

/** Human-readable status text for each state (WCAG 1.4.1 — not color-only) */
const statusText = computed(() => {
  switch (status.value) {
    case 'healthy': return 'Healthy'
    case 'degraded': return 'Degraded'
    case 'unavailable': return 'Unavailable'
    case 'error': return 'Error'
    default: return 'Loading'
  }
})

const label = computed(() => {
  if (status.value === 'loading') return 'Checking data...'
  if (status.value === 'error') return 'Status unknown'
  return `${availableCount.value}/${totalCount.value} datasets`
})

const colorClass = computed(() => {
  switch (status.value) {
    case 'healthy': return 'bg-green-100 text-green-800'
    case 'degraded': return 'bg-yellow-100 text-yellow-800'
    case 'unavailable': return 'bg-red-100 text-red-800'
    case 'error': return 'bg-gray-100 text-gray-600'
    default: return 'bg-gray-100 text-gray-500'
  }
})

/** Colored dot class for visual reinforcement (not the sole indicator) */
const dotClass = computed(() => {
  switch (status.value) {
    case 'healthy': return 'bg-green-500'
    case 'degraded': return 'bg-yellow-500'
    case 'unavailable': return 'bg-red-500'
    case 'error': return 'bg-gray-400'
    default: return 'bg-gray-400'
  }
})

onMounted(async () => {
  try {
    const res = await fetch('/api/health/data')
    if (!res.ok) throw new Error()
    const json = await res.json()
    status.value = json.status
    availableCount.value = json.available_count
    totalCount.value = json.total_count
  } catch {
    status.value = 'error'
  }
})
</script>

<template>
  <span
    :class="['inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium', colorClass]"
    role="status"
    :aria-label="`Data status: ${statusText} — ${label}`"
  >
    <!-- Status icon: provides non-color shape indicator (WCAG 1.4.1) -->
    <!-- Checkmark for healthy -->
    <svg
      v-if="status === 'healthy'"
      class="h-3 w-3 flex-shrink-0"
      aria-hidden="true"
      viewBox="0 0 16 16"
      fill="currentColor"
    >
      <path d="M13.78 4.22a.75.75 0 0 1 0 1.06l-7.25 7.25a.75.75 0 0 1-1.06 0L2.22 9.28a.75.75 0 0 1 1.06-1.06L6 10.94l6.72-6.72a.75.75 0 0 1 1.06 0Z" />
    </svg>
    <!-- Warning triangle for degraded -->
    <svg
      v-else-if="status === 'degraded'"
      class="h-3 w-3 flex-shrink-0"
      aria-hidden="true"
      viewBox="0 0 16 16"
      fill="currentColor"
    >
      <path d="M6.457 1.047c.659-1.234 2.427-1.234 3.086 0l6.082 11.378A1.75 1.75 0 0 1 14.082 15H1.918a1.75 1.75 0 0 1-1.543-2.575L6.457 1.047ZM8 5a.75.75 0 0 0-.75.75v2.5a.75.75 0 0 0 1.5 0v-2.5A.75.75 0 0 0 8 5Zm1 6a1 1 0 1 0-2 0 1 1 0 0 0 2 0Z" />
    </svg>
    <!-- X circle for unavailable -->
    <svg
      v-else-if="status === 'unavailable'"
      class="h-3 w-3 flex-shrink-0"
      aria-hidden="true"
      viewBox="0 0 16 16"
      fill="currentColor"
    >
      <path d="M2.343 13.657A8 8 0 1 1 13.658 2.343 8 8 0 0 1 2.343 13.657ZM6.03 4.97a.75.75 0 0 0-1.06 1.06L6.94 8 4.97 9.97a.75.75 0 1 0 1.06 1.06L8 9.06l1.97 1.97a.75.75 0 1 0 1.06-1.06L9.06 8l1.97-1.97a.75.75 0 0 0-1.06-1.06L8 6.94 6.03 4.97Z" />
    </svg>
    <!-- Exclamation circle for error -->
    <svg
      v-else-if="status === 'error'"
      class="h-3 w-3 flex-shrink-0"
      aria-hidden="true"
      viewBox="0 0 16 16"
      fill="currentColor"
    >
      <path d="M8 0a8 8 0 1 0 0 16A8 8 0 0 0 8 0Zm-.75 4.75a.75.75 0 0 1 1.5 0v3.5a.75.75 0 0 1-1.5 0v-3.5ZM8 12a1 1 0 1 1 0-2 1 1 0 0 1 0 2Z" />
    </svg>
    <!-- Dot for loading -->
    <span
      v-else
      :class="['inline-block h-2 w-2 rounded-full', dotClass]"
      aria-hidden="true"
    ></span>

    <!-- Status text label (primary non-color indicator) -->
    <span class="status-text">{{ statusText }}</span>

    <!-- Separator and data label -->
    <span aria-hidden="true" class="text-current opacity-50">|</span>
    <span>{{ label }}</span>
  </span>
</template>
