import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "home",
      component: () => import("@/views/HomeView.vue"),
      meta: { title: "WealthLens UK — UK Wealth Inequality Data" },
    },
    {
      path: "/charts/:name",
      name: "chart",
      component: () => import("@/views/ChartView.vue"),
      meta: { title: "Chart — WealthLens UK" },
    },
    {
      path: "/:pathMatch(.*)*",
      name: "not-found",
      component: () => import("@/views/NotFoundView.vue"),
      meta: { title: "Page Not Found — WealthLens UK" },
    },
  ],
});

router.afterEach((to) => {
  if (to.name === "chart" && to.params.name) {
    const chartName = String(to.params.name)
      .replace(/-/g, " ")
      .replace(/\b\w/g, (c) => c.toUpperCase());
    document.title = `${chartName} — WealthLens UK`;
  } else {
    document.title = to.meta.title ?? "WealthLens UK";
  }
});

export default router;
