/* =========================================================
   AUTOORIGEN — timeline.js
   Línea de tiempo en vivo de "Historia mecánica del vehículo"
   (Socket.IO). Solo se carga cuando hay una orden activa.
   ========================================================= */
(function () {
  'use strict';
  try {
    var lista = document.getElementById('timeline');
    var estadoTexto = document.getElementById('timelineEstado');
    if (!lista || typeof io === 'undefined') return;

    var vehiculoId = lista.getAttribute('data-vehiculo-id');
    var etapas = ['recibido', 'diagnosticando', 'diagnosticado', 'reparando', 'verificando', 'listo'];
    var etiquetasTipo = {
      nota: 'Nota', cambio_estado: 'Cambio de etapa', hallazgo: 'Hallazgo',
      foto: 'Foto', video: 'Video', informe: 'Informe',
      observacion_mecanico: 'Observación del mecánico', comentario_cliente: 'Comentario del cliente'
    };

    var socket = io({ transports: ['websocket', 'polling'] });

    socket.on('connect', function () {
      socket.emit('historial:unirse', { vehiculo_id: vehiculoId });
      if (estadoTexto) estadoTexto.textContent = 'Conectado — verás los cambios en vivo aquí.';
    });

    socket.on('disconnect', function () {
      if (estadoTexto) estadoTexto.textContent = 'Sin conexión en vivo. Recarga la página para ver el estado más reciente.';
    });

    socket.on('timeline:nuevo_evento', function (evento) {
      var vacio = lista.querySelector('li:only-child p');
      if (lista.children.length === 1 && vacio && !lista.children[0].hasAttribute('data-evento-id')) {
        lista.innerHTML = '';
      }

      var item = document.createElement('li');
      item.setAttribute('data-evento-id', evento.id);

      var tag = document.createElement('span');
      tag.className = 'timeline__tag';
      tag.textContent = (etiquetasTipo[evento.tipo] || evento.tipo) + ' · ' + (evento.creado_en || '').slice(0, 16).replace('T', ' ');
      item.appendChild(tag);

      var texto = document.createElement('p');
      var negrita = document.createElement('strong');
      negrita.textContent = evento.titulo;
      texto.appendChild(negrita);
      if (evento.descripcion) texto.appendChild(document.createTextNode(' — ' + evento.descripcion));
      item.appendChild(texto);

      if (evento.medio_path) {
        var mediaP = document.createElement('p');
        mediaP.className = 'timeline__medio';
        mediaP.textContent = evento.tipo === 'video' ? '🎥 Video agregado' : '📷 Foto agregada';
        item.appendChild(mediaP);
      }

      lista.appendChild(item);
      item.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

      if (evento.orden_estado_actual) {
        var pasos = document.querySelectorAll('.progreso__pasos li');
        var actualIdx = etapas.indexOf(evento.orden_estado_actual);
        pasos.forEach(function (paso, i) {
          paso.classList.toggle('is-actual', i === actualIdx);
          paso.classList.toggle('is-hecho', i < actualIdx);
        });
      }
    });
  } catch (e) {
    /* La hoja de vida sigue siendo legible aunque el socket falle. */
  }
})();
