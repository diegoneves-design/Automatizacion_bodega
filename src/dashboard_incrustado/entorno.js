/* Entorno del Dashboard dentro del MVP (iframe de Streamlit). Reemplaza lo que en el prototipo hace la propia pagina:
   - los filtros viajan en la direccion (#estado=fuera_servicio&familia=AC) de la PAGINA PADRE (la de Streamlit), no del iframe;
   - el iframe ocupa el alto de la ventana y el contenido se desplaza dentro (asi el panel lateral, que es fijo, queda a la vista);
   - en pantallas anchas el panel se acopla a un lado en vez de tapar los graficos.
   El iframe tiene el mismo origen que la pagina padre (srcdoc con allow-same-origin), asi que puede leer y escribir su direccion.
   Si por algun motivo no puede (otra version de Streamlit), cae a la direccion del propio iframe y el Dashboard sigue funcionando. */
(function () {
  'use strict';

  var ANCHO_ACOPLADO = 1100;   /* desde este ancho el panel se acopla y no es modal */
  var ALTO_MINIMO = 560;
  var RESTA_ALTO = 96;         /* lo que se resta al alto de la ventana: queda a la vista el borde de la pagina */

  var padre = null;
  try {
    if (window.parent && window.parent !== window && typeof window.parent.location.hash === 'string') padre = window.parent;
  } catch (e) { padre = null; }

  function leerHash() {
    try { return (padre || window).location.hash; } catch (e) { return ''; }
  }

  function guardarHash(h) {
    try {
      var donde = padre || window;
      if (donde.location.hash.replace(/^#/, '') === h) return;
      donde.history.replaceState(null, '', donde.location.pathname + donde.location.search + (h ? '#' + h : ''));
    } catch (e) { /* sin direccion compartible: no pasa nada */ }
  }

  function alCambiarHash(cb) {
    try { (padre || window).addEventListener('hashchange', cb); } catch (e) { /* idem */ }
  }

  function panelAcoplado() { return window.innerWidth >= ANCHO_ACOPLADO; }

  window.DASHBOARD_ENTORNO = { leerHash: leerHash, guardarHash: guardarHash, alCambiarHash: alCambiarHash, panelAcoplado: panelAcoplado };

  function ajustarAlto() {
    try {
      var marco = window.frameElement;
      if (!marco || !padre) return;
      marco.style.height = Math.max(ALTO_MINIMO, padre.innerHeight - RESTA_ALTO) + 'px';
    } catch (e) { /* queda el alto que puso Streamlit */ }
  }

  ajustarAlto();
  try { if (padre) padre.addEventListener('resize', ajustarAlto); } catch (e) { /* idem */ }
})();
