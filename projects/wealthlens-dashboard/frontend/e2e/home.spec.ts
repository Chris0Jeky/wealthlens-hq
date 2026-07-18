import { test, expect } from "@playwright/test"

test.describe("Home page (editorial front page)", () => {
  test("loads with correct title", async ({ page }) => {
    await page.goto("/")
    await expect(page).toHaveTitle(/WealthLens UK$/)
  })

  test("leads with the sourced 57% headline figure", async ({ page }) => {
    await page.goto("/")
    const h1 = page.getByRole("heading", { level: 1 })
    await expect(h1).toBeVisible()
    await expect(h1).toContainText("wealthiest 10%")
    await expect(h1).toContainText("57")
    // The claim is cited right below the figure
    await expect(page.locator(".lead-source")).toContainText("World Inequality Database")
  })

  test("navigation links are present", async ({ page }) => {
    await page.goto("/")
    const nav = page.getByRole("navigation", { name: /site/i })
    await expect(nav.getByRole("link", { name: /about/i })).toBeVisible()
    await expect(nav.getByRole("link", { name: "The data", exact: true })).toBeVisible()
  })

  // Locks reality-check F1's class shut: the home page must always offer a
  // working path into the charts (F12 — only e2e can catch this, since view
  // unit tests mock the cards).
  test("a View Chart link exists and navigates to a chart page", async ({ page }) => {
    await page.goto("/")
    const viewChart = page.getByRole("link", { name: /view .* chart/i }).first()
    await expect(viewChart).toBeVisible()
    await viewChart.click()
    await expect(page).toHaveURL(/\/charts\/[a-z-]+$/)
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible()
  })

  test("tools row links resolve (de-orphaned, F6)", async ({ page }) => {
    await page.goto("/")
    for (const href of [
      "tools/wealth-scale",
      "tools/wealth-calculator",
      "tools/tax-calculator",
      "tools/wealth-tax-simulator",
      "faq",
    ]) {
      await expect(page.locator(`a[href="/wealthlens-hq/${href}"]`).first()).toBeAttached()
    }
    // Drive one end-to-end: the most shareable tool
    await page.locator('a[href="/wealthlens-hq/tools/wealth-scale"]').first().click()
    await expect(page).toHaveURL(/\/tools\/wealth-scale$/)
    await expect(page.getByRole("heading", { level: 1 })).toContainText("1 pixel")
  })

  test("chart index lists all 12 charts including the two former orphans", async ({ page }) => {
    await page.goto("/")
    const pillarLinks = page.locator(".pillar-link")
    await expect(pillarLinks).toHaveCount(12)
    await expect(page.locator('a[href="/wealthlens-hq/charts/wage-stagnation"]')).toBeAttached()
    await expect(page.locator('a[href="/wealthlens-hq/charts/inheritance-tax"]')).toBeAttached()
  })

  // The webServer builds with VITE_STATIC_DATA=true, so cards render from
  // the committed static JSON — deterministic, no live API needed.
  test("dataset cards render", async ({ page }) => {
    await page.goto("/")
    const cards = page.locator('[role="listitem"]')
    await expect(cards.first()).toBeVisible({ timeout: 10000 })
  })

  test("masthead carries a data vintage, not a live-updated claim (F4)", async ({ page }) => {
    await page.goto("/")
    await expect(page.locator(".vintage")).toContainText(/^Data as of \d{1,2} \w{3} \d{4}$/)
    await expect(page.locator(".masthead")).not.toContainText("Live · Updated")
  })
})
