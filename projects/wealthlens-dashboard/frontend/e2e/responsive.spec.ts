import { test, expect } from '@playwright/test'

test.describe('Responsive layout', () => {
  test('mobile viewport shows hamburger, hides nav links', async ({
    page,
  }) => {
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/')

    const hamburger = page.getByRole('button', {
      name: /toggle navigation/i,
    })
    await expect(hamburger).toBeVisible()

    // Desktop nav links should be hidden at mobile width
    const desktopNav = page.locator('.nav-links')
    await expect(desktopNav).not.toBeVisible()
  })

  test('clicking hamburger opens mobile nav', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/')

    const hamburger = page.getByRole('button', {
      name: /toggle navigation/i,
    })
    await hamburger.click()

    const mobileMenu = page.locator('#mobile-menu')
    await expect(mobileMenu).toBeVisible()
    await expect(
      mobileMenu.getByRole('link', { name: /about/i }),
    ).toBeVisible()
  })

  test('desktop viewport shows full nav, no hamburger', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 800 })
    await page.goto('/')

    const hamburger = page.getByRole('button', {
      name: /toggle navigation/i,
    })
    await expect(hamburger).not.toBeVisible()

    // Desktop nav links should be visible
    const aboutLink = page.locator('.nav-links').getByRole('link', {
      name: /about/i,
    })
    await expect(aboutLink).toBeVisible()
  })
})
