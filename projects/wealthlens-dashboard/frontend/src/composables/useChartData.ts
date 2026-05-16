import { onMounted, ref } from "vue";
import { useDataStore, type DatasetRow } from "@/stores/data";

export function useChartData(datasetName: string) {
  const store = useDataStore();
  const rows = ref<DatasetRow[]>([]);
  const loading = ref(true);
  const error = ref<string | null>(null);

  onMounted(async () => {
    try {
      rows.value = await store.fetchDataset(datasetName);
    } catch (e) {
      error.value = e instanceof Error ? e.message : `Failed to load ${datasetName}`;
    } finally {
      loading.value = false;
    }
  });

  return { rows, loading, error };
}
