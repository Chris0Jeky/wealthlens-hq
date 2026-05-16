<script setup lang="ts">
export interface BreadcrumbItem {
  label: string
  to?: string
}

defineProps<{
  items: BreadcrumbItem[]
}>()
</script>

<template>
  <nav aria-label="Breadcrumb" class="text-sm text-gray-500 mb-4">
    <ol class="flex items-center gap-1">
      <li
        v-for="(item, index) in items"
        :key="index"
        class="flex items-center"
      >
        <span v-if="index > 0" class="mx-1" aria-hidden="true">/</span>
        <router-link
          v-if="item.to"
          :to="item.to"
          class="hover:text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1 rounded"
        >
          {{ item.label }}
        </router-link>
        <span v-else aria-current="page" class="text-gray-900 font-medium">
          {{ item.label }}
        </span>
      </li>
    </ol>
  </nav>
</template>
