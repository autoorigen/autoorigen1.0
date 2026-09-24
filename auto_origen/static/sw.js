/* =========================================================
   AUTOORIGEN — Service worker de la PWA
   Solo cachea archivos estáticos conocidos. Todo lo demás (HTML, /api,
   /historial, /admin, WebSocket...) siempre va a la red: esas páginas
   llevan sesión, CSRF y datos en vivo que no se pueden servir cacheados.
   ========================================================= */
const CACHE = 'autoorigen-estaticos-v2';
const ARCHIVOS_ESTATICOS = [
  '/static/css/style.css',
  '/static/css/mecanico.css',
  '/static/js/main.js',
  '/static/js/sidebar.js',
  '/static/js/pwa.js',
  '/static/js/mecanico/comun.js',
];

self.addEventListener('install', (evento) => {
  evento.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(ARCHIVOS_ESTATICOS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (evento) => {
  evento.waitUntil(
    caches.keys().then((claves) =>
      Promise.all(claves.filter((c) => c !== CACHE).map((c) => caches.delete(c)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (evento) => {
  const url = new URL(evento.request.url);
  if (evento.request.method !== 'GET' || !ARCHIVOS_ESTATICOS.includes(url.pathname)) {
    return; // deja pasar a la red sin tocar nada
  }
  evento.respondWith(
    caches.match(evento.request).then((respuestaCache) => respuestaCache || fetch(evento.request))
  );
});
