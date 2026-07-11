import { test, expect } from "@playwright/test"

/**
 * Prerender contract (ADR 0001).
 *
 * The webServer builds + prerenders, so every route is a real HTML file in
 * dist with its meta baked in. These tests check the three legs of F5:
 * raw HTML served with baked per-route meta, meaningful no-JS content, and
 * clean hydration (exactly one live copy of each tag afterwards).
 *
 * Note: HTTP 404-for-unknown-routes is GitHub Pages behaviour (404.html);
 * vite preview serves an SPA fallback with 200 instead, so here we assert
 * the 404.html artifact itself rather than the status code.
 */

const SITE_URL = "https://chris0jeky.github.io/wealthlens-hq"

const DEEP_LINKS = [
  {
    path: "charts/wealth-shares",
    ogUrl: `${SITE_URL}/charts/wealth-shares`,
    ogImage: `${SITE_URL}/og/wealth-shares.png`,
  },
  {
    path: "tools/wealth-scale",
    ogUrl: `${SITE_URL}/tools/wealth-scale`,
    ogImage: `${SITE_URL}/og/og-default.png`,
  },
  {
    path: "simulator",
    ogUrl: `${SITE_URL}/simulator`,
    ogImage: `${SITE_URL}/og/og-default.png`,
  },
]

test.describe("baked HTML (no JavaScript executed — what crawlers see)", () => {
  for (const link of DEEP_LINKS) {
    test(`raw ${link.path} returns 200 with baked route meta`, async ({ request }) => {
      const res = await request.get(link.path)
      expect(res.status()).toBe(200)
      const html = await res.text()

      // Baked, route-specific meta — not the generic shell
      expect(html).toContain(`content="${link.ogUrl}"`)
      expect(html).toContain(`content="${link.ogImage}"`)
      expect(html).toContain(`href="${link.ogUrl}"`) // canonical
      expect(html).toContain("data-wl-meta")
      // Absolute OG image (scrapers ignore relative URLs)
      expect(html).not.toMatch(/property="og:image" content="\/(?!\/)/)
    })
  }

  test("baked chart page carries real article content in the raw HTML", async ({ request }) => {
    const res = await request.get("charts/wealth-shares")
    const html = await res.text()
    expect(html).toContain("<h1")
    // The source line is part of the article — crawlers should see citations
    expect(html.length).toBeGreaterThan(20_000)
  })

  test("404.html is the baked Page-not-found view with noindex", async ({ request }) => {
    const res = await request.get("404.html")
    expect(res.status()).toBe(200)
    const html = await res.text()
    expect(html).toContain("Page not found")
    expect(html).toMatch(/<meta name="robots"[^>]*content="noindex"/)
    expect(html).not.toContain('rel="canonical"')
  })

  test("sitemap.xml lists the prerendered routes with the canonical identity", async ({
    request,
  }) => {
    const res = await request.get("sitemap.xml")
    expect(res.status()).toBe(200)
    const xml = await res.text()
    expect(xml).toContain(`<loc>${SITE_URL}/</loc>`)
    expect(xml).toContain(`<loc>${SITE_URL}/charts/wealth-shares</loc>`)
    expect(xml).toContain(`<loc>${SITE_URL}/tools/wealth-scale</loc>`)
    expect(xml).not.toContain("wealthlens.uk")
    expect(xml).not.toContain("<lastmod>")
  })
})

test.describe("no-JS rendering", () => {
  test.use({ javaScriptEnabled: false })

  test("a deep-linked chart page shows readable content without JavaScript", async ({ page }) => {
    await page.goto("charts/wealth-shares")
    const h1 = page.locator("h1").first()
    await expect(h1).toBeVisible()
    expect((await h1.textContent())?.trim().length).toBeGreaterThan(10)
    // The accessible data fallback ships in the baked HTML
    await expect(page.locator("main")).toContainText(/source/i)
  })
})

test.describe("hydration over baked HTML", () => {
  test("the app takes over: SPA navigation works without a full reload", async ({ page }) => {
    await page.goto("charts/wealth-shares")
    await page.waitForLoadState("networkidle")
    // Marker survives only if navigation stays client-side
    await page.evaluate(() => {
      ;(window as unknown as { __wlE2eMarker: boolean }).__wlE2eMarker = true
    })
    await page
      .getByRole("navigation", { name: /site/i })
      .getByRole("link", { name: /about/i })
      .click()
    await expect(page).toHaveURL(/\/about$/)
    const markerAlive = await page.evaluate(
      () => (window as unknown as { __wlE2eMarker?: boolean }).__wlE2eMarker === true,
    )
    expect(markerAlive).toBe(true)
  })

  test("hydrated page has exactly one live copy of each meta tag", async ({ page }) => {
    await page.goto("charts/wealth-shares")
    await page.waitForLoadState("networkidle")
    const counts = await page.evaluate(() => ({
      ogTitle: document.head.querySelectorAll('meta[property="og:title"]').length,
      ogUrl: document.head.querySelectorAll('meta[property="og:url"]').length,
      canonical: document.head.querySelectorAll('link[rel="canonical"]').length,
      description: document.head.querySelectorAll('meta[name="description"]').length,
    }))
    expect(counts).toEqual({ ogTitle: 1, ogUrl: 1, canonical: 1, description: 1 })
  })

  test("hydrated title matches the baked title (no drift)", async ({ page, request }) => {
    const raw = await (await request.get("charts/wealth-shares")).text()
    const bakedTitle = raw.match(/<title>([^<]+)<\/title>/)?.[1]
    expect(bakedTitle).toBeTruthy()
    await page.goto("charts/wealth-shares")
    await page.waitForLoadState("networkidle")
    await expect(page).toHaveTitle(bakedTitle as string)
  })
})
