<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  page: number
  totalPages: number
}>()

const emit = defineEmits<{
  (e: 'update:page', page: number): void
}>()

const safePage = computed(() => Math.max(1, Math.min(props.page, props.totalPages)))

const pages = computed(() => {
  const total = props.totalPages
  const current = safePage.value
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
  <nav v-if="totalPages > 1" aria-label="Pagination" class="flex items-center justify-center">
    <ul class="flex items-center gap-1 list-none m-0 p-0" role="list">
      <li>
        <button
          type="button"
          :aria-disabled="safePage <= 1 ? 'true' : undefined"
          :class="['px-3 py-1.5 rounded text-sm font-medium hover:bg-gray-100 dark:hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500', safePage <= 1 && 'opacity-40 cursor-not-allowed']"
          aria-label="Previous page"
          @click="goTo(safePage - 1)"
        >
          &lsaquo;
        </button>
      </li>

      <li v-for="(item, idx) in pages" :key="`${idx}-${item}`">
        <span v-if="item === '...'" class="px-2 py-1.5 text-sm text-gray-400" aria-hidden="true">
          &hellip;
        </span>
        <button
          v-else
          type="button"
          :aria-label="`Page ${item}`"
          :aria-current="item === safePage ? 'page' : undefined"
          :class="[
            'px-3 py-1.5 rounded text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500',
            item === safePage
              ? 'bg-blue-600 text-white'
              : 'hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300',
          ]"
          @click="goTo(item)"
        >
          {{ item }}
        </button>
      </li>

      <li>
        <button
          type="button"
          :aria-disabled="safePage >= totalPages ? 'true' : undefined"
          :class="['px-3 py-1.5 rounded text-sm font-medium hover:bg-gray-100 dark:hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500', safePage >= totalPages && 'opacity-40 cursor-not-allowed']"
          aria-label="Next page"
          @click="goTo(safePage + 1)"
        >
          &rsaquo;
        </button>
      </li>
    </ul>
  </nav>
</template>
