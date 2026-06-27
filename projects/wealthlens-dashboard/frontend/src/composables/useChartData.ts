import { onMounted, ref, shallowRef } from "vue";
import { useDataStore, type DatasetRow } from "@/stores/data";

export function useChartData(datasetName: string) {
  const store = useDataStore();
  const rows = shallowRef<DatasetRow[]>([]);
  const loading = ref(true);
  const error = ref<string | null>(null);

  onMounted(async () => {
    try {
      // Request the full dataset. The live API paginates with a default limit of
      // 100, but charts render EVERY row, so the default would silently truncate
      // larger datasets (housing-affordability has 348 rows, wealth-shares 250),
      // dropping whole regions/years and presenting partial data as complete. 1000
      // is the backend max (Query le=1000) and covers all current datasets; the
      // static-build path ignores these args.
      const response = await store.fetchDataset(datasetName, 1, 1000);
      rows.value = response.data;
    } catch (e) {
      error.value = e instanceof Error ? e.message : `Failed to load ${datasetName}`;
    } finally {
      loading.value = false;
    }
  });

  return { rows, loading, error };
}
