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
    // Build in static-data mode and prerender (ADR 0001) so e2e exercises the
    // exact artifact GitHub Pages deploys: baked HTML + static JSON data.
    command: "npm run build && npm run prerender && npm run preview",
    port: 4173,
    reuseExistingServer: !isCI,
    env: { VITE_STATIC_DATA: "true" },
    timeout: 300_000,
  },
})
