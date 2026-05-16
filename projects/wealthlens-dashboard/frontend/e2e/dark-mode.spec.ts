import { test, expect } from '@playwright/test'

test.describe('Dark mode', () => {
  test('toggle dark mode via button click', async ({ page }) => {
    await page.goto('/')
    const themeButton = page.getByRole('button', { name: /switch theme/i })
    await expect(themeButton).toBeVisible()

    // Click until we reach dark mode (cycles through light -> dark -> system)
    const html = page.locator('html')
    const maxClicks = 3
    for (let i = 0; i < maxClicks; i++) {
      await themeButton.click()
      if (await html.evaluate((el) => el.classList.contains('dark'))) break
    }
    await expect(html).toHaveClass(/dark/)
  })

  test('html element has dark class after toggle to dark', async ({ page }) => {
    await page.goto('/')
    const themeButton = page.getByRole('button', { name: /switch theme/i })

    for (let i = 0; i < 3; i++) {
      await themeButton.click()
      if (
        await page
          .locator('html')
          .evaluate((el) => el.classList.contains('dark'))
      )
        break
    }
    await expect(page.locator('html')).toHaveClass(/dark/)
  })

  test('persists across page reload', async ({ page }) => {
    await page.goto('/')
    const themeButton = page.getByRole('button', { name: /switch theme/i })

    for (let i = 0; i < 3; i++) {
      await themeButton.click()
      if (
        await page
          .locator('html')
          .evaluate((el) => el.classList.contains('dark'))
      )
        break
    }

    const stored = await page.evaluate(() =>
      localStorage.getItem('wealthlens-theme'),
    )
    expect(stored).toBe('dark')

    await page.reload()
    await expect(page.locator('html')).toHaveClass(/dark/)
  })

  test('toggle back to light mode', async ({ page }) => {
    await page.goto('/')
    await page.evaluate(() =>
      localStorage.setItem('wealthlens-theme', 'dark'),
    )
    await page.reload()
    await expect(page.locator('html')).toHaveClass(/dark/)

    const themeButton = page.getByRole('button', { name: /switch theme/i })
    for (let i = 0; i < 3; i++) {
      await themeButton.click()
      if (
        !(await page
          .locator('html')
          .evaluate((el) => el.classList.contains('dark')))
      )
        break
    }
    await expect(page.locator('html')).not.toHaveClass(/dark/)
  })
})
