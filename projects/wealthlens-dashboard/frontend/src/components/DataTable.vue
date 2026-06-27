<script setup lang="ts">
import { computed } from "vue"

export interface Column {
  key: string
  label: string
  align?: "left" | "right" | "center"
}

const props = defineProps<{
  columns: Column[]
  rows: Record<string, unknown>[]
  caption?: string
}>()

const alignClass = (col: Column) => {
  if (col.align === "right") return "text-right"
  if (col.align === "center") return "text-center"
  return "text-left"
}

const isEmpty = computed(() => props.rows.length === 0)
</script>

<template>
  <div class="w-full overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-700">
    <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
      <caption v-if="caption" class="sr-only">
        {{
          caption
        }}
      </caption>
      <thead class="bg-gray-50 dark:bg-gray-800">
        <tr>
          <th
            v-for="col in columns"
            :key="col.key"
            scope="col"
            :class="[
              'px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400',
              alignClass(col),
            ]"
          >
            {{ col.label }}
          </th>
        </tr>
      </thead>
      <tbody class="divide-y divide-gray-200 dark:divide-gray-700 bg-white dark:bg-gray-900">
        <tr v-if="isEmpty">
          <td :colspan="columns.length" class="px-4 py-8 text-center text-sm text-gray-500">
            No data available
          </td>
        </tr>
        <tr v-for="(row, idx) in rows" :key="idx" class="hover:bg-gray-50 dark:hover:bg-gray-800">
          <td
            v-for="col in columns"
            :key="col.key"
            :class="[
              'px-4 py-3 text-sm text-gray-900 dark:text-gray-100 whitespace-nowrap',
              alignClass(col),
            ]"
          >
            <slot :name="`cell-${col.key}`" :value="row[col.key]" :row="row">
              {{ row[col.key] ?? "—" }}
            </slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
