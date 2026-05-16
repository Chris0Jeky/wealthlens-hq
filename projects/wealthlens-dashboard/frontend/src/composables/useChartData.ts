import { onMounted, ref, shallowRef } from "vue";
import { useDataStore, type DatasetRow } from "@/stores/data";

export function useChartData(datasetName: string) {
  const store = useDataStore();
  const rows = shallowRef<DatasetRow[]>([]);
  const loading = ref(true);
  const error = ref<string | null>(null);

  onMounted(async () => {
    try {
      const response = await store.fetchDataset(datasetName);
      rows.value = response.data;
    } catch (e) {
      error.value = e instanceof Error ? e.message : `Failed to load ${datasetName}`;
    } finally {
      loading.value = false;
    }
  });

  return { rows, loading, error };
}
