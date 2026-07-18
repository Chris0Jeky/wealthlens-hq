import { test, expect } from "@playwright/test"

/**
 * Reuse layer (RFC-001; reality-check F7/F8): the chrome-free /embed shell,
 * the wired ShareBar, and the static CSV mirrors.
 */

test.describe("embed shell (/embed/:chart)", () => {
  test("renders the chart without any site chrome", async ({ page }) => {
    await page.goto("embed/wealth-shares")
    await page.waitForLoadState("networkidle")

    // Chart canvas renders
    await expect(page.locator("canvas").first()).toBeVisible({ timeout: 15000 })
    // No masthead, no footer, no skip link
    await expect(page.locator(".masthead")).toHaveCount(0)
    await expect(page.locator("footer.foot")).toHaveCount(0)
    // Source line + backlink present
    await expect(page.locator(".embed-source")).toContainText("World Inequality Database")
    await expect(page.locator(".embed-backlink")).toHaveAttribute(
      "href",
      /\/charts\/wealth-shares$/,
    )
  })

  test("is prerendered with noindex and canonical pointing at the article", async ({ request }) => {
    const res = await request.get("embed/wealth-shares.html")
    expect(res.status()).toBe(200)
    const html = await res.text()
    expect(html).toMatch(/<meta name="robots"[^>]*content="noindex"/)
    expect(html).toMatch(/rel="canonical"[^>]*charts\/wealth-shares/)
  })

  test("is excluded from the sitemap", async ({ request }) => {
    const xml = await (await request.get("sitemap.xml")).text()
    expect(xml).not.toContain("/embed/")
  })

  test("works inside a sandboxed third-party iframe and auto-resizes it", async ({ page }) => {
    // A minimal "third-party" host page carrying exactly the snippet users copy
    const src = "http://localhost:4173/wealthlens-hq/embed/wealth-shares"
    await page.setContent(`
      <main style="width:800px">
        <iframe src="${src}" width="100%" height="560" style="border:0"
          sandbox="allow-scripts allow-popups" title="Test embed"></iframe>
        <script>
          window.__heights = [];
          window.addEventListener("message", function (e) {
            var d = e.data;
            if (!d || d.source !== "wealthlens-embed" || d.chart !== "wealth-shares") return;
            window.__heights.push(d.height);
            var f = document.querySelector('iframe');
            if (f && typeof d.height === "number" && d.height > 0) f.style.height = Math.ceil(d.height) + "px";
          });
        </script>
      </main>
    `)

    const frame = page.frameLocator("iframe")
    await expect(frame.locator("canvas").first()).toBeVisible({ timeout: 20000 })
    await expect(frame.locator(".embed-backlink")).toBeVisible()

    // The shell posted its height and the host script resized the iframe
    await expect
      .poll(
        async () =>
          page.evaluate(() => (window as unknown as { __heights: number[] }).__heights.length),
        {
          timeout: 10000,
        },
      )
      .toBeGreaterThan(0)
    const height = await page.locator("iframe").evaluate((el) => el.style.height)
    expect(height).toMatch(/^\d+px$/)
    expect(height).not.toBe("560px")
  })
})

test.describe("ShareBar (F7) and CSV mirrors (F8)", () => {
  test("Copy link puts the chart URL on the clipboard", async ({ page, context }) => {
    await context.grantPermissions(["clipboard-read", "clipboard-write"])
    await page.goto("charts/wealth-shares")
    await page.getByRole("button", { name: "Copy link to chart" }).click()
    await expect(page.getByRole("toolbar", { name: /share and download/i })).toContainText(
      "Copied!",
    )
    const copied = await page.evaluate(() => navigator.clipboard.readText())
    expect(copied).toBe("http://localhost:4173/wealthlens-hq/charts/wealth-shares")
  })

  test("PNG download produces a real file", async ({ page }) => {
    await page.goto("charts/wealth-shares")
    await page.waitForLoadState("networkidle")
    const downloadPromise = page.waitForEvent("download")
    await page
      .getByRole("toolbar", { name: /share and download/i })
      .getByRole("button", { name: "Download PNG" })
      .click()
    const download = await downloadPromise
    expect(download.suggestedFilename()).toBe("wealthlens-wealth-shares.png")
  })

  test("chart-page CSV link serves the static mirror with provenance-aware content", async ({
    page,
    request,
  }) => {
    await page.goto("charts/wealth-shares")
    const csvLink = page
      .getByRole("toolbar", { name: /share and download/i })
      .locator("a[download]")
    await expect(csvLink).toHaveAttribute("href", "/wealthlens-hq/data/wealth-shares.csv")

    const res = await request.get("data/wealth-shares.csv")
    expect(res.status()).toBe(200)
    const body = await res.text()
    expect(body.split("\n")[0]).toContain("year")
  })

  test("home-card CSV links resolve on the static deploy (F8)", async ({ page, request }) => {
    await page.goto("/")
    const firstCsv = page.locator('[role="listitem"] a[download]').first()
    const href = await firstCsv.getAttribute("href")
    expect(href).toMatch(/^\/wealthlens-hq\/data\/[a-z-]+\.csv$/)
    const res = await request.get(href as string)
    expect(res.status()).toBe(200)
  })

  test("no CSV affordance for the NC-ND dataset until AR #10", async ({ page, request }) => {
    await page.goto("charts/generational-wealth")
    const toolbar = page.getByRole("toolbar", { name: /share and download/i })
    await expect(toolbar).toBeVisible()
    await expect(toolbar.locator("a[download]")).toHaveCount(0)
    // And the mirror genuinely does not exist. (vite preview answers unknown
    // paths with the SPA fallback shell; GitHub Pages returns a real 404 —
    // so assert "not a CSV" rather than a status code.)
    const res = await request.get("data/generational-wealth.csv")
    const body = await res.text()
    expect(body).not.toContain("generation,")
    expect(res.headers()["content-type"] ?? "").not.toContain("csv")
  })
})
