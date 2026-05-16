import { createApp } from "vue";
import { createPinia } from "pinia";
import { createRouter, createWebHistory } from "vue-router";
import App from "./App.vue";
import "./style.css";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "home",
      component: () => import("./views/HomeView.vue"),
    },
    {
      path: "/charts/:name",
      name: "chart",
      component: () => import("./views/ChartView.vue"),
    },
  ],
});

const app = createApp(App);
app.use(createPinia());
app.use(router);
app.mount("#app");
