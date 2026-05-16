<script setup lang="ts">
</script>

<template>
  <div class="max-w-6xl mx-auto px-6 py-20 text-center">
    <h1 class="text-6xl font-bold text-gray-300 mb-4">404</h1>
    <h2 class="text-2xl font-semibold mb-3">Page not found</h2>
    <p class="text-gray-600 mb-6">
      The page you're looking for doesn't exist or has been moved.
    </p>
    <router-link
      to="/"
      class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
    >
      &larr; Back to dashboard
    </router-link>
  </div>
</template>
