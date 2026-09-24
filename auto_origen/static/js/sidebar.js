/* =========================================================
   AUTOORIGEN — sidebar.js
   Abre/cierra el menú lateral (banner + barra lateral de opciones).
   ========================================================= */
(function () {
  'use strict';
  try {
    var toggle = document.getElementById('menuToggle');
    var sidebar = document.getElementById('sidebar');
    var scrim = document.getElementById('sidebarScrim');
    if (!toggle || !sidebar) return;

    function cerrar() {
      sidebar.classList.remove('is-open');
      if (scrim) scrim.hidden = true;
      toggle.setAttribute('aria-expanded', 'false');
      toggle.setAttribute('aria-label', 'Abrir menú');
    }
    function abrir() {
      sidebar.classList.add('is-open');
      if (scrim) scrim.hidden = false;
      toggle.setAttribute('aria-expanded', 'true');
      toggle.setAttribute('aria-label', 'Cerrar menú');
    }

    toggle.addEventListener('click', function () {
      sidebar.classList.contains('is-open') ? cerrar() : abrir();
    });
    if (scrim) scrim.addEventListener('click', cerrar);
    sidebar.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', cerrar);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') cerrar();
    });
  } catch (e) {
    /* El sitio sigue siendo navegable aunque falle este script. */
  }
})();
