self.addEventListener("install", function(event) {
  event.waitUntil(
    caches.open("jarvas-cache").then(function(cache) {
      return cache.addAll([
        "/",
        "/manifest.json"
      ]);
    })
  );
});

self.addEventListener("fetch", function(event) {
  event.respondWith(
    caches.match(event.request).then(function(response) {
      return response || fetch(event.request);
    })
  );
});