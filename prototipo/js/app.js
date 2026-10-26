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

  /* ----- P1 Cargar pedido (HU-02) ----- */

  function textoContador(p) {
    var n = p.skus.length;
    var t = plural(n, 'producto detectado', 'productos detectados') + ' · máximo ' + MAX_SKUS;
    if (p.repetidos) t += ' · ' + plural(p.repetidos, 'repetido ignorado', 'repetidos ignorados');
    return t;
  }

  function errorListado(p) {
    var n = p.skus.length;
    if (n === 0) return 'Pega al menos un SKU, uno por línea. Ejemplo: SD-63A20-0314';
    if (n > MAX_SKUS) return 'Hay ' + n + ' productos y el máximo es ' + MAX_SKUS + '. Quita ' + (n - MAX_SKUS) + ' para continuar.';
    return '';
  }

  VISTAS.p1 = {
    titulo: function () { return 'Cargar pedido'; },

    html: function () {
      var f = estado.form;
      var o = orden(f.id_orden);
      var aviso = estado.aviso;
      estado.aviso = null;
      var p = parsearListado(f.listado);
      var ordenes = D.ordenes.map(function (x) {
        return { valor: x.id_orden, etiqueta: x.id_orden + ' · ' + cliente(x.id_cliente).razon_social };
      });

      return migas('p1') +
        '<h1 id="titulo" tabindex="-1">Cargar pedido</h1>' +
        '<p class="ayuda-pantalla">Datos de ejemplo: edita el listado para probar un error.</p>' +
        '<div class="aviso" id="aviso" tabindex="-1" role="status" aria-live="polite">' + esc(aviso || '') + '</div>' +
        '<form id="form-carga" novalidate>' +
          '<div class="campo"><label for="orden">Orden</label>' +
            '<select id="orden">' + opciones(ordenes, 'valor', 'etiqueta', f.id_orden) + '</select></div>' +
          '<div class="campo"><label for="cliente">Cliente</label>' +
            '<input id="cliente" type="text" readonly value="' + esc(cliente(o.id_cliente).razon_social) + '"></div>' +
          '<div class="fila-2">' +
            '<div class="campo"><label for="tipo">Tipo de movimiento</label>' +
              '<select id="tipo">' + opciones(D.tipos_movimiento, 'valor', 'etiqueta', f.tipo_movimiento) + '</select></div>' +
            '<div class="campo"><label for="modalidad">Modalidad</label>' +
              '<select id="modalidad">' + opciones(D.modalidades, 'valor', 'etiqueta', f.modalidad) + '</select></div>' +
          '</div>' +
          '<div class="campo"><label for="skus">Productos del pedido, uno por línea</label>' +
            '<textarea id="skus" rows="7" spellcheck="false" autocapitalize="characters" autocomplete="off" aria-describedby="skus-ayuda skus-error">' +
              esc(f.listado) + '</textarea>' +
            '<p class="ayuda' + (p.skus.length > MAX_SKUS ? ' es-alerta' : '') + '" id="skus-ayuda" aria-live="polite">' + esc(textoContador(p)) + '</p>' +
            '<p class="error" id="skus-error" role="alert"></p></div>' +
          '<div class="acciones">' +
            '<button type="submit" class="boton boton-primario" id="cargar">Cargar pedido →</button>' +
            '<button type="button" class="boton boton-secundario" id="cancelar">Cancelar</button>' +
          '</div>' +
        '</form>';
    },

    enlazar: function () {
      var f = estado.form;
      var selOrden = document.getElementById('orden');
      var selTipo = document.getElementById('tipo');
      var selModalidad = document.getElementById('modalidad');
      var area = document.getElementById('skus');
      var ayuda = document.getElementById('skus-ayuda');
      var error = document.getElementById('skus-error');

      function mostrarError(msg) {
        error.textContent = msg ? '✕ ' + msg : '';
        if (msg) area.setAttribute('aria-invalid', 'true'); else area.removeAttribute('aria-invalid');
      }

      selOrden.addEventListener('change', function () {
        estado.form = formDeOrden(Number(selOrden.value));
        render('orden');
      });
      selTipo.addEventListener('change', function () { f.tipo_movimiento = selTipo.value; });
      selModalidad.addEventListener('change', function () { f.modalidad = selModalidad.value; });

      area.addEventListener('input', function () {
        f.listado = area.value;
        var p = parsearListado(area.value);
        ayuda.textContent = textoContador(p);
        ayuda.classList.toggle('es-alerta', p.skus.length > MAX_SKUS);
        mostrarError('');
      });

      document.getElementById('cancelar').addEventListener('click', function () {
        estado.form = formDeOrden(3001);
        estado.form.listado = '';
        estado.aviso = 'Carga cancelada. No se guardó nada.';
        render('aviso');
      });

      document.getElementById('form-carga').addEventListener('submit', function (ev) {
        ev.preventDefault();
        var p = parsearListado(area.value);
        var msg = errorListado(p);
        if (msg) { mostrarError(msg); area.focus(); return; }
        mostrarError('');

        botonCargando(document.getElementById('cargar'), 'Cargando…');
        document.getElementById('cancelar').disabled = true;
        esperar(function () {
          estado.pedido = {
            id_orden: f.id_orden,
            id_cliente: orden(f.id_orden).id_cliente,
            tipo_movimiento: f.tipo_movimiento,
            modalidad: f.modalidad,
            lineas: p.skus.map(function (sku) {
              return { sku: sku, resultado: 'pendiente', vigente: true, cambio: null };
            })
          };
          estado.guia = null;
          estado.aviso = null;
          ir('p2');
        });
      });
    }
  };

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
