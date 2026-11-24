/* Portal: decide si el botón está desactivado («Aplicación en despliegue») o es un enlace a la aplicación («Abrir la aplicación»).
   Lee la dirección de config.js (window.PORTAL_CONFIG.URL_APLICACION). Sin dependencias, sin red, sin claves. */
(function () {
  'use strict';

  /* Solo https, sin usuario ni contraseña. Devuelve la dirección normalizada o '' si no sirve. */
  function direccionValida(texto) {
    if (typeof texto !== 'string' || !texto.trim()) return '';
    try {
      var u = new URL(texto.trim());
      if (u.protocol !== 'https:' || u.username || u.password || !u.hostname) return '';
      return u.href;
    } catch (e) {
      return '';
    }
  }

  var config = window.PORTAL_CONFIG || {};
  var destino = direccionValida(config.URL_APLICACION);

  var pendiente = document.getElementById('abrir-pendiente');
  var enlace = document.getElementById('abrir');
  var nota = document.getElementById('nota');
  if (!pendiente || !enlace || !nota) return;

  if (!destino) {
    /* Queda lo que ya trae el HTML: botón desactivado y aviso. */
    pendiente.hidden = false;
    enlace.hidden = true;
    return;
  }

  enlace.setAttribute('href', destino);
  enlace.hidden = false;
  pendiente.hidden = true;
  nota.hidden = true;
})();
