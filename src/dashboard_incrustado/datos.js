/* Modo incrustado: los datos ya vienen cargados por el servidor (en el bloque JSON de la pagina, id datos-dashboard), asi que el
   navegador no usa ninguna clave ni llama a ninguna red. Entrega lo mismo que entrega api.js (leerDashboard) en el prototipo:
   { datos: <lo que devuelve inventario_dashboard()> } o { error: {...} }, de modo que dashboard.js no nota la diferencia. */
(function () {
  'use strict';
  var datos = null;
  var fallo = null;
  try {
    datos = JSON.parse(document.getElementById('datos-dashboard').textContent);
  } catch (e) {
    fallo = { tipo: 'sistema', mensaje: 'No se pudieron leer los datos del Dashboard. Recarga la página.', campo: '' };
  }
  window.API = {
    leerDashboard: function () { return Promise.resolve(fallo ? { error: fallo } : { datos: datos }); }
  };
})();
