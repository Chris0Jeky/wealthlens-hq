/**
 * Static-deploy download layer (RFC-001a).
 *
 * `scripts/generate_static_api.py` emits a `{slug}.csv` mirror next to each
 * dataset's JSON, so downloads need no backend. This module is the frontend
 * side of that contract.
 */

/**
 * Slugs with NO CSV mirror until the output-licence decision lands
 * (ACTION-REQUIRED #10): the upstream Resolution Foundation series is
 * CC BY-NC-ND 4.0, and a download affordance invites exactly the
 * redistribution ND forbids. Mirrors CSV_MIRROR_EXCLUDED in
 * scripts/generate_static_api.py — change both together.
 */
export const CSV_DOWNLOAD_EXCLUDED: ReadonlySet<string> = new Set(["generational-wealth"])

/** URL of a dataset's CSV mirror on the static deploy. */
export function csvDownloadUrl(slug: string): string {
  return `${import.meta.env.BASE_URL}data/${slug}.csv`
}

/** Whether a CSV download exists for this slug. */
export function hasCsvDownload(slug: string): boolean {
  return !CSV_DOWNLOAD_EXCLUDED.has(slug)
}
