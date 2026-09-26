import { readFileSync } from "node:fs"
import { resolve } from "node:path"
import { afterEach, describe, expect, it } from "vitest"
import {
  OBSERVATORY_SCRIPT_ATTR,
  PRERENDER_FLAG,
  findObservatoryScript,
  isEmbedPath,
  isPrerendering,
  mountObservatory,
  notePulseboardNavigation,
  observatoryScriptUrl,
  releasePulseboardBar,
  startObservatory,
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

describe("Pulseboard SDK v3 host wiring (Pulseboard#105)", () => {
  const html = readFileSync(resolve(__dirname, "../../../index.html"), "utf-8")
  const artifact = readFileSync(resolve(__dirname, "../../../public/observatory.js"), "utf-8")

  function placeholder(): HTMLElement {
    const node = document.createElement("div")
    node.setAttribute("data-pulseboard-bar", "")
    node.style.minHeight = "2.5rem"
    document.body.prepend(node)
    return node
  }

  function fakeWindow(pathname: string, framed = false): Window {
    const self = {} as Record<string, unknown>
    Object.assign(self, { location: { pathname }, self, top: framed ? {} : self })
    return self as unknown as Window
  }

  afterEach(() => {
    document.querySelectorAll("script, [data-pulseboard-bar]").forEach((el) => el.remove())
    delete (window as unknown as Record<string, unknown>).Pulseboard
    delete (window as unknown as Record<string, unknown>)[PRERENDER_FLAG]
  })

  it("reserves the bar space as the first element of <body> with min-height, never height", () => {
    const doc = new DOMParser().parseFromString(html, "text/html")
    const first = doc.body.firstElementChild as HTMLElement
    expect(first.hasAttribute("data-pulseboard-bar")).toBe(true)
    expect(first.style.minHeight).toBe("2.5rem")
    expect(first.style.height).toBe("")
    expect(first.childElementCount).toBe(0)
  })

  it("ships the SDK 3.1 artifact for wealthlens at the path the loader requests", () => {
    expect(artifact).toContain("pulseboard-sdk 3.1.0 for wealthlens")
    expect(artifact).toContain(
      '"collector":"https://pulseboard-observatory.commit-atlas.workers.dev"',
    )
    expect(observatoryScriptUrl(BASE, VERSION)).toMatch(/\/observatory\.js\?v=/)
  })

  it("loads the SDK on a production page and keeps the reservation for it", () => {
    const bar = placeholder()
    const script = startObservatory({
      enabled: true,
      base: BASE,
      version: VERSION,
      win: fakeWindow("/wealthlens-hq/charts/wealth-shares"),
    })
    expect(script?.getAttribute("src")).toBe(`${BASE}observatory.js?v=${VERSION}`)
    expect(bar.hasAttribute("hidden")).toBe(false)
  })

  it.each([
    ["a build without the flag", false, "/wealthlens-hq/", false],
    ["an embed route", true, "/wealthlens-hq/embed/wealth-shares", false],
    ["a framed page", true, "/wealthlens-hq/", true],
  ])("does not load the SDK in %s and releases the reserved space", (_, enabled, path, framed) => {
    const bar = placeholder()
    const script = startObservatory({
      enabled,
      base: BASE,
      version: VERSION,
      win: fakeWindow(path, framed),
    })
    expect(script).toBeNull()
    expect(findObservatoryScript()).toBeNull()
    expect(bar.hasAttribute("hidden")).toBe(true)
    expect(bar.style.minHeight).toBe("0px")
  })

  it("leaves the reservation in the prerender snapshot for the live page", () => {
    const bar = placeholder()
    ;(window as unknown as Record<string, unknown>)[PRERENDER_FLAG] = true
    expect(startObservatory({ enabled: true, base: BASE, version: VERSION })).toBeNull()
    expect(bar.hasAttribute("hidden")).toBe(false)
  })

  it("bakes snapshots without the reservation when the flag is off", () => {
    const bar = placeholder()
    ;(window as unknown as Record<string, unknown>)[PRERENDER_FLAG] = true
    expect(startObservatory({ enabled: false, base: BASE, version: VERSION })).toBeNull()
    expect(bar.hasAttribute("hidden")).toBe(true)
  })

  it("bakes embed snapshots without the reservation, since embeds never load the SDK", () => {
    const bar = placeholder()
    const win = fakeWindow("/wealthlens-hq/embed/wealth-shares")
    ;(win as unknown as Record<string, unknown>)[PRERENDER_FLAG] = true
    expect(startObservatory({ enabled: true, base: BASE, version: VERSION, win })).toBeNull()
    expect(bar.hasAttribute("hidden")).toBe(true)
  })

  it("recognises only embed paths under the base", () => {
    expect(isEmbedPath("/wealthlens-hq/embed/x", BASE)).toBe(true)
    expect(isEmbedPath("/wealthlens-hq/embedded", BASE)).toBe(false)
    expect(isEmbedPath("/wealthlens-hq/", BASE)).toBe(false)
  })

  it("releasing a missing placeholder is a no-op", () => {
    expect(() => releasePulseboardBar()).not.toThrow()
  })

  it("product navigation survives window.Pulseboard being undefined or throwing", () => {
    expect((window as unknown as Record<string, unknown>).Pulseboard).toBeUndefined()
    expect(notePulseboardNavigation(false)).toBe(false)
    ;(window as unknown as Record<string, unknown>).Pulseboard = {
      route() {
        throw new Error("blocked")
      },
    }
    expect(() => notePulseboardNavigation(false)).not.toThrow()
    expect(notePulseboardNavigation(false)).toBe(false)
  })

  it("records later navigations on the registered home route only, never the landing page", () => {
    const routes: string[] = []
    ;(window as unknown as Record<string, unknown>).Pulseboard = {
      route(name: string) {
        routes.push(name)
        return true
      },
    }
    expect(notePulseboardNavigation(true)).toBe(false)
    expect(notePulseboardNavigation(false)).toBe(true)
    expect(routes).toEqual(["home"])
  })
})
