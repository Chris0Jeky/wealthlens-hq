import { META_MARKER_ATTR } from "@/composables/usePageMeta"

/**
 * Remove head elements baked in by the build-time prerender (ADR 0001).
 *
 * Prerendered pages ship with the meta/canonical elements `usePageMeta`
 * had created at snapshot time, marked with `data-wl-meta`. The app strips
 * them once at boot, before mount, and the mounting view's own
 * `usePageMeta` call recreates them — so crawlers see baked meta, hydrated
 * pages carry exactly one copy, and the two can never drift.
 *
 * Returns the number of elements removed (0 on dev/non-prerendered pages).
 */
export function stripPrerenderedMeta(doc: Document = document): number {
  const stale = doc.head.querySelectorAll(`[${META_MARKER_ATTR}]`)
  stale.forEach((el) => el.remove())
  return stale.length
}
