import { createRouter, createWebHistory } from "vue-router";
import { VALID_CHART_NAMES } from "@/constants/charts";

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
        if (!VALID_CHART_NAMES.has(to.params.name as string)) {
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
