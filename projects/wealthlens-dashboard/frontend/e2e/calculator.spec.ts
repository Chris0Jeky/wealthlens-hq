import { test, expect } from '@playwright/test'

test.describe('Wealth Calculator', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('./tools/wealth-calculator')
  })

  test('page loads with calculator heading', async ({ page }) => {
    await expect(
      page.getByRole('heading', { name: /where do you fit/i }),
    ).toBeVisible()
  })

  test('enter value and calculate shows results', async ({ page }) => {
    await page.locator('#wealth-input').fill('150000')
    await page.getByRole('button', { name: /calculate/i }).click()
    await expect(page.getByText(/your position/i)).toBeVisible()
    await expect(page.getByText(/decile/i)).toBeVisible()
  })

  test('preset buttons fill input', async ({ page }) => {
    await page.getByRole('button', { name: /median/i }).click()
    const input = page.locator('#wealth-input')
    await expect(input).not.toHaveValue('')
  })

  test('comparison stats appear after calculation', async ({ page }) => {
    await page.locator('#wealth-input').fill('302500')
    await page.getByRole('button', { name: /calculate/i }).click()
    await expect(page.getByText(/how you compare/i)).toBeVisible()
  })
})
