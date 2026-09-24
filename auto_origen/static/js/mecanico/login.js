document.addEventListener('DOMContentLoaded', function () {
  'use strict';

  if (AOMecanico.token()) {
    window.location.href = '/mecanico/';
    return;
  }

  var form = document.getElementById('formLogin');
  var nota = document.getElementById('loginNota');
  var boton = form.querySelector('button[type="submit"]');

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var usuario = form.usuario.value.trim();
    var password = form.password.value;
    if (!usuario || !password) {
      nota.textContent = 'Completa usuario y contraseña.';
      return;
    }

    boton.disabled = true;
    nota.textContent = 'Entrando…';

    fetch('/api/tecnicos/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ usuario: usuario, password: password }),
    })
      .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, datos: d }; }); })
      .then(function (resultado) {
        if (resultado.ok && resultado.datos.ok) {
          AOMecanico.guardarSesion(resultado.datos.token, resultado.datos.tecnico.nombre);
          window.location.href = '/mecanico/';
        } else {
          nota.textContent = (resultado.datos && resultado.datos.error) || 'Usuario o contraseña incorrectos.';
          boton.disabled = false;
        }
      })
      .catch(function () {
        nota.textContent = 'No se pudo conectar con el servidor.';
        boton.disabled = false;
      });
  });
});
