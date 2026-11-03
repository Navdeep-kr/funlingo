// FunLingo Network-First PWA Service Worker v7
const CACHE_NAME = 'funlingo-pwa-v7';
const ASSETS = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icon-192.svg',
  './icon-512.svg'
];

self.addEventListener('install', (evt) => {
  self.skipWaiting();
  evt.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS);
    })
  );
});

self.addEventListener('activate', (evt) => {
  evt.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((k) => {
          if (k !== CACHE_NAME) {
            console.log('[SW] Deleting old cache:', k);
            return caches.delete(k);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (evt) => {
  if (evt.request.method !== 'GET') return;

  // For HTML navigation: Network-First (always fresh, offline fallback)
  if (evt.request.mode === 'navigate' || evt.request.destination === 'document') {
    evt.respondWith(
      fetch(evt.request).then((res) => {
        if (res && res.status === 200) {
          const clone = res.clone();
          caches.open(CACHE_NAME).then((c) => c.put(evt.request, clone));
        }
        return res;
      }).catch(() => caches.match(evt.request) || caches.match('./index.html'))
    );
    return;
  }

  // For assets: Network-First with cache fallback
  evt.respondWith(
    fetch(evt.request).then((res) => {
      if (res && res.status === 200) {
        const clone = res.clone();
        caches.open(CACHE_NAME).then((c) => c.put(evt.request, clone));
      }
      return res;
    }).catch(() => caches.match(evt.request))
  );
});
