import { defineConfig, devices } from "@playwright/test"

const isCI = !!process.env.CI

export default defineConfig({
  testDir: "e2e",
  fullyParallel: true,
  forbidOnly: isCI,
  retries: isCI ? 1 : 0,
  workers: isCI ? 1 : undefined,
  reporter: "html",
  use: {
    baseURL: "http://localhost:4173/wealthlens-hq/",
    trace: "on-first-retry",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: {
    command: "npm run build && npm run preview",
    port: 4173,
    reuseExistingServer: !isCI,
  },
})
