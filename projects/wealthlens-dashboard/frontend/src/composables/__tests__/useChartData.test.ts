import { describe, it, expect, vi, beforeEach } from "vitest";
import { mount, flushPromises } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { defineComponent } from "vue";

/**
 * useChartData must request the FULL dataset. The live API paginates with a
 * default limit of 100, but charts render every row, so the default would
 * silently truncate larger datasets (housing-affordability 348, wealth-shares
 * 250) — a data-integrity violation. This locks the explicit limit=1000.
 */

const fetchDataset = vi.fn().mockResolvedValue({
  data: [{ region: "London", value: 1 }],
  page: 1,
  limit: 1000,
  total: 1,
  total_pages: 1,
});

vi.mock("@/stores/data", () => ({
  useDataStore: () => ({ fetchDataset }),
}));

import { useChartData } from "@/composables/useChartData";

// Minimal host so the composable's onMounted hook actually fires.
const Host = defineComponent({
  props: { name: { type: String, required: true } },
  setup(props) {
    return useChartData(props.name);
  },
  template: "<div />",
});

describe("useChartData", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setActivePinia(createPinia());
  });

  it("requests the full dataset (limit 1000), not the paginated default of 100", async () => {
    mount(Host, { props: { name: "wealth-shares" } });
    await flushPromises();
    expect(fetchDataset).toHaveBeenCalledWith("wealth-shares", 1, 1000);
  });

  it("exposes the returned rows once loaded", async () => {
    const wrapper = mount(Host, { props: { name: "wealth-shares" } });
    await flushPromises();
    expect((wrapper.vm as unknown as { rows: unknown[] }).rows).toHaveLength(1);
    expect((wrapper.vm as unknown as { loading: boolean }).loading).toBe(false);
  });
});
