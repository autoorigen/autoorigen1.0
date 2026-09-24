/* =========================================================
   AUTOORIGEN — pwa.js
   Registra el service worker para que el sitio se pueda instalar como
   app (Safari en iPhone: "Compartir → Agregar a pantalla de inicio";
   Chrome/Android/escritorio: ícono de instalar en la barra de direcciones).
   ========================================================= */
(function () {
  'use strict';
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('/sw.js').catch(function () {
        /* El sitio sigue funcionando igual sin service worker. */
      });
    });
  }
})();
