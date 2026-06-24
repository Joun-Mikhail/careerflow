/* CareerFlow service worker — conservative caching strategy.
 *
 * Goals:
 *   1. Never cache anything from /api/* — user data must not be readable from
 *      a stale cache or after logout.
 *   2. Navigation (the app shell HTML) is network-first; we fall back to a
 *      cached shell only when the network is unreachable, so deploys roll out
 *      immediately and visitors never get stuck on an old version.
 *   3. Static, hash-named build assets under /assets/ are cache-first
 *      (immutable) — they're long-lived and safe to keep.
 *   4. Other static GETs (icons, manifest, favicon, /install) are
 *      stale-while-revalidate.
 */
const VERSION = 'v2';
const SHELL_CACHE = `careerflow-shell-${VERSION}`;
const STATIC_CACHE = `careerflow-static-${VERSION}`;
const SHELL_ASSETS = ['/', '/manifest.json', '/favicon.svg'];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(SHELL_CACHE).then((cache) => cache.addAll(SHELL_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    (async () => {
      const keys = await caches.keys();
      await Promise.all(
        keys
          .filter((k) => k !== SHELL_CACHE && k !== STATIC_CACHE)
          .map((k) => caches.delete(k))
      );
      await self.clients.claim();
    })()
  );
});

function isApiRequest(url) {
  return (
    url.pathname.startsWith('/api/') ||
    url.pathname === '/health' ||
    url.pathname === '/openapi.json'
  );
}

function isImmutableAsset(url) {
  return url.pathname.startsWith('/assets/');
}

async function networkFirst(request, cacheName, fallback) {
  try {
    const fresh = await fetch(request);
    if (fresh.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, fresh.clone()).catch(() => {});
    }
    return fresh;
  } catch (err) {
    const cached = await caches.match(request);
    if (cached) return cached;
    if (fallback) {
      const fallbackHit = await caches.match(fallback);
      if (fallbackHit) return fallbackHit;
    }
    throw err;
  }
}

async function cacheFirst(request, cacheName) {
  const cached = await caches.match(request);
  if (cached) return cached;
  const fresh = await fetch(request);
  if (fresh.ok) {
    const cache = await caches.open(cacheName);
    cache.put(request, fresh.clone()).catch(() => {});
  }
  return fresh;
}

async function staleWhileRevalidate(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(request);
  const network = fetch(request)
    .then((response) => {
      if (response.ok) cache.put(request, response.clone()).catch(() => {});
      return response;
    })
    .catch(() => cached);
  return cached || network;
}

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') return;

  let url;
  try {
    url = new URL(request.url);
  } catch {
    return;
  }
  if (url.origin !== self.location.origin) return;

  // Never cache API traffic.
  if (isApiRequest(url)) return;

  if (request.mode === 'navigate') {
    event.respondWith(networkFirst(request, SHELL_CACHE, '/'));
    return;
  }

  if (isImmutableAsset(url)) {
    event.respondWith(cacheFirst(request, STATIC_CACHE));
    return;
  }

  event.respondWith(staleWhileRevalidate(request, STATIC_CACHE));
});

// Wipe everything when the app posts a logout signal. Belt-and-braces in case
// the bundle ever caches a static page that exposes user-scoped state.
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'CAREERFLOW_LOGOUT') {
    event.waitUntil(
      (async () => {
        const keys = await caches.keys();
        await Promise.all(keys.map((k) => caches.delete(k)));
      })()
    );
  }
});
