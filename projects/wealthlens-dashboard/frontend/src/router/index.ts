import { createRouter, createWebHistory } from "vue-router";
import { VALID_CHART_NAMES } from "@/constants/charts";

// The deployed site builds in static mode (no backend). The /simulator scenario
// page needs the live /api/simulator endpoint, and its data is not published
// statically yet, so the route is registered only in API mode (dev) — a new
// feature off-by-default in production until the static export lands.
const SIMULATOR_ENABLED = import.meta.env.VITE_STATIC_DATA !== "true";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior(to, _from, savedPosition) {
    if (savedPosition) return savedPosition;
    if (to.hash) return { el: to.hash };
    return { top: 0 };
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
          return { name: "not-found", params: { pathMatch: ["charts", to.params.name as string] } };
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
    ...(SIMULATOR_ENABLED
      ? [
          {
            path: "/simulator",
            name: "simulator",
            component: () => import("@/views/SimulatorView.vue"),
          },
        ]
      : []),
    {
      path: "/:pathMatch(.*)*",
      name: "not-found",
      component: () => import("@/views/NotFoundView.vue"),
    },
  ],
});

export default router;
