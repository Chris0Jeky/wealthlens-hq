/**
 * Bootstrap for the vendored Pulseboard SDK v3 (public/observatory.js; Pulseboard#105).
 *
 * The SDK shows a Beta consent bar on the published site and only runs on the
 * registered origin (https://chris0jeky.github.io); see observatory/README.md. This
 * module guarantees how it is loaded, so that it cannot double-count or serve stale
 * bytes:
 *
 * - Single instance: never inject while the build-time prerender (ADR 0001) is
 *   snapshotting, so no tag is baked into the static HTML; and at runtime never
 *   append a second tag when one is already in the document.
 * - Versioned URL: the request carries `?v=<digest prefix>`, derived at build time
 *   from the locked artifact (scripts/observatory-version.mjs), so the service
 *   worker's cache-first script branch keys a regenerated adapter as a new URL.
 * - Not in embeds: /embed/* charts and any framed copy of the site never load it,
 *   so a third-party page embedding a chart never shows the Beta bar.
 * - Reserved space: App.vue renders `[data-pulseboard-bar]` (min-height 2.5rem, static,
 *   v-once) right after the skip link. The SDK releases it itself when no bar shows;
 *   wherever the SDK is not loaded (flag off, dev, tests, embeds) or its script fails
 *   to load, this module releases it. The prerender snapshot
 *   keeps the reservation for the live page only when the SDK will load there.
 * - Default off: only a production build with `VITE_PULSEBOARD=on` loads it; the
 *   deploy workflow sets that flag (owner decision, Pulseboard#105).
 *
 * Every call into `window.Pulseboard` is optional and guarded: the product works
 * unchanged when the SDK is absent, blocked or throwing. No product event carries
 * figures, amounts or anything a visitor typed; only the registered `home` route.
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
  // A blocked or failed SDK load must not leave an empty reserved strip.
  script.addEventListener("error", () => releasePulseboardBar(doc))
  doc.head.append(script)
  return script
}

/** The host's reserved bar space; the SDK renders its Beta bar into it. */
export const PULSEBOARD_BAR_SELECTOR = "[data-pulseboard-bar]"

/** Collapse the reserved bar space exactly as the SDK does when no bar shows. */
export function releasePulseboardBar(doc: Document = document): void {
  const node = doc.querySelector<HTMLElement>(PULSEBOARD_BAR_SELECTOR)
  if (!node) return
  node.style.height = "0"
  node.style.minHeight = "0"
  node.style.overflow = "hidden"
  node.setAttribute("hidden", "")
}

/** True inside any iframe, including a sandboxed one where touching `top` throws. */
export function isFramed(win: Window = window): boolean {
  try {
    return win.self !== win.top
  } catch {
    return true
  }
}

export function isEmbedPath(pathname: string, base: string): boolean {
  return pathname.startsWith(`${base}embed/`) || pathname === `${base}embed`
}

export interface StartObservatoryOptions extends MountObservatoryOptions {
  /** Production build AND `VITE_PULSEBOARD=on` (default off; the deploy workflow turns it on). */
  enabled: boolean
}

/**
 * Decide whether this page loads the SDK. Returns the adapter tag, or null when it
 * was not loaded (prerender, flag off, embed or framed page).
 */
export function startObservatory({
  enabled,
  base,
  version,
  doc = document,
  win = window,
}: StartObservatoryOptions): HTMLScriptElement | null {
  // With the flag off, and on embeds (which never load the SDK), the snapshot is baked
  // without the reservation too.
  if (!enabled || isEmbedPath(win.location.pathname, base)) {
    releasePulseboardBar(doc)
    return null
  }
  if (isPrerendering(win)) return null
  if (isFramed(win)) {
    releasePulseboardBar(doc)
    return null
  }
  return mountObservatory({ base, version, doc, win })
}

interface PulseboardApi {
  route?: (name: string) => unknown
}

/**
 * Record an in-app navigation as a `page.view` on the registered `home` route (the
 * only route Pulseboard registers for WealthLens). The first navigation is skipped:
 * the SDK records the landing page itself. Never throws; returns whether the SDK
 * accepted the call.
 */
export function notePulseboardNavigation(initial: boolean, win: Window = window): boolean {
  if (initial) return false
  try {
    const api = (win as unknown as { Pulseboard?: PulseboardApi }).Pulseboard
    return api?.route?.("home") === true
  } catch {
    return false
  }
}
