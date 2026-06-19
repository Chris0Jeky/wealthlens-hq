import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { resolve } from 'path'

export default defineConfig({
  base: '/wealthlens-hq/',
  plugins: [vue(), tailwindcss()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
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
        // unblocks the Vite/Rollup dependency upgrades. Behaviour is unchanged:
        // the same two manual chunks are produced.
        manualChunks(id) {
          // Heavy charting library (incl. its private zrender renderer) —
          // isolated so it only loads on chart routes. Check this before the
          // framework rule so `vue-echarts` lands here, not in vue-vendor.
          if (/[\\/]node_modules[\\/](echarts|zrender|vue-echarts)[\\/]/.test(id)) {
            return "echarts";
          }
          // Framework core (Vue runtime + its @vue/* internals, router, Pinia)
          // — cached across all routes.
          if (/[\\/]node_modules[\\/](vue|@vue|vue-router|pinia)[\\/]/.test(id)) {
            return "vue-vendor";
          }
          return undefined;
        },
      },
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
