import { describe, it, expect, vi, beforeEach } from "vitest";
import { setActivePinia, createPinia } from "pinia";
import { useDataStore } from "@/stores/data";

describe("useDataStore", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.restoreAllMocks();
  });

  it("has empty datasets initially", () => {
    const store = useDataStore();
    expect(store.datasets).toEqual([]);
  });

  it("is not loading initially", () => {
    const store = useDataStore();
    expect(store.loading).toBe(false);
  });

  it("has no error initially", () => {
    const store = useDataStore();
    expect(store.error).toBeNull();
  });

  describe("fetchDatasets", () => {
    it("populates the datasets list on success", async () => {
      const mockDatasets = ["wealth-distribution", "income-percentiles", "housing-costs"];
      vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
        ok: true,
        json: async () => ({ datasets: mockDatasets }),
      } as Response);

      const store = useDataStore();
      await store.fetchDatasets();

      expect(store.datasets).toEqual(mockDatasets);
      expect(store.loading).toBe(false);
      expect(store.error).toBeNull();
    });

    it("sets loading to true while fetching", async () => {
      let resolveFetch!: (value: Response) => void;
      vi.spyOn(globalThis, "fetch").mockReturnValueOnce(
        new Promise((resolve) => {
          resolveFetch = resolve;
        }),
      );

      const store = useDataStore();
      const fetchPromise = store.fetchDatasets();
      expect(store.loading).toBe(true);

      resolveFetch({
        ok: true,
        json: async () => ({ datasets: [] }),
      } as Response);
      await fetchPromise;

      expect(store.loading).toBe(false);
    });

    it("sets error on fetch failure", async () => {
      vi.spyOn(globalThis, "fetch").mockRejectedValueOnce(
        new Error("Network error"),
      );

      const store = useDataStore();
      await store.fetchDatasets();

      expect(store.error).toBe("Network error");
      expect(store.loading).toBe(false);
      expect(store.datasets).toEqual([]);
    });
  });

  describe("fetchDataset", () => {
    it("returns data rows on success", async () => {
      const mockData = [
        { decile: 1, wealth: 15000 },
        { decile: 2, wealth: 45000 },
      ];
      vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: mockData }),
      } as Response);

      const store = useDataStore();
      const result = await store.fetchDataset("wealth-distribution");

      expect(result).toEqual(mockData);
      expect(globalThis.fetch).toHaveBeenCalledWith("/api/data/wealth-distribution");
    });

    it("throws on non-ok response", async () => {
      vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
        ok: false,
        status: 404,
      } as Response);

      const store = useDataStore();
      await expect(store.fetchDataset("missing")).rejects.toThrow(
        "Failed to fetch missing",
      );
    });
  });
});
