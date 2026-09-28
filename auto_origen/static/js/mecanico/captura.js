// document.currentScript solo es válido mientras este archivo se ejecuta por
// primera vez (no dentro de DOMContentLoaded), así que el orden_id se guarda
// aquí arriba y se usa después mediante el cierre (closure).
var ORDEN_ID_CAPTURA = document.currentScript.getAttribute('data-orden-id');

document.addEventListener('DOMContentLoaded', function () {
  'use strict';
  if (!AOMecanico.exigirSesion()) return;

  var ordenId = ORDEN_ID_CAPTURA;
  var lista = document.getElementById('listaCapturas');

  function subir(input, titulo, esVideoIngreso) {
    var archivo = input.files[0];
    if (!archivo) return;

    var item = document.createElement('div');
    item.className = 'mecanico-item';
    item.textContent = titulo + ' — subiendo…';
    lista.prepend(item);

    var formData = new FormData();
    formData.append('archivo', archivo);
    formData.append('titulo', titulo);
    if (esVideoIngreso) formData.append('es_video_ingreso', '1');

    AOMecanico.api('/api/inspecciones/' + ordenId + '/medios', { method: 'POST', body: formData })
      .then(function (r) { return r.json(); })
      .then(function (datos) {
        item.textContent = titulo + (datos.ok ? ' — subido ✓' : ' — error: ' + datos.error);
      })
      .catch(function () {
        item.textContent = titulo + ' — error de conexión';
      });

    input.value = '';
  }

  document.getElementById('inputPlaca').addEventListener('change', function () { subir(this, 'Foto de la placa'); });
  document.getElementById('inputIngreso').addEventListener('change', function () { subir(this, 'Video de ingreso del vehículo', true); });
  document.getElementById('inputFoto').addEventListener('change', function () { subir(this, 'Foto de la inspección'); });
  document.getElementById('inputVideo').addEventListener('change', function () { subir(this, 'Video de la inspección'); });

  document.getElementById('btnContinuar').addEventListener('click', function () {
    window.location.href = '/mecanico/observaciones/' + ordenId;
  });
});
