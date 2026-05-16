import { ref, watch, type Ref } from "vue";

/**
 * Ensures a loading state displays for a minimum duration to prevent
 * flash-of-skeleton when data loads very quickly.
 *
 * Returns a `showing` ref that stays true for at least `minMs` after
 * `loading` becomes true, even if `loading` goes false sooner.
 */
export function useMinLoadingTime(loading: Ref<boolean>, minMs = 300) {
  const showing = ref(loading.value);
  let timer: ReturnType<typeof setTimeout> | null = null;

  watch(loading, (isLoading) => {
    if (isLoading) {
      showing.value = true;
      if (timer) clearTimeout(timer);
      timer = setTimeout(() => {
        timer = null;
        if (!loading.value) {
          showing.value = false;
        }
      }, minMs);
    } else {
      if (timer === null) {
        showing.value = false;
      }
    }
  });

  return { showing };
}
