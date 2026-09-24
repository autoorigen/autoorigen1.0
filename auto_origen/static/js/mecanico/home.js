document.addEventListener('DOMContentLoaded', function () {
  'use strict';
  if (!AOMecanico.exigirSesion()) return;

  document.getElementById('btnNueva').addEventListener('click', function () {
    window.location.href = '/mecanico/nueva';
  });
  document.getElementById('btnHistorial').addEventListener('click', function () {
    window.location.href = '/mecanico/historial';
  });
});
