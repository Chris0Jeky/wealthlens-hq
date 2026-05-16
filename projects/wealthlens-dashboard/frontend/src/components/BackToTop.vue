<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const visible = ref(false)
const THRESHOLD = 300

function onScroll() {
  visible.value = window.scrollY > THRESHOLD
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => {
  window.addEventListener('scroll', onScroll, { passive: true })
})

onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
})
</script>

<template>
  <Transition
    enter-from-class="opacity-0 translate-y-2"
    enter-active-class="transition duration-200"
    leave-active-class="transition duration-200"
    leave-to-class="opacity-0 translate-y-2"
  >
    <button
      v-if="visible"
      type="button"
      class="fixed bottom-6 right-6 p-3 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 motion-safe:transition-transform motion-safe:hover:scale-110"
      aria-label="Scroll to top"
      @click="scrollToTop"
    >
      &#x2191;
    </button>
  </Transition>
</template>
