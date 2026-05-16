import { test, expect } from '@playwright/test'

test.describe('Navigation', () => {
  test('navigate to chart page via direct URL', async ({ page }) => {
    await page.goto('/charts/wealth-shares')
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('navigate to about page', async ({ page }) => {
    await page.goto('/')
    await page.getByRole('link', { name: /about/i }).click()
    await expect(page).toHaveURL(/\/about/)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('navigate to wealth calculator', async ({ page }) => {
    await page.goto('/tools/wealth-calculator')
    await expect(page.getByRole('heading', { name: /wealth/i })).toBeVisible()
  })

  test('404 page shows for invalid route', async ({ page }) => {
    await page.goto('/this-does-not-exist')
    await expect(page.getByText(/not found|404/i)).toBeVisible()
  })

  test('back button works', async ({ page }) => {
    await page.goto('/')
    await page.getByRole('link', { name: /about/i }).click()
    await expect(page).toHaveURL(/\/about/)
    await page.goBack()
    await expect(page).toHaveURL(/\/$/)
  })
})
