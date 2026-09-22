import { afterEach, describe, expect, it } from "vitest"
import {
  OBSERVATORY_SCRIPT_ATTR,
  PRERENDER_FLAG,
  findObservatoryScript,
  isPrerendering,
  mountObservatory,
  observatoryScriptUrl,
} from "../observatory"

const BASE = "/wealthlens-hq/"
const VERSION = "0123456789abcdef"

function adapterTags(): HTMLScriptElement[] {
  return Array.from(document.scripts).filter((s) =>
    /(^|\/)observatory\.js$/.test((s.getAttribute("src") ?? "").split(/[?#]/)[0]),
  )
}

describe("mountObservatory", () => {
  afterEach(() => {
    document.querySelectorAll("script").forEach((el) => el.remove())
    delete (window as unknown as Record<string, unknown>)[PRERENDER_FLAG]
  })

  it("appends exactly one deferred, marked, versioned tag on a plain page", () => {
    const script = mountObservatory({ base: BASE, version: VERSION })

    expect(adapterTags()).toHaveLength(1)
    expect(script).not.toBeNull()
    expect(script?.getAttribute("src")).toBe(`${BASE}observatory.js?v=${VERSION}`)
    expect(script?.defer).toBe(true)
    expect(script?.hasAttribute(OBSERVATORY_SCRIPT_ATTR)).toBe(true)
  })

  it("mounts once when a prerendered page already carries a baked tag", () => {
    // Shape of the tag the pre-#604 prerender baked: unmarked and unversioned.
    const baked = document.createElement("script")
    baked.setAttribute("src", `${BASE}observatory.js`)
    baked.defer = true
    document.head.append(baked)

    const result = mountObservatory({ base: BASE, version: VERSION })

    expect(result).toBe(baked)
    expect(adapterTags()).toHaveLength(1)
  })

  it("is idempotent across repeated boots", () => {
    const first = mountObservatory({ base: BASE, version: VERSION })
    const second = mountObservatory({ base: BASE, version: VERSION })

    expect(second).toBe(first)
    expect(adapterTags()).toHaveLength(1)
  })

  it("injects nothing while the prerender is snapshotting", () => {
    ;(window as unknown as Record<string, unknown>)[PRERENDER_FLAG] = true

    expect(isPrerendering()).toBe(true)
    expect(mountObservatory({ base: BASE, version: VERSION })).toBeNull()
    expect(adapterTags()).toHaveLength(0)
    expect(findObservatoryScript()).toBeNull()
  })

  it("only treats the exact flag value as prerender mode", () => {
    ;(window as unknown as Record<string, unknown>)[PRERENDER_FLAG] = "yes"
    expect(isPrerendering()).toBe(false)
  })

  it("does not mistake unrelated scripts for the adapter", () => {
    const other = document.createElement("script")
    other.setAttribute("src", `${BASE}assets/not-observatory.js`)
    document.head.append(other)

    mountObservatory({ base: BASE, version: VERSION })
    expect(adapterTags()).toHaveLength(1)
  })
})

describe("observatoryScriptUrl", () => {
  it("carries the build-time version as a query string", () => {
    expect(observatoryScriptUrl(BASE, VERSION)).toBe(
      "/wealthlens-hq/observatory.js?v=0123456789abcdef",
    )
  })

  it("falls back to the bare path only when no version is known", () => {
    expect(observatoryScriptUrl(BASE, "")).toBe("/wealthlens-hq/observatory.js")
  })

  it("is fed a 16-hex build-time version in the test build", () => {
    expect(__WL_OBSERVATORY_VERSION__).toMatch(/^[0-9a-f]{16}$/)
  })
})
