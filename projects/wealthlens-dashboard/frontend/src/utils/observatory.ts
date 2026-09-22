/**
 * Bootstrap for the vendored Pulseboard Observatory adapter (public/observatory.js).
 *
 * The adapter is inert until a separately reviewed change gives it an endpoint
 * (see observatory/README.md and issue #604). This module only guarantees how it
 * is loaded, so that activation cannot double-count or serve stale bytes:
 *
 * - Single instance: never inject while the build-time prerender (ADR 0001) is
 *   snapshotting, so no tag is baked into the static HTML; and at runtime never
 *   append a second tag when one is already in the document.
 * - Versioned URL: the request carries `?v=<digest prefix>`, derived at build time
 *   from the locked artifact (scripts/observatory-version.mjs), so the service
 *   worker's cache-first script branch keys a regenerated adapter as a new URL.
 */

/** Marker attribute on the injected tag; the idempotence check looks for it. */
export const OBSERVATORY_SCRIPT_ATTR = "data-wl-observatory"

/**
 * Global set by scripts/prerender.ts (via a Playwright init script) before any
 * page script runs. Its presence means "this document is about to be serialised".
 */
export const PRERENDER_FLAG = "__WL_PRERENDER__"

/** Matches any adapter tag, marked or not, versioned or not (e.g. an older baked page). */
const ADAPTER_PATH = /(^|\/)observatory\.js$/

export function isPrerendering(win: Window = window): boolean {
  return (win as unknown as Record<string, unknown>)[PRERENDER_FLAG] === true
}

export function observatoryScriptUrl(base: string, version: string): string {
  const url = `${base}observatory.js`
  return version ? `${url}?v=${encodeURIComponent(version)}` : url
}

export function findObservatoryScript(doc: Document = document): HTMLScriptElement | null {
  const marked = doc.querySelector<HTMLScriptElement>(`script[${OBSERVATORY_SCRIPT_ATTR}]`)
  if (marked) return marked
  for (const script of Array.from(doc.scripts)) {
    const src = script.getAttribute("src")
    if (src && ADAPTER_PATH.test(src.split(/[?#]/)[0])) return script
  }
  return null
}

export interface MountObservatoryOptions {
  base: string
  version: string
  doc?: Document
  win?: Window
}

/**
 * Append the adapter tag at most once. Returns the tag now responsible for the
 * adapter (existing or new), or null when loading was skipped for the prerender.
 */
export function mountObservatory({
  base,
  version,
  doc = document,
  win = window,
}: MountObservatoryOptions): HTMLScriptElement | null {
  if (isPrerendering(win)) return null
  const existing = findObservatoryScript(doc)
  if (existing) return existing
  const script = doc.createElement("script")
  script.src = observatoryScriptUrl(base, version)
  script.defer = true
  script.setAttribute(OBSERVATORY_SCRIPT_ATTR, "")
  doc.head.append(script)
  return script
}
