document.addEventListener('DOMContentLoaded', function () {
  'use strict';
  if (!AOMecanico.exigirSesion()) return;

  var lista = document.getElementById('listaHistorial');
  var cargando = document.getElementById('historialCargando');

  AOMecanico.apiJson('/api/inspecciones', { method: 'GET' })
    .then(function (resultado) {
      cargando.hidden = true;
      if (!resultado.ok) {
        lista.innerHTML = '<p class="mecanico-vacio">' + ((resultado.datos && resultado.datos.error) || 'No se pudo cargar.') + '</p>';
        return;
      }
      var inspecciones = resultado.datos.inspecciones || [];
      if (inspecciones.length === 0) {
        lista.innerHTML = '<p class="mecanico-vacio">Todavía no hay inspecciones registradas.</p>';
        return;
      }
      inspecciones.forEach(function (insp) {
        var a = document.createElement('a');
        a.className = 'mecanico-item';
        a.href = '/mecanico/detalle/' + insp.id;
        var titulo = document.createElement('div');
        titulo.className = 'mecanico-item__titulo';
        titulo.textContent = insp.vehiculo_placa + ' — ' + (insp.marca || '') + ' ' + (insp.modelo || '');
        var meta = document.createElement('div');
        meta.className = 'mecanico-item__meta';
        meta.textContent = insp.cliente_nombre + ' · Etapa: ' + insp.estado_actual;
        a.appendChild(titulo);
        a.appendChild(meta);
        lista.appendChild(a);
      });
    })
    .catch(function () {
      cargando.hidden = true;
      lista.innerHTML = '<p class="mecanico-vacio">No se pudo conectar con el servidor.</p>';
    });
});
