// WealthLens UK — Service Worker
// Cache-first for static assets, network-first for HTML/API
//
// IMPORTANT: Base path '/wealthlens-hq/' is coupled to vite.config.ts `base`.
// If deploying to a custom domain at '/', update all paths below.
// This worker is served from '/wealthlens-hq/sw.js' and is scoped to
// '/wealthlens-hq/'. It cannot intercept root '/api/' requests unless the
// server sends a broader Service-Worker-Allowed header.
// Bump CACHE_NAME on breaking changes to force cache invalidation.

const CACHE_NAME = 'wl-v1'
const OFFLINE_URL = '/wealthlens-hq/offline.html'
const API_OFFLINE_BODY = JSON.stringify({
  error: 'service_unavailable',
  message: 'The WealthLens API is unavailable while offline.',
})

// Static assets to pre-cache on install
const PRECACHE_URLS = [
  OFFLINE_URL,
  '/wealthlens-hq/icons/icon-192.svg',
  '/wealthlens-hq/icons/icon-512.svg',
]

// --- Install: pre-cache offline fallback and icons ---
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE_URLS)),
  )
  self.skipWaiting()
})

// --- Activate: clean up old caches ---
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(
          keys
            .filter((key) => key !== CACHE_NAME)
            .map((key) => caches.delete(key)),
        ),
      ),
  )
  self.clients.claim()
})

// --- Fetch strategy ---
self.addEventListener('fetch', (event) => {
  const { request } = event
  const url = new URL(request.url)
  const isApiRequest = url.pathname.startsWith('/wealthlens-hq/api/')

  // Only handle same-origin requests
  if (url.origin !== self.location.origin) return

  // API requests under the worker scope: network-first, JSON error fallback.
  if (isApiRequest) {
    event.respondWith(
      fetch(request).catch(
        () =>
          new Response(API_OFFLINE_BODY, {
            status: 503,
            statusText: 'Service Unavailable',
            headers: {
              'Content-Type': 'application/json; charset=utf-8',
              'Cache-Control': 'no-store',
            },
          }),
      ),
    )
    return
  }

  // HTML requests: network-first, offline page fallback.
  if (request.mode === 'navigate' || request.destination === 'document') {
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
            .then((cached) => cached || caches.match(OFFLINE_URL)),
        ),
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
          }),
      ),
    )
    return
  }

  // Everything else: network with cache fallback
  event.respondWith(fetch(request).catch(() => caches.match(request)))
})
