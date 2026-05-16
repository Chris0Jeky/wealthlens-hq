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

    it("sets error on non-ok HTTP response", async () => {
      vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ datasets: ["should-not-appear"] }),
      } as unknown as Response);

      const store = useDataStore();
      await store.fetchDatasets();

      expect(store.error).toBe("HTTP 500");
      expect(store.loading).toBe(false);
      expect(store.datasets).toEqual([]);
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

    it("last-resolved fetch overwrites datasets (no cancellation)", async () => {
      let resolveFirst!: (v: Response) => void;
      let resolveSecond!: (v: Response) => void;

      const fetchSpy = vi.spyOn(globalThis, "fetch");
      fetchSpy.mockReturnValueOnce(new Promise(r => { resolveFirst = r; }));
      fetchSpy.mockReturnValueOnce(new Promise(r => { resolveSecond = r; }));

      const store = useDataStore();
      const p1 = store.fetchDatasets();
      const p2 = store.fetchDatasets();

      resolveSecond({ ok: true, json: async () => ({ datasets: ["second"] }) } as Response);
      resolveFirst({ ok: true, json: async () => ({ datasets: ["first"] }) } as Response);

      await Promise.all([p1, p2]);
      expect(store.datasets).toEqual(["first"]);
      expect(store.loading).toBe(false);
      expect(store.error).toBeNull();
    });

    it("clears previous error on successful retry", async () => {
      const fetchSpy = vi.spyOn(globalThis, "fetch");
      fetchSpy.mockRejectedValueOnce(new Error("Network error"));

      const store = useDataStore();
      await store.fetchDatasets();
      expect(store.error).toBe("Network error");

      fetchSpy.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ datasets: ["recovered"] }),
      } as Response);

      await store.fetchDatasets();
      expect(store.error).toBeNull();
      expect(store.datasets).toEqual(["recovered"]);
    });

    it("handles non-Error thrown values", async () => {
      vi.spyOn(globalThis, "fetch").mockRejectedValueOnce("string error");

      const store = useDataStore();
      await store.fetchDatasets();

      expect(store.error).toBe("Failed to fetch datasets");
      expect(store.loading).toBe(false);
    });

    it("sets datasets to undefined when response lacks datasets key", async () => {
      vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),
      } as Response);

      const store = useDataStore();
      await store.fetchDatasets();
      // Store blindly assigns json.datasets — documents current behavior
      expect(store.datasets).toBeUndefined();
      expect(store.error).toBeNull();
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
        json: async () => ({
          data: mockData,
          page: 1,
          limit: 100,
          total: 2,
          total_pages: 1,
        }),
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

    it("includes statusText in error message", async () => {
      vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
        ok: false,
        status: 503,
        statusText: "Service Unavailable",
      } as Response);

      const store = useDataStore();
      await expect(store.fetchDataset("broken")).rejects.toThrow(
        "Failed to fetch broken: 503 Service Unavailable",
      );
    });

    it("propagates network errors to caller", async () => {
      vi.spyOn(globalThis, "fetch").mockRejectedValueOnce(new Error("Network error"));

      const store = useDataStore();
      await expect(store.fetchDataset("any-dataset")).rejects.toThrow("Network error");
    });

    it("returns empty data array without error", async () => {
      vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: [] }),
      } as Response);

      const store = useDataStore();
      const result = await store.fetchDataset("empty-set");

      expect(result).toEqual([]);
    });
  });
});
