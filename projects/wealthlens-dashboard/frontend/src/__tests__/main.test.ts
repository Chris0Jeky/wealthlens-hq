import { afterEach, describe, expect, it, vi } from "vitest"
import { h, nextTick, type App } from "vue"
import { createMemoryHistory, createRouter, type Router } from "vue-router"
import { usePageMeta } from "@/composables/usePageMeta"

let router: Router | undefined

afterEach(() => {
  const container = document.getElementById("app") as (HTMLElement & { __vue_app__?: App }) | null
  container?.__vue_app__?.unmount()
  router = undefined
  document.body.innerHTML = ""
  document.head.querySelectorAll("[data-wl-meta]").forEach((element) => element.remove())
  document.head
    .querySelectorAll("script[data-wl-observatory]")
    .forEach((element) => element.remove())
  vi.doUnmock("@/router")
  vi.restoreAllMocks()
  vi.unstubAllEnvs()
  vi.unstubAllGlobals()
  vi.resetModules()
})

describe("initial route bootstrap", () => {
  it.each([false, true])(
    "keeps baked content and metadata until readiness (SDK enabled: %s)",
    async (sdkEnabled) => {
      vi.stubEnv("PROD", sdkEnabled)
      vi.stubEnv("VITE_PULSEBOARD", sdkEnabled ? "on" : "off")
      const noteRoute = vi.fn(() => true)
      if (sdkEnabled) vi.stubGlobal("Pulseboard", { route: noteRoute })
      document.body.innerHTML =
        '<div id="app" data-v-app><main id="baked-main">Baked route</main></div>'
      document.head.innerHTML = '<meta data-wl-meta property="og:title" content="Baked title">'
      const bakedMain = document.getElementById("baked-main")!
      const bakedMeta = document.head.querySelector("[data-wl-meta]")!
      let releaseRoute!: () => void
      let importStarted!: () => void
      const started = new Promise<void>((resolve) => (importStarted = resolve))
      const pending = new Promise<void>((resolve) => (releaseRoute = resolve))
      let mounts = 0
      const view = {
        setup() {
          mounts++
          usePageMeta({ title: "Live route", url: "https://example.com/" })
          return () => h("h1", "Live route")
        },
      }
      router = createRouter({
        history: createMemoryHistory(),
        routes: [
          {
            path: "/",
            component: async () => {
              importStarted()
              await pending
              return view
            },
          },
          { path: "/:pathMatch(.*)*", component: view },
        ],
      })
      vi.doMock("@/router", () => ({ default: router }))

      // Execute the real entry point with a real router/Vue mount. Only the
      // initial view loader is controlled, matching a slow lazy-route download.
      await import("@/main")
      await started
      await nextTick()

      try {
        expect(bakedMain.isConnected).toBe(true)
        expect(bakedMeta.isConnected).toBe(true)
        expect(
          (document.getElementById("app") as HTMLElement & { __vue_app__?: App }).__vue_app__,
        ).toBeUndefined()
        expect(mounts).toBe(0)
      } finally {
        releaseRoute()
        await router.isReady()
        await nextTick()
      }

      expect(bakedMain.isConnected).toBe(false)
      expect(bakedMeta.isConnected).toBe(false)
      expect(document.querySelector("main h1")?.textContent).toBe("Live route")
      expect(mounts).toBe(1)
      expect(document.head.querySelectorAll('meta[property="og:title"]')).toHaveLength(1)
      expect(document.head.querySelectorAll('link[rel="canonical"]')).toHaveLength(1)
      // The SDK must see the *newly mounted* reservation, not only the baked
      // node that createApp replaces. Loading and navigation remain single-shot.
      expect(document.querySelector("[data-pulseboard-bar]")?.hasAttribute("hidden")).toBe(
        !sdkEnabled,
      )
      expect(document.querySelectorAll("script[data-wl-observatory]")).toHaveLength(
        sdkEnabled ? 1 : 0,
      )
      expect(noteRoute).not.toHaveBeenCalled()
      if (sdkEnabled) {
        await router.push("/about")
        expect(noteRoute).toHaveBeenCalledExactlyOnceWith("home")
        expect(document.querySelectorAll("script[data-wl-observatory]")).toHaveLength(1)
      }
    },
  )

  it("mounts a non-prerendered entry after its initial route resolves", async () => {
    document.body.innerHTML = '<div id="app"></div>'
    const view = { render: () => h("h1", "Dev route") }
    router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: "/:pathMatch(.*)*", component: async () => view }],
    })
    vi.doMock("@/router", () => ({ default: router }))

    await import("@/main")
    await router.isReady()
    await nextTick()

    expect(document.querySelector("#app[data-v-app] main h1")?.textContent).toBe("Dev route")
    expect(document.querySelector("[data-pulseboard-bar]")?.hasAttribute("hidden")).toBe(true)
  })

  it("retains the baked fallback and reports a rejected initial route import", async () => {
    document.body.innerHTML =
      '<div id="app" data-v-app><main id="baked-main">Baked route</main></div>'
    document.head.innerHTML = '<meta data-wl-meta property="og:title" content="Baked title">'
    const bakedMain = document.getElementById("baked-main")!
    const bakedMeta = document.head.querySelector("[data-wl-meta]")!
    const error = new Error("Route download failed")
    const report = vi.spyOn(console, "error").mockImplementation(() => {})
    router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: "/", component: () => Promise.reject(error) }],
    })
    router.onError(() => {})
    vi.doMock("@/router", () => ({ default: router }))

    await import("@/main")
    await expect(router.isReady()).rejects.toBe(error)
    await nextTick()

    expect(bakedMain.isConnected).toBe(true)
    expect(bakedMeta.isConnected).toBe(true)
    expect(
      (document.getElementById("app") as HTMLElement & { __vue_app__?: App }).__vue_app__,
    ).toBeUndefined()
    expect(report).toHaveBeenCalledWith("[App] Initial route failed:", error)

    router.addRoute({ path: "/recovered", component: { render: () => h("h1", "Recovered route") } })
    await router.push("/recovered")
    await nextTick()
    expect(document.querySelector("main h1")?.textContent).toBe("Recovered route")
    expect(bakedMain.isConnected).toBe(false)
  })

  it("keeps navigation usable after an empty entry fails and recovers on a later route", async () => {
    document.body.innerHTML = '<div id="app">\n </div>'
    const error = new Error("Route download failed")
    vi.spyOn(console, "error").mockImplementation(() => {})
    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: "/", component: () => Promise.reject(error) },
        { path: "/:pathMatch(.*)*", component: { render: () => h("h1", "Recovered route") } },
      ],
    })
    router.onError(() => {})
    vi.doMock("@/router", () => ({ default: router }))

    await import("@/main")
    await expect(router.isReady()).rejects.toBe(error)
    await nextTick()
    expect(document.querySelector("#app[data-v-app] nav")).not.toBeNull()
    expect(document.querySelector("[data-pulseboard-bar]")?.hasAttribute("hidden")).toBe(true)

    await router.push("/recovered")
    await nextTick()
    expect(document.querySelector("main h1")?.textContent).toBe("Recovered route")
  })
})
