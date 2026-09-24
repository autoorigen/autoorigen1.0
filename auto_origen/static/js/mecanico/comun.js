/* =========================================================
   AUTOORIGEN — mecanico/comun.js
   Sesión del mecánico (token en localStorage) + helper de fetch con el
   header Authorization ya puesto. Todas las pantallas de /mecanico/*
   usan esto para hablar con la misma API que usa la app Android.
   ========================================================= */
window.AOMecanico = (function () {
  'use strict';

  var CLAVE_TOKEN = 'ao_mecanico_token';
  var CLAVE_NOMBRE = 'ao_mecanico_nombre';

  function token() { return localStorage.getItem(CLAVE_TOKEN); }
  function nombre() { return localStorage.getItem(CLAVE_NOMBRE); }

  function guardarSesion(t, n) {
    localStorage.setItem(CLAVE_TOKEN, t);
    localStorage.setItem(CLAVE_NOMBRE, n);
  }

  function cerrarSesion() {
    localStorage.removeItem(CLAVE_TOKEN);
    localStorage.removeItem(CLAVE_NOMBRE);
    window.location.href = '/mecanico/login';
  }

  function exigirSesion() {
    if (!token()) {
      window.location.href = '/mecanico/login';
      return false;
    }
    return true;
  }

  function api(ruta, opciones) {
    opciones = opciones || {};
    var cabeceras = Object.assign({}, opciones.headers || {}, { Authorization: 'Bearer ' + token() });
    return fetch(ruta, Object.assign({}, opciones, { headers: cabeceras })).then(function (respuesta) {
      if (respuesta.status === 401) {
        cerrarSesion();
        throw new Error('Sesión expirada');
      }
      return respuesta;
    });
  }

  function apiJson(ruta, opciones) {
    opciones = opciones || {};
    var cabeceras = Object.assign({ 'Content-Type': 'application/json' }, opciones.headers || {});
    return api(ruta, Object.assign({}, opciones, { headers: cabeceras })).then(function (respuesta) {
      return respuesta.json().then(function (datos) {
        return { ok: respuesta.ok && datos.ok, datos: datos };
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    var nombreEl = document.getElementById('mecanicoNombre');
    var salirEl = document.getElementById('mecanicoSalir');
    if (nombre() && nombreEl) nombreEl.textContent = nombre();
    if (token() && salirEl) {
      salirEl.hidden = false;
      salirEl.addEventListener('click', cerrarSesion);
    }
  });

  return { token: token, nombre: nombre, guardarSesion: guardarSesion, cerrarSesion: cerrarSesion, exigirSesion: exigirSesion, api: api, apiJson: apiJson };
})();
