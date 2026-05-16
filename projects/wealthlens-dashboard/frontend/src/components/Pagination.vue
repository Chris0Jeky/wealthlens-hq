<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  page: number
  totalPages: number
}>()

const emit = defineEmits<{
  (e: 'update:page', page: number): void
}>()

const pages = computed(() => {
  const total = props.totalPages
  const current = props.page
  const delta = 1
  const range: (number | '...')[] = []

  for (let i = 1; i <= total; i++) {
    if (i === 1 || i === total || (i >= current - delta && i <= current + delta)) {
      range.push(i)
    } else if (range[range.length - 1] !== '...') {
      range.push('...')
    }
  }
  return range
})

function goTo(p: number) {
  if (p >= 1 && p <= props.totalPages && p !== props.page) {
    emit('update:page', p)
  }
}
</script>

<template>
  <nav v-if="totalPages > 1" aria-label="Pagination" class="flex items-center justify-center gap-1">
    <button
      type="button"
      :disabled="page <= 1"
      aria-label="Previous page"
      class="px-3 py-1.5 rounded text-sm font-medium disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-100 dark:hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
      @click="goTo(page - 1)"
    >
      &lsaquo;
    </button>

    <template v-for="(item, idx) in pages" :key="idx">
      <span v-if="item === '...'" class="px-2 py-1.5 text-sm text-gray-400" aria-hidden="true">
        &hellip;
      </span>
      <button
        v-else
        type="button"
        :aria-label="`Page ${item}`"
        :aria-current="item === page ? 'page' : undefined"
        :class="[
          'px-3 py-1.5 rounded text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500',
          item === page
            ? 'bg-blue-600 text-white'
            : 'hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300',
        ]"
        @click="goTo(item)"
      >
        {{ item }}
      </button>
    </template>

    <button
      type="button"
      :disabled="page >= totalPages"
      aria-label="Next page"
      class="px-3 py-1.5 rounded text-sm font-medium disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-100 dark:hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
      @click="goTo(page + 1)"
    >
      &rsaquo;
    </button>
  </nav>
</template>
