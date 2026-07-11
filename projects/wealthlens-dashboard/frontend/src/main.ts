import { createApp } from "vue"
import { createPinia } from "pinia"
import App from "./App.vue"
import router from "@/router"
import i18n from "@/i18n"
import { stripPrerenderedMeta } from "@/utils/prerenderedMeta"
import "./style.css"

// Prerendered pages (ADR 0001) ship with baked [data-wl-meta] head tags for
// crawlers; drop them before mount so the mounting view's usePageMeta call
// recreates exactly one live copy.
stripPrerenderedMeta()

const app = createApp(App)
app.use(createPinia())
app.use(i18n)
app.use(router)
app.mount("#app")

// Register service worker in production
if (import.meta.env.PROD && "serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register("/wealthlens-hq/sw.js", { scope: "/wealthlens-hq/" })
      .then((reg) => {
        console.log("[SW] Registered:", reg.scope)
      })
      .catch((err) => {
        console.warn("[SW] Registration failed:", err)
      })
  })
}
