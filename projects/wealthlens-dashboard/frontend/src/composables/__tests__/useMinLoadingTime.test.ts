import { describe, it, expect, vi } from "vitest";
import { ref, nextTick } from "vue";
import { useMinLoadingTime } from "../useMinLoadingTime";

describe("useMinLoadingTime", () => {
  it("reflects loading=true immediately", () => {
    const loading = ref(true);
    const { showing } = useMinLoadingTime(loading, 300);
    expect(showing.value).toBe(true);
  });

  it("keeps showing=true for minimum duration even if loading goes false quickly", async () => {
    vi.useFakeTimers();
    const loading = ref(false);
    const { showing } = useMinLoadingTime(loading, 300);

    loading.value = true;
    await nextTick();
    expect(showing.value).toBe(true);

    loading.value = false;
    await nextTick();
    expect(showing.value).toBe(true);

    vi.advanceTimersByTime(300);
    await nextTick();
    expect(showing.value).toBe(false);

    vi.useRealTimers();
  });

  it("hides immediately after minMs if loading already false", async () => {
    vi.useFakeTimers();
    const loading = ref(false);
    const { showing } = useMinLoadingTime(loading, 200);

    loading.value = true;
    await nextTick();

    loading.value = false;
    await nextTick();

    vi.advanceTimersByTime(200);
    await nextTick();
    expect(showing.value).toBe(false);

    vi.useRealTimers();
  });

  it("stays showing while loading remains true past minMs", async () => {
    vi.useFakeTimers();
    const loading = ref(false);
    const { showing } = useMinLoadingTime(loading, 100);

    loading.value = true;
    await nextTick();

    vi.advanceTimersByTime(200);
    await nextTick();
    expect(showing.value).toBe(true);

    loading.value = false;
    await nextTick();
    expect(showing.value).toBe(false);

    vi.useRealTimers();
  });
});
