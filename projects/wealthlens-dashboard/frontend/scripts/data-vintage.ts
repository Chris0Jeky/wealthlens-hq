/**
 * Build-time data vintage — the honest replacement for the masthead's old
 * `new Date()` "UPDATED {today}" claim (reality-check F4), which rendered the
 * visitor's clock as if it were a data event.
 *
 * Reads the curated freshness file and returns the newest dataset
 * `last_updated` date, formatted for the masthead ("16 May 2026"). Consumed
 * by vite.config.ts / vitest.config.ts, which inject it as the
 * `__WL_DATA_VINTAGE__` compile-time constant.
 *
 * Returns "" when the file is missing or unparsable — the masthead then
 * shows no vintage claim at all, which is more honest than a made-up date.
 */
import { readFileSync } from "node:fs"
import { dirname, join } from "node:path"
import { fileURLToPath } from "node:url"

const DEFAULT_FRESHNESS_PATH = join(
  dirname(fileURLToPath(import.meta.url)),
  "..",
  "public",
  "data",
  "freshness.json",
)

export function readDataVintage(freshnessPath: string = DEFAULT_FRESHNESS_PATH): string {
  let parsed: unknown
  try {
    parsed = JSON.parse(readFileSync(freshnessPath, "utf-8"))
  } catch {
    return ""
  }
  if (typeof parsed !== "object" || parsed === null) return ""

  let newest = Number.NEGATIVE_INFINITY
  for (const entry of Object.values(parsed as Record<string, unknown>)) {
    const raw =
      typeof entry === "object" && entry !== null
        ? (entry as { last_updated?: unknown }).last_updated
        : undefined
    if (typeof raw !== "string") continue
    const ts = Date.parse(raw)
    if (!Number.isNaN(ts) && ts > newest) newest = ts
  }
  if (!Number.isFinite(newest)) return ""

  return new Date(newest).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  })
}
