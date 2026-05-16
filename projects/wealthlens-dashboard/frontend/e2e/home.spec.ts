import { test, expect } from '@playwright/test'

test.describe('Home page', () => {
  test('loads with correct title', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveTitle('WealthLens UK')
  })

  test('main heading is visible', async ({ page }) => {
    await page.goto('/')
    await expect(
      page.getByRole('heading', { name: /wealth inequality dashboard/i }),
    ).toBeVisible()
  })

  test('navigation links are present', async ({ page }) => {
    await page.goto('/')
    const nav = page.getByRole('navigation', { name: /site/i })
    await expect(nav.getByRole('link', { name: /about/i })).toBeVisible()
    await expect(nav.getByRole('link', { name: 'The data', exact: true })).toBeVisible()
  })

  // Requires API or static data fallback — mark as fixme until data layer is stable
  test.fixme('dataset cards render', async ({ page }) => {
    await page.goto('/')
    const cards = page.locator('[role="listitem"]')
    await expect(cards.first()).toBeVisible({ timeout: 10000 })
  })
})
