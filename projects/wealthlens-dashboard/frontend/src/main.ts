import { createApp } from "vue"
import { createPinia } from "pinia"
import App from "./App.vue"
import router from "@/router"
import i18n from "@/i18n"
import { stripPrerenderedMeta } from "@/utils/prerenderedMeta"
import { START_LOCATION } from "vue-router"
import { notePulseboardNavigation, startObservatory } from "@/utils/observatory"
import "./style.css"

const app = createApp(App)
app.use(createPinia())
app.use(i18n)
app.use(router)
// createApp replaces the baked DOM rather than hydrating it (ADR 0001).
// Keep that readable snapshot, including its metadata, until the initial lazy
// route resolves; mounting earlier briefly renders an empty RouterView and
// pulls the footer up before the page arrives.
function mountApp(): void {
  stripPrerenderedMeta()
  app.mount("#app")

  // Run after mount: releasing the reservation on a baked node would be lost
  // when createApp replaces it. The SDK must see the live bar container too.
  // Pulseboard is production-only and opt-in; never in snapshots or embeds.
  startObservatory({
    enabled: import.meta.env.PROD && import.meta.env.VITE_PULSEBOARD === "on",
    base: import.meta.env.BASE_URL,
    version: __WL_OBSERVATORY_VERSION__,
  })
}

router
  .isReady()
  .then(mountApp)
  .catch((error) => {
    // A failed lazy import must not erase the readable prerendered fallback.
    console.error("[App] Initial route failed:", error)
    const container = document.getElementById("app")
    if (container && container.childElementCount === 0 && !container.textContent?.trim()) {
      // Dev/non-prerendered entries have no readable fallback. Keep the site
      // navigation usable, so another route can recover from a failed import.
      mountApp()
      return
    }
    // A later successful navigation (including browser Back/Forward) can
    // still take over a preserved snapshot after the initial promise rejected.
    const stop = router.afterEach((_to, _from, failure) => {
      if (failure) return
      stop()
      mountApp()
    })
  })

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

// In-app navigations count as page views on the registered `home` route; the SDK
// records the landing page itself. Query or hash changes on the same page are not
// page views. A no-op whenever the SDK is absent.
router.afterEach((to, from, failure) => {
  if (failure || to.meta.embed || to.path === from.path) return
  notePulseboardNavigation(from === START_LOCATION)
})
