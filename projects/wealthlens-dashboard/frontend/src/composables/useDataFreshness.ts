import { ref, watchEffect, isRef, type Ref } from "vue";

export interface FreshnessEntry {
  last_updated: string;
  source: string;
}

export interface FreshnessInfo {
  lastUpdated: Date;
  source: string;
  isStale: boolean;
}

let cachedData: Record<string, FreshnessEntry> | null = null;
let fetchPromise: Promise<Record<string, FreshnessEntry> | null> | null = null;

const FRESHNESS_URL = `${import.meta.env.BASE_URL}data/freshness.json`;

async function loadFreshnessData(): Promise<Record<string, FreshnessEntry> | null> {
  if (cachedData) return cachedData;

  if (!fetchPromise) {
    fetchPromise = fetch(FRESHNESS_URL)
      .then((res) => {
        if (!res.ok) {
          fetchPromise = null;
          return null;
        }
        return res.json() as Promise<Record<string, FreshnessEntry>>;
      })
      .then((data) => {
        cachedData = data;
        return data;
      })
      .catch(() => {
        fetchPromise = null;
        return null;
      });
  }

  return fetchPromise;
}

export function useDataFreshness(dataset: Ref<string> | string) {
  const freshnessInfo = ref<FreshnessInfo | null>(null);
  const loading = ref(true);

  const datasetRef = isRef(dataset) ? dataset : ref(dataset);

  watchEffect(() => {
    const slug = datasetRef.value;
    loading.value = true;

    loadFreshnessData().then((data) => {
      loading.value = false;
      if (!data || !(slug in data)) {
        freshnessInfo.value = null;
        return;
      }

      const entry = data[slug];
      const lastUpdated = parseDateOnly(entry.last_updated);
      if (!lastUpdated) {
        freshnessInfo.value = null;
        return;
      }

      freshnessInfo.value = {
        lastUpdated,
        source: entry.source,
        isStale: daysAgo(lastUpdated) > 30,
      };
    });
  });

  return { freshnessInfo, loading };
}

export function daysAgo(date: Date): number {
  const now = new Date();
  const todayUTC = Date.UTC(now.getFullYear(), now.getMonth(), now.getDate());
  const dateUTC = Date.UTC(date.getFullYear(), date.getMonth(), date.getDate());
  return Math.max(0, Math.floor((todayUTC - dateUTC) / (1000 * 60 * 60 * 24)));
}

function parseDateOnly(value: string): Date | null {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
  if (!match) return null;

  const year = Number(match[1]);
  const month = Number(match[2]);
  const day = Number(match[3]);
  const date = new Date(year, month - 1, day);

  if (
    date.getFullYear() !== year ||
    date.getMonth() !== month - 1 ||
    date.getDate() !== day
  ) {
    return null;
  }

  return date;
}

export function relativeTime(date: Date): string {
  const days = daysAgo(date);

  if (days === 0) return "today";
  if (days === 1) return "1 day ago";
  if (days < 7) return `${days} days ago`;
  if (days < 14) return "1 week ago";
  if (days < 30) return `${Math.floor(days / 7)} weeks ago`;
  if (days < 60) return "1 month ago";
  return `${Math.floor(days / 30)} months ago`;
}

export function _resetCache(): void {
  cachedData = null;
  fetchPromise = null;
}
