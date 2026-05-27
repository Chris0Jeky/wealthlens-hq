import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import tailwindcss from '@tailwindcss/vite';
import { resolve } from 'path';
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
                manualChunks: {
                    // Heavy charting library — isolated so it only loads on chart routes
                    echarts: [
                        "echarts",
                        "echarts/core",
                        "echarts/renderers",
                        "echarts/charts",
                        "echarts/components",
                        "vue-echarts",
                    ],
                    // Framework core — cached across all routes
                    "vue-vendor": ["vue", "vue-router", "pinia"],
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
});
