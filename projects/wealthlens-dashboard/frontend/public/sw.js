// WealthLens UK — Service Worker
// Cache-first for static assets, network-first for HTML/API
//
// IMPORTANT: Base path '/wealthlens-hq/' is coupled to vite.config.ts `base`.
// If deploying to a custom domain at '/', update all paths below.
// Bump CACHE_NAME on breaking changes to force cache invalidation.

const CACHE_NAME = 'wl-v1'
const OFFLINE_URL = '/wealthlens-hq/offline.html'

// Static assets to pre-cache on install
const PRECACHE_URLS = [
  OFFLINE_URL,
  '/wealthlens-hq/icons/icon-192.svg',
  '/wealthlens-hq/icons/icon-512.svg',
]

// --- Install: pre-cache offline fallback and icons ---
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE_URLS))
  )
  self.skipWaiting()
})

// --- Activate: clean up old caches ---
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => key !== CACHE_NAME)
          .map((key) => caches.delete(key))
      )
    )
  )
  self.clients.claim()
})

// --- Fetch strategy ---
self.addEventListener('fetch', (event) => {
  const { request } = event
  const url = new URL(request.url)

  // Only handle same-origin requests
  if (url.origin !== self.location.origin) return

  // HTML and API requests: network-first
  if (
    request.mode === 'navigate' ||
    request.destination === 'document' ||
    url.pathname.startsWith('/wealthlens-hq/api/')
  ) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // Cache successful HTML responses
          if (response.ok && request.destination === 'document') {
            const clone = response.clone()
            caches.open(CACHE_NAME).then((cache) => cache.put(request, clone))
          }
          return response
        })
        .catch(() =>
          caches
            .match(request)
            .then((cached) => cached || caches.match(OFFLINE_URL))
        )
    )
    return
  }

  // Static assets (CSS, JS, fonts, images): cache-first
  if (
    request.destination === 'style' ||
    request.destination === 'script' ||
    request.destination === 'font' ||
    request.destination === 'image'
  ) {
    event.respondWith(
      caches.match(request).then(
        (cached) =>
          cached ||
          fetch(request).then((response) => {
            if (response.ok) {
              const clone = response.clone()
              caches.open(CACHE_NAME).then((cache) => cache.put(request, clone))
            }
            return response
          })
      )
    )
    return
  }

  // Everything else: network with cache fallback
  event.respondWith(
    fetch(request).catch(() => caches.match(request))
  )
})
