import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from '@/router'
import './style.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')

// Register service worker in production
if (import.meta.env.PROD && 'serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/wealthlens-hq/sw.js')
      .then((reg) => {
        console.log('[SW] Registered:', reg.scope)
      })
      .catch((err) => {
        console.warn('[SW] Registration failed:', err)
      })
  })
}
