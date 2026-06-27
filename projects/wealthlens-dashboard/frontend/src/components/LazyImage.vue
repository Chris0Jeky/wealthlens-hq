<script setup lang="ts">
import { ref } from "vue"
import { useIntersectionObserver } from "@/composables/useIntersectionObserver"

const props = defineProps<{
  src: string
  alt: string
  width?: number
  height?: number
}>()

const imgRef = ref<HTMLImageElement | null>(null)
const loaded = ref(false)
const failed = ref(false)

function finishLoading() {
  loaded.value = true
}

function handleError() {
  failed.value = true
  finishLoading()
}

const { isVisible: inView } = useIntersectionObserver(imgRef, {
  rootMargin: "200px",
  threshold: 0,
  once: true,
})
</script>

<template>
  <img
    ref="imgRef"
    :src="inView ? props.src : undefined"
    :alt="props.alt"
    :width="props.width"
    :height="props.height"
    :class="['lazy-img', { 'lazy-img--loaded': loaded, 'lazy-img--failed': failed }]"
    :aria-busy="!loaded"
    loading="lazy"
    @load="finishLoading"
    @error="handleError"
  />
</template>

<style scoped>
.lazy-img {
  opacity: 0;
  transition: opacity 0.3s ease;
}

.lazy-img--loaded {
  opacity: 1;
}

@media (prefers-reduced-motion: reduce) {
  .lazy-img {
    transition: none;
    opacity: 1;
  }
}
</style>
