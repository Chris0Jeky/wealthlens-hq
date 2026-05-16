<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'

type Status = 'healthy' | 'degraded' | 'unavailable' | 'loading' | 'error'

const status = ref<Status>('loading')
const availableCount = ref(0)
const totalCount = ref(0)

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
    :class="['inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium', colorClass]"
    role="status"
    :aria-label="`Data status: ${status}`"
  >
    {{ label }}
  </span>
</template>
