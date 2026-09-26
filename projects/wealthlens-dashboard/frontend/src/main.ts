import { createApp } from "vue"
import { createPinia } from "pinia"
import App from "./App.vue"
import router from "@/router"
import i18n from "@/i18n"
import { stripPrerenderedMeta } from "@/utils/prerenderedMeta"
import { START_LOCATION } from "vue-router"
import { notePulseboardNavigation, startObservatory } from "@/utils/observatory"
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

// Pulseboard SDK v3 (observatory/README.md): off unless a production build sets
// VITE_PULSEBOARD=on (deploy.yml does); never in the prerender snapshot, embeds or
// frames; one tag, versioned by the locked digest so the service worker cannot pin
// stale bytes. Wherever it does not load, the reserved bar space is released.
startObservatory({
  enabled: import.meta.env.PROD && import.meta.env.VITE_PULSEBOARD === "on",
  base: import.meta.env.BASE_URL,
  version: __WL_OBSERVATORY_VERSION__,
})
// In-app navigations count as page views on the registered `home` route; the SDK
// records the landing page itself. Query or hash changes on the same page are not
// page views. A no-op whenever the SDK is absent.
router.afterEach((to, from, failure) => {
  if (failure || to.meta.embed || to.path === from.path) return
  notePulseboardNavigation(from === START_LOCATION)
})
