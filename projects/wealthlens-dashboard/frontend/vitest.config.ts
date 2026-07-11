import { defineConfig } from "vitest/config"
import vue from "@vitejs/plugin-vue"
import { resolve } from "path"
import { readDataVintage } from "./scripts/data-vintage"

export default defineConfig({
  plugins: [vue()],
  define: {
    // Mirror vite.config.ts so components using the constant are testable.
    __WL_DATA_VINTAGE__: JSON.stringify(readDataVintage()),
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
