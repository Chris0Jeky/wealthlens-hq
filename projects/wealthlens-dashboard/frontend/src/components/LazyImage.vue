<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";

const props = defineProps<{
  src: string;
  alt: string;
  width?: number;
  height?: number;
}>();

const imgRef = ref<HTMLImageElement | null>(null);
const loaded = ref(false);
const inView = ref(false);

let observer: IntersectionObserver | null = null;

onMounted(() => {
  if (!imgRef.value) return;
  observer = new IntersectionObserver(
    ([entry]) => {
      if (entry.isIntersecting) {
        inView.value = true;
        observer?.disconnect();
      }
    },
    { rootMargin: "200px" }
  );
  observer.observe(imgRef.value);
});

onUnmounted(() => {
  observer?.disconnect();
});
</script>

<template>
  <img
    ref="imgRef"
    :src="inView ? props.src : undefined"
    :alt="props.alt"
    :width="props.width"
    :height="props.height"
    :class="['lazy-img', { 'lazy-img--loaded': loaded }]"
    loading="lazy"
    @load="loaded = true"
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
</style>
