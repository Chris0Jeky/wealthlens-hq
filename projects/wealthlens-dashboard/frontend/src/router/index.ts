import { createRouter, createWebHistory } from "vue-router";

const VALID_CHARTS = new Set([
  "wealth-shares",
  "housing-affordability",
  "wealth-by-decile",
  "cgt-concentration",
]);

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "home",
      component: () => import("@/views/HomeView.vue"),
    },
    {
      path: "/charts/:name",
      name: "chart",
      component: () => import("@/views/ChartView.vue"),
      beforeEnter(to) {
        if (!VALID_CHARTS.has(to.params.name as string)) {
          return { name: "not-found", params: { pathMatch: ["charts", to.params.name as string] } };
        }
      },
    },
    {
      path: "/:pathMatch(.*)*",
      name: "not-found",
      component: () => import("@/views/NotFoundView.vue"),
    },
  ],
});

export default router;
