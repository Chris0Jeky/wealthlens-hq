import { test, expect } from "@playwright/test"

const LANDINGS = [
  { path: "", chunk: "HomeView", embed: false },
  { path: "charts/wealth-shares", chunk: "ChartView", embed: false },
  { path: "tools/wealth-calculator", chunk: "WealthCalculatorView", embed: false },
  { path: "embed/wealth-shares", chunk: "EmbedChartView", embed: true },
  { path: "404.html", chunk: "NotFoundView", embed: false },
]

interface BootMeasurements {
  entryLoaded: boolean
  cls: number
  footerShift: number
}

test.describe("initial lazy route over the baked snapshot", () => {
  test.use({ viewport: { width: 412, height: 823 }, serviceWorkers: "block" })

  for (const landing of LANDINGS) {
    test(`retains readable ${landing.path || "home"} while its initial chunk is delayed`, async ({
      page,
    }, testInfo) => {
      // An explicit gate, not a sleep: the real entry runs while its initial
      // lazy view is unavailable. This catches a transient empty RouterView
      // that assertions against the final settled page cannot detect.
      let release!: () => void
      const gate = new Promise<void>((resolve) => (release = resolve))
      let requested!: () => void
      const chunkRequested = new Promise<void>((resolve) => (requested = resolve))
      await page.route(new RegExp(`/assets/${landing.chunk}-[^/]+\\.js$`), async (route) => {
        requested()
        await gate
        await route.continue()
      })
      await page.addInitScript(() => {
        const state: BootMeasurements = { entryLoaded: false, cls: 0, footerShift: 0 }
        ;(window as unknown as { __wlBoot: BootMeasurements }).__wlBoot = state
        document.addEventListener(
          "load",
          (event) => {
            const node = event.target
            if (node instanceof HTMLScriptElement && node.type === "module") {
              state.entryLoaded = true
            }
          },
          true,
        )
        new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            const shift = entry as PerformanceEntry & {
              hadRecentInput: boolean
              value: number
              sources?: { node?: Node }[]
            }
            if (shift.hadRecentInput) continue
            state.cls += shift.value
            if (shift.sources?.some((source) => source.node?.nodeName === "FOOTER")) {
              state.footerShift += shift.value
            }
          }
        }).observe({ type: "layout-shift", buffered: true })
      })

      try {
        await page.goto(landing.path, { waitUntil: "domcontentloaded" })
        await chunkRequested
        await page.waitForFunction(
          () => (window as unknown as { __wlBoot: BootMeasurements }).__wlBoot.entryLoaded,
        )
        // Allow the pending state to paint, rather than checking within one task.
        await page.evaluate(
          () =>
            new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve))),
        )
        await expect(page.locator("#app[data-v-app]")).toHaveCount(0)
        await expect(page.locator(landing.embed ? ".embed-title" : "main h1").first()).toBeVisible()
        await expect(page.locator('meta[data-wl-meta][property="og:title"]')).toHaveCount(1)
      } finally {
        release()
      }

      await expect(page.locator("#app[data-v-app]")).toHaveCount(1)
      await page.waitForLoadState("networkidle")
      await expect(page.locator(landing.embed ? ".embed-title" : "main h1").first()).toBeVisible()
      await expect(page.locator('meta[property="og:title"]')).toHaveCount(1)
      await expect(page.locator('link[rel="canonical"]')).toHaveCount(
        landing.path === "404.html" ? 0 : 1,
      )
      await expect(page.locator('footer[role="contentinfo"]')).toHaveCount(landing.embed ? 0 : 1)
      await expect(page.locator("[data-pulseboard-bar]")).toBeHidden()
      await testInfo.attach("mobile-bootstrap-measurements", {
        body: JSON.stringify(
          await page.evaluate(() => (window as unknown as { __wlBoot: BootMeasurements }).__wlBoot),
          null,
          2,
        ),
        contentType: "application/json",
      })
    })
  }
})
