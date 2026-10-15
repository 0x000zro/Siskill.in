const CACHE_NAME = "siskill-pwa-v3";
const STATIC_ASSETS = [
  "./",
  "./index.html",
  "./style.css",
  "./app.js",
  "./script.js",
  "./icon.svg",
  "./manifest.webmanifest",
  "./dist_assets/master_catalog.json"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log("[SW v3] Pre-caching App Shell & Master Catalog");
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) return caches.delete(key);
        })
      )
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const reqUrl = event.request.url;

  // Strategy 1: Network-First with Offline Cache Fallback for JSON data bundles
  // (Ensures newly synced questions appear immediately when online, yet works 100% offline)
  if (reqUrl.includes("dist_assets/") && reqUrl.endsWith(".json")) {
    event.respondWith(
      fetch(event.request)
        .then((networkRes) => {
          if (networkRes && networkRes.status === 200) {
            const copy = networkRes.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
          }
          return networkRes;
        })
        .catch(() => caches.match(event.request))
    );
    return;
  }

  // Strategy 2: Cache-First with Network Fallback for UI Shell & Fonts
  event.respondWith(
    caches.match(event.request).then((cachedRes) => {
      if (cachedRes) return cachedRes;
      return fetch(event.request)
        .then((networkRes) => {
          if (networkRes && networkRes.status === 200 && event.request.method === "GET") {
            const copy = networkRes.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
          }
          return networkRes;
        })
        .catch(() => caches.match("./index.html"));
    })
  );
});
