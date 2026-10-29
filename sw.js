/**
 * News Colossal — Offline News Vault Service Worker (sw.js)
 * Architecture: Zero external dependencies, pure vanilla ES6
 * Dual Caching: Network-First for dynamic news feeds; Stale-While-Revalidate for app shell
 */

const CACHE_NAME = 'news-colossal-vault-v1';

const STATIC_ASSETS = [
  './',
  './index.html',
  './style.css',
  './app.js',
  './manifest.json',
  './data/news.json',
  './data/podcasts.json',
  './assets/map.svg',
  './assets/icon-192.svg',
  './assets/icon-512.svg',
  './assets/icon-192.png',
  './assets/icon-512.png'
];

// Resilient Installation: Pre-cache static assets with per-asset failure isolation
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        return Promise.all(
          STATIC_ASSETS.map((asset) => {
            return cache.add(asset).catch((err) => {
              console.warn('[Offline Vault] Non-fatal precache skip for asset:', asset, err);
            });
          })
        );
      })
      .then(() => self.skipWaiting())
  );
});

// Activation: Clean up stale caches and claim immediate client control
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch Dispatcher: Dual Caching Strategy
self.addEventListener('fetch', (event) => {
  // Only intercept GET requests
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);

  // Ignore cross-origin non-HTTP schemes (e.g., chrome-extension)
  if (!url.protocol.startsWith('http')) return;

  // Strategy A: Dynamic News Feeds (Network-First with Cache Fallback)
  if (url.pathname.includes('/data/news.json') || url.pathname.includes('/data/podcasts.json') || url.pathname.includes('/data/narrative_memory.json')) {
    event.respondWith(
      fetch(event.request)
        .then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const responseClone = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, responseClone);
            });
          }
          return networkResponse;
        })
        .catch(() => {
          return caches.match(event.request).then((cachedResponse) => {
            if (cachedResponse) {
              return cachedResponse;
            }
            // Synthetic fallback if neither network nor cache is available
            const fallbackData = {
              articles: [],
              offline: true,
              message: 'Offline News Vault: Cached dispatch temporarily unavailable.',
              timestamp: new Date().toISOString()
            };
            return new Response(JSON.stringify(fallbackData), {
              status: 200,
              headers: { 'Content-Type': 'application/json' }
            });
          });
        })
    );
    return;
  }

  // Strategy B: App Shell & Static Assets (Stale-While-Revalidate)
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      const fetchPromise = fetch(event.request)
        .then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const responseClone = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, responseClone);
            });
          }
          return networkResponse;
        })
        .catch((fetchErr) => {
          // If offline and request is HTML navigation, fallback to index.html
          if (event.request.mode === 'navigate') {
            return caches.match('./index.html') || caches.match('./');
          }
          return null;
        });

      // Return cached version immediately if available, while fetching update in background
      return cachedResponse || fetchPromise;
    })
  );
});
