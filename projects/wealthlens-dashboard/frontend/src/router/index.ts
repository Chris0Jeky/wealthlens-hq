import { createRouter, createWebHistory } from "vue-router";
import { VALID_CHART_NAMES } from "@/constants/charts";

const router = createRouter({
  history: createWebHistory(),
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
      // Placeholder routes — these pages will be built later.
      // For now they resolve to HomeView to avoid dead nav links.
      path: "/methodology",
      name: "methodology",
      component: () => import("@/views/HomeView.vue"),
    },
    {
      path: "/about",
      name: "about",
      component: () => import("@/views/HomeView.vue"),
    },
    {
      path: "/contribute",
      name: "contribute",
      component: () => import("@/views/HomeView.vue"),
    },
    {
      path: "/:pathMatch(.*)*",
      name: "not-found",
      component: () => import("@/views/NotFoundView.vue"),
    },
  ],
});

export default router;
