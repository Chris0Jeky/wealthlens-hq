import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"
import tailwindcss from "@tailwindcss/vite"
import { resolve } from "path"
import { readDataVintage } from "./scripts/data-vintage"

export default defineConfig({
  base: "/wealthlens-hq/",
  plugins: [vue(), tailwindcss()],
  define: {
    // Newest dataset last_updated, baked at build time (masthead honesty —
    // replaces the fabricated new Date() "UPDATED {today}" claim, F4).
    __WL_DATA_VINTAGE__: JSON.stringify(readDataVintage()),
  },
  resolve: {
    alias: {
      "@": resolve(__dirname, "src"),
    },
  },
  build: {
    chunkSizeWarningLimit: 600,
    rollupOptions: {
      output: {
        // Function form (not the object form): newer Rollup type definitions —
        // pulled in transitively by recent esbuild/Vite bumps — only accept a
        // `ManualChunksFunction`, so the object literal raised vite.config.ts
        // TS2769. The function form is backward-compatible across Vite 6+ and
        // unblocks the Vite/Rollup dependency upgrades. For the current
        // dependency tree it yields the same two named chunks (echarts,
        // vue-vendor) — the build output is byte-identical to the object form.
        manualChunks(id) {
          // Heavy charting library (incl. its private zrender renderer) —
          // isolated so it only loads on chart routes. Check this before the
          // framework rule so `vue-echarts` lands here, not in vue-vendor.
          if (/[\\/]node_modules[\\/](echarts|zrender|vue-echarts)[\\/]/.test(id)) {
            return "echarts"
          }
          // Framework core (Vue runtime + its @vue/* internals, router, Pinia)
          // — cached across all routes.
          if (/[\\/]node_modules[\\/](vue|@vue|vue-router|pinia)[\\/]/.test(id)) {
            return "vue-vendor"
          }
          return undefined
        },
      },
    },
  },
  preview: {
    // GitHub Pages serves everything with Access-Control-Allow-Origin: * —
    // mirror that so the sandboxed /embed iframe (opaque origin) can fetch
    // its data in e2e runs exactly as it does in production.
    cors: true,
  },
  server: {
    port: 3000,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
})
