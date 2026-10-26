/* Prototipo navegable: rutas por hash (#/p1 a #/p4), estado en memoria.
   Sin dependencias ni paso de build. */
(function () {
  'use strict';

  var D = window.DATOS;
  var MAX_SKUS = 60;
  var ESPERA_MS = 600;
  var RUTAS = ['p1', 'p2', 'p3', 'p4'];
  var NOMBRE_APP = 'Automatizacion_bodega';
  var vista = document.getElementById('vista');

  var estado = estadoInicial();
  var ultimaRuta = null;

  /* ---------- Utilidades ---------- */

  function esc(texto) {
    return String(texto).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function buscar(lista, campo, valor) {
    for (var i = 0; i < lista.length; i++) {
      if (lista[i][campo] === valor) return lista[i];
    }
    return null;
  }

  function orden(id) { return buscar(D.ordenes, 'id_orden', id); }
  function cliente(id) { return buscar(D.clientes, 'id_cliente', id); }
  function usuario(id) { return buscar(D.usuarios, 'id_usuario', id); }
  function equipo(sku) { return buscar(D.equipos, 'sku', sku); }
  function etiqueta(lista, valor) { var e = buscar(lista, 'valor', valor); return e ? e.etiqueta : valor; }

  function plural(n, uno, varios) { return n + ' ' + (n === 1 ? uno : varios); }

  function dosDigitos(n) { return (n < 10 ? '0' : '') + n; }
  function hhmm(fecha) { return dosDigitos(fecha.getHours()) + ':' + dosDigitos(fecha.getMinutes()); }
  function fechaHora(fecha) {
    return dosDigitos(fecha.getDate()) + '/' + dosDigitos(fecha.getMonth() + 1) + '/' + fecha.getFullYear() + ' ' + hhmm(fecha);
  }

  function opciones(lista, campoValor, campoEtiqueta, seleccionado) {
    return lista.map(function (e) {
      var valor = e[campoValor];
      return '<option value="' + esc(valor) + '"' + (String(valor) === String(seleccionado) ? ' selected' : '') + '>' +
        esc(e[campoEtiqueta]) + '</option>';
    }).join('');
  }

  /* ---------- Estado ---------- */

  function formDeOrden(id) {
    var o = orden(id);
    return { id_orden: id, tipo_movimiento: o.tipo_movimiento, modalidad: o.modalidad, listado: o.skus.join('\n') };
  }

  function estadoInicial() {
    return {
      form: formDeOrden(3001),   // lo que hay escrito en P1
      pedido: null,              // se crea al cargar el pedido
      aviso: null,               // mensaje de una sola vez
      validando: false,
      p3: null,
      guia: null
    };
  }

  /* ---------- Reglas de validación ---------- */

  function parsearListado(texto) {
    var vistos = Object.create(null);
    var skus = [];
    var repetidos = 0;
    texto.split(/\r?\n/).forEach(function (linea) {
      var sku = linea.trim().toUpperCase();
      if (!sku) return;
      if (vistos[sku]) { repetidos++; return; }
      vistos[sku] = true;
      skus.push(sku);
    });
    return { skus: skus, repetidos: repetidos };
  }

  function resultadoSku(sku) {
    var e = equipo(sku);
    if (!e) return 'no_existe';
    if (e.estado !== 'disponible') return 'no_disponible';
    return 'ok';
  }

  function vigentes() { return estado.pedido.lineas.filter(function (l) { return l.vigente; }); }
  function conProblema(l) { return l.resultado === 'no_existe' || l.resultado === 'no_disponible'; }
  function todoOk() {
    if (!estado.pedido) return false;
    var v = vigentes();
    return v.length > 0 && v.every(function (l) { return l.resultado === 'ok'; });
  }

  /* ---------- Navegación ---------- */

  function rutaActual() {
    var h = location.hash.replace(/^#\/?/, '');
    return RUTAS.indexOf(h) >= 0 ? h : 'p1';
  }

  function ir(ruta) {
    if (location.hash === '#/' + ruta) render(true);
    else location.hash = '#/' + ruta;
  }

  function migas(actual) {
    var pasos = [
      ['p1', 'Cargar pedido'],
      ['p2', 'Validar'],
      [actual === 'p3' ? 'p3' : 'p4', actual === 'p3' ? 'Registrar cambio' : 'Guía lista']
    ];
    return '<nav class="migas" aria-label="Dónde estoy"><ol>' + pasos.map(function (p) {
      return '<li' + (p[0] === actual ? ' aria-current="step"' : '') + '>' + esc(p[1]) + '</li>';
    }).join('') + '</ol></nav>';
  }

  function botonCargando(boton, texto) {
    boton.disabled = true;
    boton.classList.add('cargando');
    boton.setAttribute('aria-busy', 'true');
    boton.innerHTML = '<span class="giro" aria-hidden="true"></span><span>' + esc(texto) + '</span>';
  }

  function esperar(fn) { window.setTimeout(fn, ESPERA_MS); }

  /* ---------- Pantallas ---------- */
  var VISTAS = {};

  /* @@VISTA-P1 */

  /* @@VISTA-P2 */

  /* @@VISTA-P3 */

  /* @@VISTA-P4 */

  /* ---------- Render ---------- */

  function render(foco) {
    var ruta = rutaActual();
    if (ruta !== 'p1' && !estado.pedido) { location.replace('#/p1'); return; }
    if (ruta === 'p4' && !todoOk()) { location.replace('#/p2'); return; }

    var v = VISTAS[ruta];
    if (!v) { vista.innerHTML = ''; return; }
    var cambioRuta = ruta !== ultimaRuta;
    ultimaRuta = ruta;

    vista.innerHTML = v.html();
    document.title = v.titulo() + ' · ' + NOMBRE_APP;
    v.enlazar();

    var destino = null;
    if (typeof foco === 'string') destino = document.getElementById(foco);
    else if (cambioRuta || foco === true) destino = document.getElementById('titulo');
    if (destino) destino.focus();
    if (cambioRuta) window.scrollTo(0, 0);
  }

  window.addEventListener('hashchange', function () { render(); });

  document.getElementById('reiniciar').addEventListener('click', function () {
    estado = estadoInicial();
    ultimaRuta = null;
    if (location.hash === '#/p1') render(true);
    else location.hash = '#/p1';
  });

  render();
})();
