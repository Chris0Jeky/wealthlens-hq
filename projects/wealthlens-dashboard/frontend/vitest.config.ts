import { defineConfig } from "vitest/config"
import vue from "@vitejs/plugin-vue"
import { resolve } from "path"
import { readDataVintage } from "./scripts/data-vintage"
import { readObservatoryVersion } from "./scripts/observatory-version.mjs"

export default defineConfig({
  plugins: [vue()],
  define: {
    // Mirror vite.config.ts so components using the constant are testable.
    __WL_DATA_VINTAGE__: JSON.stringify(readDataVintage()),
    // Locked-digest prefix of public/observatory.js; versions the adapter URL so
    // the service worker cannot pin stale bytes after regeneration (#604).
    __WL_OBSERVATORY_VERSION__: JSON.stringify(readObservatoryVersion()),
  },
  resolve: {
    alias: {
      "@": resolve(__dirname, "src"),
    },
  },
  test: {
    environment: "jsdom",
    include: ["src/**/*.{test,spec}.ts", "scripts/**/*.{test,spec}.ts"],
    setupFiles: ["src/test-setup.ts"],
    coverage: {
      provider: "v8",
      reporter: ["text", "text-summary"],
      include: ["src/**/*.{ts,vue}"],
      exclude: ["src/**/__tests__/**", "src/**/*.test.ts", "src/main.ts"],
    },
  },
})
