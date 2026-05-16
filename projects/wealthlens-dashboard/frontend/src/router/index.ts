import { createRouter, createWebHistory } from "vue-router";

const SITE_TITLE = "WealthLens UK";

const CHART_TITLES: Record<string, string> = {
  "wealth-shares": "Wealth Shares",
  "housing-affordability": "Housing Affordability",
  "wealth-by-decile": "Wealth by Decile",
  "cgt-concentration": "CGT Concentration",
};

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "home",
      component: () => import("@/views/HomeView.vue"),
      meta: { title: "Home" },
    },
    {
      path: "/charts/:name",
      name: "chart",
      component: () => import("@/views/ChartView.vue"),
    },
    {
      path: "/:pathMatch(.*)*",
      name: "not-found",
      component: () => import("@/views/NotFoundView.vue"),
      meta: { title: "Page Not Found" },
    },
  ],
});

router.afterEach((to) => {
  let pageTitle = to.meta.title;
  if (to.name === "chart" && typeof to.params.name === "string") {
    pageTitle = CHART_TITLES[to.params.name] ?? "Chart";
  }
  document.title = pageTitle ? `${pageTitle} — ${SITE_TITLE}` : SITE_TITLE;
});

export default router;
