var ORDEN_ID_OBSERVACIONES = document.currentScript.getAttribute('data-orden-id');

document.addEventListener('DOMContentLoaded', function () {
  'use strict';
  if (!AOMecanico.exigirSesion()) return;

  var ordenId = ORDEN_ID_OBSERVACIONES;
  var form = document.getElementById('formObservaciones');
  var nota = document.getElementById('observacionesNota');
  var boton = form.querySelector('button[type="submit"]');

  function agregarEvento(tipo, descripcion) {
    return AOMecanico.apiJson('/api/inspecciones/' + ordenId + '/eventos', {
      method: 'POST',
      body: JSON.stringify({ tipo: tipo, descripcion: descripcion }),
    });
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var mecanico = form.observacion_mecanico.value.trim();
    var cliente = form.comentario_cliente.value.trim();

    boton.disabled = true;
    nota.textContent = 'Guardando…';

    var pasos = [];
    if (mecanico) pasos.push(agregarEvento('observacion_mecanico', mecanico));
    if (cliente) pasos.push(agregarEvento('comentario_cliente', cliente));

    Promise.all(pasos)
      .then(function (resultados) {
        var fallo = resultados.find(function (r) { return !r.ok; });
        if (fallo) {
          nota.textContent = (fallo.datos && fallo.datos.error) || 'No se pudo guardar.';
          boton.disabled = false;
          return;
        }
        window.location.href = '/mecanico/';
      })
      .catch(function () {
        nota.textContent = 'No se pudo conectar con el servidor.';
        boton.disabled = false;
      });
  });
});
