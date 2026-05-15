import { defineStore } from "pinia";
import { ref } from "vue";

export interface DatasetRow {
  [key: string]: string | number | null;
}

export const useDataStore = defineStore("data", () => {
  const datasets = ref<string[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function fetchDatasets(): Promise<void> {
    loading.value = true;
    error.value = null;
    try {
      const res = await fetch("/api/data/");
      const json = await res.json();
      datasets.value = json.datasets;
    } catch (e) {
      error.value = e instanceof Error ? e.message : "Failed to fetch datasets";
    } finally {
      loading.value = false;
    }
  }

  async function fetchDataset(name: string): Promise<DatasetRow[]> {
    const res = await fetch(`/api/data/${name}`);
    if (!res.ok) throw new Error(`Failed to fetch ${name}`);
    const json = await res.json();
    return json.data;
  }

  return { datasets, loading, error, fetchDatasets, fetchDataset };
});
