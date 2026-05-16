/**
 * useDataFreshness — Composable for fetching and caching data freshness metadata.
 *
 * Loads `/data/freshness.json` once per session (module-scope cache) and
 * exposes per-dataset freshness info: last updated date, source name, and
 * whether the data is considered stale (> 30 days old).
 */
import { ref, type Ref } from "vue";

/** Shape of a single entry in freshness.json. */
export interface FreshnessEntry {
  last_updated: string;
  source: string;
}

/** Return type for a resolved freshness lookup. */
export interface FreshnessInfo {
  lastUpdated: Date;
  source: string;
  isStale: boolean;
}

/** Module-scope cache: loaded once, shared across all component instances. */
let cachedData: Record<string, FreshnessEntry> | null = null;
let fetchPromise: Promise<Record<string, FreshnessEntry> | null> | null = null;

/**
 * Fetches freshness.json from the public directory.
 * Returns null if the file doesn't exist or can't be parsed.
 */
async function loadFreshnessData(): Promise<Record<string, FreshnessEntry> | null> {
  if (cachedData) return cachedData;

  if (!fetchPromise) {
    fetchPromise = fetch("/data/freshness.json")
      .then((res) => {
        if (!res.ok) return null;
        return res.json() as Promise<Record<string, FreshnessEntry>>;
      })
      .then((data) => {
        cachedData = data;
        return data;
      })
      .catch(() => {
        return null;
      });
  }

  return fetchPromise;
}

/**
 * Composable that returns reactive freshness info for a given dataset slug.
 *
 * @param dataset - The dataset slug (e.g. "wealth-shares")
 * @returns Reactive refs for freshnessInfo (null if unavailable) and loading state
 */
export function useDataFreshness(dataset: Ref<string> | string) {
  const freshnessInfo = ref<FreshnessInfo | null>(null);
  const loading = ref(true);

  const datasetValue = typeof dataset === "string" ? dataset : dataset.value;

  loadFreshnessData().then((data) => {
    loading.value = false;
    if (!data || !(datasetValue in data)) {
      freshnessInfo.value = null;
      return;
    }

    const entry = data[datasetValue];
    const lastUpdated = new Date(entry.last_updated);
    const now = new Date();
    const diffMs = now.getTime() - lastUpdated.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    freshnessInfo.value = {
      lastUpdated,
      source: entry.source,
      isStale: diffDays > 30,
    };
  });

  return { freshnessInfo, loading };
}

/**
 * Returns the number of days between a date and now.
 */
export function daysAgo(date: Date): number {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  return Math.floor(diffMs / (1000 * 60 * 60 * 24));
}

/**
 * Returns a human-readable relative time string.
 * Examples: "today", "1 day ago", "2 weeks ago", "3 months ago"
 */
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

/**
 * Resets the module-scope cache. Useful for testing.
 */
export function _resetCache(): void {
  cachedData = null;
  fetchPromise = null;
}
