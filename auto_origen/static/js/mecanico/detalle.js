var ORDEN_ID_DETALLE = document.currentScript.getAttribute('data-orden-id');

var ETIQUETAS_TIPO_DETALLE = {
  nota: 'Nota', cambio_estado: 'Cambio de etapa', hallazgo: 'Hallazgo',
  foto: 'Foto', video: 'Video', informe: 'Informe',
  observacion_mecanico: 'Observación del mecánico', comentario_cliente: 'Comentario del cliente',
  video_ingreso: 'Video de ingreso',
};

document.addEventListener('DOMContentLoaded', function () {
  'use strict';
  if (!AOMecanico.exigirSesion()) return;

  var ordenId = ORDEN_ID_DETALLE;
  var cargando = document.getElementById('detalleCargando');
  var contenedor = document.getElementById('detalleContenido');

  function lineaSiExiste(etiqueta, valor) {
    return valor ? '<p>' + etiqueta + ': ' + valor + '</p>' : '';
  }

  AOMecanico.apiJson('/api/inspecciones/' + ordenId, { method: 'GET' })
    .then(function (resultado) {
      cargando.hidden = true;
      if (!resultado.ok) {
        contenedor.innerHTML = '<p class="mecanico-vacio">' + ((resultado.datos && resultado.datos.error) || 'No se pudo cargar.') + '</p>';
        return;
      }

      var insp = resultado.datos.inspeccion;
      var ficha = document.createElement('div');
      ficha.className = 'mecanico-ficha';
      ficha.innerHTML =
        '<p><strong>' + insp.vehiculo_placa + ' — ' + (insp.marca || '') + ' ' + (insp.modelo || '') + '</strong></p>' +
        '<p>Cliente: ' + insp.cliente_nombre + ' · ' + insp.cliente_telefono + '</p>' +
        '<p>Etapa: ' + insp.estado_actual + '</p>' +
        lineaSiExiste('Combustible', insp.combustible) +
        lineaSiExiste('Kilometraje', insp.kilometraje) +
        lineaSiExiste('Kilometraje del aceite', insp.kilometraje_aceite) +
        lineaSiExiste('Inspeccionado por', insp.tecnico_nombre);
      contenedor.appendChild(ficha);

      insp.eventos.forEach(function (evento) {
        var div = document.createElement('div');
        div.className = 'mecanico-evento';

        var meta = document.createElement('div');
        meta.className = 'mecanico-item__meta';
        meta.textContent = (ETIQUETAS_TIPO_DETALLE[evento.tipo] || evento.tipo) + ' · ' + (evento.creado_en || '').slice(0, 16).replace('T', ' ');
        div.appendChild(meta);

        var texto = document.createElement('div');
        texto.textContent = evento.titulo + (evento.descripcion ? ' — ' + evento.descripcion : '');
        div.appendChild(texto);

        if (evento.medio_path && evento.tipo === 'foto') {
          var img = document.createElement('img');
          img.className = 'mecanico-evento__foto';
          img.alt = evento.titulo;
          AOMecanico.api('/api/inspecciones/medios/' + evento.medio_path)
            .then(function (r) { return r.blob(); })
            .then(function (blob) { img.src = URL.createObjectURL(blob); })
            .catch(function () { /* si la foto no carga, el resto del detalle sigue visible */ });
          div.appendChild(img);
        } else if (evento.medio_path && (evento.tipo === 'video' || evento.tipo === 'video_ingreso')) {
          var p = document.createElement('p');
          p.className = 'mecanico-item__meta';
          p.textContent = '🎥 Video disponible en el servidor';
          div.appendChild(p);
        }

        contenedor.appendChild(div);
      });
    })
    .catch(function () {
      cargando.hidden = true;
      contenedor.innerHTML = '<p class="mecanico-vacio">No se pudo conectar con el servidor.</p>';
    });
});
