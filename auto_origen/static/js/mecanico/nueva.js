document.addEventListener('DOMContentLoaded', function () {
  'use strict';
  if (!AOMecanico.exigirSesion()) return;

  var form = document.getElementById('formNueva');
  var nota = document.getElementById('nuevaNota');
  var boton = form.querySelector('button[type="submit"]');
  var combustible = null;

  document.querySelectorAll('.chip-combustible').forEach(function (chip) {
    chip.addEventListener('click', function () {
      document.querySelectorAll('.chip-combustible').forEach(function (c) { c.classList.remove('is-activo'); });
      chip.classList.add('is-activo');
      combustible = chip.getAttribute('data-valor');
    });
  });

  form.addEventListener('submit', function (e) {
    e.preventDefault();

    var datos = {
      placa: form.placa.value.trim().toUpperCase(),
      cliente_nombre: form.cliente_nombre.value.trim(),
      cliente_telefono: form.cliente_telefono.value.trim(),
      marca: form.marca.value.trim() || null,
      modelo: form.modelo.value.trim() || null,
      combustible: combustible,
      kilometraje: form.kilometraje.value.trim() || null,
      kilometraje_aceite: form.kilometraje_aceite.value.trim() || null,
    };

    if (!datos.placa || !datos.cliente_nombre || !datos.cliente_telefono) {
      nota.textContent = 'Placa, nombre del cliente y teléfono son obligatorios.';
      return;
    }

    boton.disabled = true;
    nota.textContent = 'Guardando…';

    AOMecanico.apiJson('/api/inspecciones', { method: 'POST', body: JSON.stringify(datos) })
      .then(function (resultado) {
        if (resultado.ok) {
          window.alert(
            'Código de acceso para ' + datos.placa + ': ' + resultado.datos.codigo_acceso +
            '\n\nEntrégaselo al cliente ahora (de palabra, por WhatsApp o en el recibo) — ' +
            'lo va a necesitar junto con la placa para ver el estado de su carro en la web.'
          );
          window.location.href = '/mecanico/captura/' + resultado.datos.orden_id;
        } else {
          nota.textContent = (resultado.datos && resultado.datos.error) || 'No se pudo crear el registro.';
          boton.disabled = false;
        }
      })
      .catch(function () {
        nota.textContent = 'No se pudo conectar con el servidor.';
        boton.disabled = false;
      });
  });
});
