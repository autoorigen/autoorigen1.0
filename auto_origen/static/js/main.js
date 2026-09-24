/* =========================================================
   AUTOORIGEN — main.js (V1.2)
   1. Preloader        3. Animaciones al hacer scroll
   2. Header al bajar  4. Formulario de contacto → Flask
   (El menú lateral vive en sidebar.js)
   ========================================================= */
(function () {
  'use strict';
  try {
    var reduceMotion = window.matchMedia &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    /* ---------- 1. Preloader ---------- */
    var preloader = document.getElementById('preloader');
    function hidePreloader() {
      if (!preloader) return;
      var el = preloader;
      preloader = null;
      el.classList.add('is-hidden');
      setTimeout(function () { el.remove(); }, 700);
    }
    if (reduceMotion) {
      hidePreloader();
    } else {
      window.addEventListener('load', function () { setTimeout(hidePreloader, 500); });
      setTimeout(hidePreloader, 2500); // por si las fuentes tardan en cargar
    }

    /* ---------- 2. Header al bajar ---------- */
    var header = document.getElementById('siteHeader');
    function onScroll() {
      if (!header) return;
      header.classList.toggle('is-scrolled', window.scrollY > 40);
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();

    /* ---------- 3. Animaciones al hacer scroll ---------- */
    var revealEls = document.querySelectorAll('[data-reveal]');
    if (reduceMotion || !('IntersectionObserver' in window)) {
      revealEls.forEach(function (el) { el.classList.add('is-visible'); });
    } else {
      // Los textos del hero aparecen de una vez al cargar
      document.querySelectorAll('.hero [data-reveal]').forEach(function (el) {
        el.classList.add('is-visible');
      });
      // El resto se marca cuando entra en pantalla
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.15, rootMargin: '0px 0px -60px 0px' });
      revealEls.forEach(function (el) {
        if (!el.classList.contains('is-visible')) observer.observe(el);
      });
    }

    /* ---------- 4. Formulario de contacto → Flask (/api/contacto) ---------- */
    var form = document.getElementById('contactForm');
    var formNote = document.getElementById('formNote');
    if (form) {
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        if (!form.checkValidity()) {
          if (formNote) formNote.textContent = 'Revisa los campos obligatorios antes de enviar.';
          return;
        }

        var submitBtn = form.querySelector('button[type="submit"]');
        var payload = {};
        new FormData(form).forEach(function (value, key) { payload[key] = value; });

        if (submitBtn) submitBtn.disabled = true;
        if (formNote) formNote.textContent = 'Enviando...';

        var csrfMeta = document.querySelector('meta[name="csrf-token"]');

        fetch('/api/contacto', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfMeta ? csrfMeta.content : ''
          },
          body: JSON.stringify(payload)
        })
          .then(function (res) {
            return res.json().then(function (data) { return { ok: res.ok, data: data }; });
          })
          .then(function (result) {
            if (result.ok && result.data.ok) {
              if (formNote) formNote.textContent = result.data.message;
              form.reset();
            } else {
              if (formNote) formNote.textContent = result.data.error || 'No se pudo enviar el mensaje.';
            }
          })
          .catch(function () {
            if (formNote) formNote.textContent = 'Error de conexión. Intenta de nuevo o escríbenos por WhatsApp.';
          })
          .finally(function () {
            if (submitBtn) submitBtn.disabled = false;
          });
      });
    }
  } catch (e) {
    /* La página sigue siendo completamente navegable aunque falle JS. */
  }
})();
