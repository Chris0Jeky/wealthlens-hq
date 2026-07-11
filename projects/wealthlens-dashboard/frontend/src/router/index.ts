import { createRouter, createWebHistory } from "vue-router"
import { VALID_CHART_NAMES } from "@/constants/charts"

// The /simulator scenario page is always registered. In dev it reads the live
// /api/simulator endpoint; on the static deploy it reads the JSON published by
// scripts/generate_static_api.py (useSimulatorDashboard switches on VITE_STATIC_DATA).
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior(to, _from, savedPosition) {
    if (savedPosition) return savedPosition
    if (to.hash) return { el: to.hash }
    return { top: 0 }
  },
  routes: [
    {
      path: "/",
      name: "home",
      component: () => import("@/views/HomeView.vue"),
    },
    {
      path: "/datasets/:name",
      name: "dataset-detail",
      component: () => import("@/views/DatasetDetailView.vue"),
    },
    {
      path: "/charts/:name",
      name: "chart",
      component: () => import("@/views/ChartView.vue"),
      beforeEnter(to) {
        if (!VALID_CHART_NAMES.has(to.params.name as string)) {
          return { name: "not-found", params: { pathMatch: ["charts", to.params.name as string] } }
        }
      },
    },
    {
      path: "/methodology",
      name: "methodology",
      component: () => import("@/views/MethodologyView.vue"),
    },
    {
      path: "/data-sources",
      name: "data-sources",
      component: () => import("@/views/DataSourcesView.vue"),
    },
    {
      path: "/about",
      name: "about",
      component: () => import("@/views/AboutView.vue"),
    },
    {
      path: "/contribute",
      name: "contribute",
      component: () => import("@/views/ContributeView.vue"),
    },
    {
      path: "/tools/wealth-calculator",
      name: "wealth-calculator",
      component: () => import("@/views/WealthCalculatorView.vue"),
    },
    {
      path: "/tools/wealth-scale",
      name: "wealth-scale",
      component: () => import("@/views/WealthScaleView.vue"),
    },
    {
      path: "/faq",
      name: "faq",
      component: () => import("@/views/FaqView.vue"),
    },
    {
      path: "/tools/wealth-tax-simulator",
      name: "wealth-tax-simulator",
      component: () => import("@/views/WealthTaxSimulatorView.vue"),
    },
    {
      path: "/tools/tax-calculator",
      name: "tax-calculator",
      component: () => import("@/views/TaxCalculatorView.vue"),
    },
    {
      path: "/simulator",
      name: "simulator",
      component: () => import("@/views/SimulatorView.vue"),
    },
    {
      // Chrome-free chart shell for third-party iframes (RFC-001f).
      // meta.embed suppresses the site header/footer in App.vue; the route is
      // prerendered (noindex) but excluded from the sitemap.
      path: "/embed/:name",
      name: "embed",
      component: () => import("@/views/EmbedChartView.vue"),
      meta: { embed: true },
      beforeEnter(to) {
        if (!VALID_CHART_NAMES.has(to.params.name as string)) {
          return { name: "not-found", params: { pathMatch: ["embed", to.params.name as string] } }
        }
      },
    },
    {
      path: "/:pathMatch(.*)*",
      name: "not-found",
      component: () => import("@/views/NotFoundView.vue"),
    },
  ],
})

export default router
