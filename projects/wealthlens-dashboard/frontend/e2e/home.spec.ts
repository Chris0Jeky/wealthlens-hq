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
    await expect(page.getByRole('link', { name: /about/i })).toBeVisible()
    await expect(
      page.getByRole('link', { name: /the data/i }),
    ).toBeVisible()
  })

  test('dataset cards render', async ({ page }) => {
    await page.goto('/')
    const cards = page.locator('[role="listitem"]')
    await expect(cards.first()).toBeVisible({ timeout: 10000 })
  })
})
