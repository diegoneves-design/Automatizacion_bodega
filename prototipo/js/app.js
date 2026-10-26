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

  /* ----- P2 Validar pedido (HU-01, HU-04) ----- */

  var PASTILLAS = {
    pendiente: ['p-neutra', 'Pendiente'],
    validando: ['p-neutra', 'Validando…'],
    ok: ['p-ok', '✓ ok'],
    no_existe: ['p-alerta', '✕ no existe'],
    no_disponible: ['p-alerta', '✕ sin stock']
  };

  function lineaHtml(l, validando) {
    var e = equipo(l.sku);
    var res = validando ? 'validando' : l.resultado;
    var pastilla = PASTILLAS[res];
    var clases = 'linea' + (!validando && conProblema(l) ? ' es-alerta' : '') + (l.cambio ? ' es-cambio' : '');
    var detalle = '';

    if (!validando && l.resultado === 'no_existe') {
      detalle = 'No está en el inventario. Revisa el código o cámbialo con Registrar cambio.';
    } else if (!validando && l.resultado === 'no_disponible') {
      detalle = 'El equipo está en mantención y no se puede despachar. Cámbialo con Registrar cambio.';
    }

    var cambio = '';
    if (l.cambio) {
      var u = usuario(l.cambio.id_usuario);
      cambio = '<p class="detalle cambio"><span aria-hidden="true">↻</span> Cambiado por ' + esc(u.nombre) + ' (' + esc(u.rol) +
        ') a las ' + esc(l.cambio.hora) + ' · reemplaza a ' + esc(l.cambio.sale) +
        (l.cambio.motivo ? ' · ' + esc(l.cambio.motivo) : '') + '</p>';
    }

    return '<li class="' + clases + '">' +
      '<div><div class="sku">' + esc(l.sku) + '</div>' +
      '<div class="desc">' + esc(e ? e.descripcion : '— (no se encuentra)') + '</div></div>' +
      '<span class="pastilla ' + pastilla[0] + '">' + esc(pastilla[1]) + '</span>' +
      (detalle ? '<p class="detalle">' + esc(detalle) + '</p>' : '') + cambio + '</li>';
  }

  VISTAS.p2 = {
    titulo: function () { return 'Validar pedido'; },

    html: function () {
      var p = estado.pedido;
      var v = vigentes();
      var validando = estado.validando;
      var pend = v.filter(function (l) { return l.resultado === 'pendiente'; }).length;
      var err = v.filter(conProblema).length;
      var modo = pend > 0 ? 'validar' : (err > 0 ? 'registrar' : 'preparar');
      var bloqueado = modo !== 'preparar';
      var aviso = estado.aviso;
      estado.aviso = null;

      var resumen;
      if (validando) {
        resumen = ['r-neutro', 'Validando el pedido…'];
      } else if (pend > 0) {
        resumen = ['r-neutro', plural(pend, 'producto sin validar', 'productos sin validar') + '. Presiona Validar para revisar.'];
      } else if (err > 0) {
        resumen = ['r-alerta', '✕ Corrige ' + plural(err, 'producto', 'productos') + ' para continuar'];
      } else {
        resumen = ['r-ok', '✓ ' + v.length + ' de ' + v.length + ' productos ok'];
      }

      function clase(m) { return 'boton ' + (modo === m ? 'boton-primario' : 'boton-secundario'); }

      return migas('p2') +
        '<a class="enlace volver" id="volver" href="#/p1"><span aria-hidden="true">‹</span> Volver</a>' +
        '<h1 id="titulo" tabindex="-1">Validar pedido · orden ' + p.id_orden + '</h1>' +
        '<p class="meta">' + esc(cliente(p.id_cliente).razon_social) + ' · ' + esc(etiqueta(D.tipos_movimiento, p.tipo_movimiento)) +
          ' · ' + esc(etiqueta(D.modalidades, p.modalidad)) + '</p>' +
        '<div class="aviso" id="aviso" role="status" aria-live="polite">' + esc(aviso || '') + '</div>' +
        '<div class="acciones acciones-arriba">' +
          '<button type="button" class="' + clase('validar') + (validando ? ' cargando' : '') + '" id="validar"' + (validando ? ' disabled aria-busy="true"' : '') + '>' +
            (validando ? '<span class="giro" aria-hidden="true"></span><span>Validando…</span>' : 'Validar') + '</button>' +
        '</div>' +
        '<ul class="lista" aria-label="Productos del pedido">' + v.map(function (l) { return lineaHtml(l, validando); }).join('') + '</ul>' +
        '<div class="resumen ' + resumen[0] + '" id="resumen" tabindex="-1" role="status" aria-live="polite">' + esc(resumen[1]) + '</div>' +
        '<div class="acciones">' +
          '<button type="button" class="' + (bloqueado ? 'boton boton-secundario' : clase('preparar')) + '" id="preparar"' + (bloqueado || validando ? ' disabled' : '') + '>' +
            (bloqueado ? 'Preparar guía (bloqueado)' : 'Preparar guía →') + '</button>' +
          '<button type="button" class="' + clase('registrar') + '" id="registrar"' + (validando ? ' disabled' : '') + '>Registrar cambio</button>' +
        '</div>';
    },

    enlazar: function () {
      document.getElementById('validar').addEventListener('click', function () {
        estado.validando = true;
        render('resumen');
        esperar(function () {
          vigentes().forEach(function (l) { l.resultado = resultadoSku(l.sku); });
          estado.validando = false;
          if (rutaActual() === 'p2') render('resumen');
        });
      });

      document.getElementById('preparar').addEventListener('click', function () {
        if (!todoOk()) return;
        estado.guia = { id_usuario: 1, fecha: new Date() };
        ir('p4');
      });

      document.getElementById('registrar').addEventListener('click', function () {
        abrirP3();
        ir('p3');
      });
    }
  };

  /* ----- P3 Registrar cambio (HU-03) ----- */

  function abrirP3() {
    var problema = vigentes().filter(conProblema)[0];
    estado.p3 = {
      sale: problema ? problema.sku : '',
      entra: '',
      motivo: problema ? (problema.resultado === 'no_existe' ? 'Código mal digitado' : 'Equipo en mantención') : '',
      id_usuario: 2
    };
  }

  function etiquetaSale(l) {
    var e = equipo(l.sku);
    if (!e) return l.sku + ' · no existe en el inventario';
    return l.sku + ' · ' + e.descripcion + (l.resultado === 'no_disponible' ? ' · sin stock' : '');
  }

  function etiquetaEntra(e) {
    return e.sku + ' · ' + e.descripcion + ' · ' + (e.estado === 'disponible' ? 'disponible' : 'sin stock');
  }

  VISTAS.p3 = {
    titulo: function () { return 'Registrar cambio'; },

    html: function () {
      if (!estado.p3) abrirP3();
      var f = estado.p3;
      var p = estado.pedido;

      var sale = [{ valor: '', etiqueta: 'Elige el equipo que sale' }].concat(vigentes().map(function (l) {
        return { valor: l.sku, etiqueta: etiquetaSale(l) };
      }));
      var entra = [{ valor: '', etiqueta: 'Elige el equipo que entra' }].concat(D.equipos.map(function (e) {
        return { valor: e.sku, etiqueta: etiquetaEntra(e) };
      }));
      var responsables = D.usuarios.map(function (u) {
        return { valor: u.id_usuario, etiqueta: u.nombre + ' · ' + u.rol };
      });

      return migas('p3') +
        '<h1 id="titulo" tabindex="-1">Registrar cambio · orden ' + p.id_orden + '</h1>' +
        '<p class="ayuda-pantalla">Cambia un equipo del pedido. La línea nueva queda destacada en la validación.</p>' +
        '<form id="form-cambio" novalidate>' +
          '<div class="campo"><label for="sale">Equipo que sale</label>' +
            '<select id="sale" aria-describedby="sale-error">' + opciones(sale, 'valor', 'etiqueta', f.sale) + '</select>' +
            '<p class="error" id="sale-error" role="alert"></p></div>' +
          '<div class="campo"><label for="entra">Equipo que entra</label>' +
            '<select id="entra" aria-describedby="entra-error">' + opciones(entra, 'valor', 'etiqueta', f.entra) + '</select>' +
            '<p class="error" id="entra-error" role="alert"></p></div>' +
          '<div class="campo"><label for="motivo">Motivo (opcional)</label>' +
            '<select id="motivo">' + opciones(D.motivos_cambio, 'valor', 'etiqueta', f.motivo) + '</select></div>' +
          '<div class="campo"><label for="responsable">Quién lo registra</label>' +
            '<select id="responsable">' + opciones(responsables, 'valor', 'etiqueta', f.id_usuario) + '</select>' +
            '<p class="ayuda">Fecha y hora: se guardan solas al presionar Guardar cambio (ahora, ' + hhmm(new Date()) + ').</p></div>' +
          '<div class="acciones">' +
            '<button type="submit" class="boton boton-primario" id="guardar">Guardar cambio →</button>' +
            '<button type="button" class="boton boton-secundario" id="volver-p2">Volver</button>' +
          '</div>' +
        '</form>';
    },

    enlazar: function () {
      var f = estado.p3;
      var selSale = document.getElementById('sale');
      var selEntra = document.getElementById('entra');
      var selMotivo = document.getElementById('motivo');
      var selResp = document.getElementById('responsable');

      function marcar(sel, msg) {
        var error = document.getElementById(sel.id + '-error');
        error.textContent = msg ? '✕ ' + msg : '';
        if (msg) sel.setAttribute('aria-invalid', 'true'); else sel.removeAttribute('aria-invalid');
      }

      selSale.addEventListener('change', function () {
        f.sale = selSale.value;
        marcar(selSale, '');
        var l = vigentes().filter(function (x) { return x.sku === f.sale; })[0];
        if (l && conProblema(l)) {
          f.motivo = l.resultado === 'no_existe' ? 'Código mal digitado' : 'Equipo en mantención';
          selMotivo.value = f.motivo;
        }
      });
      selEntra.addEventListener('change', function () { f.entra = selEntra.value; marcar(selEntra, ''); });
      selMotivo.addEventListener('change', function () { f.motivo = selMotivo.value; });
      selResp.addEventListener('change', function () { f.id_usuario = Number(selResp.value); });

      document.getElementById('volver-p2').addEventListener('click', function () {
        estado.p3 = null;
        ir('p2');
      });

      document.getElementById('form-cambio').addEventListener('submit', function (ev) {
        ev.preventDefault();
        var sale = selSale.value;
        var entra = selEntra.value;
        var errSale = '';
        var errEntra = '';

        if (!sale) errSale = 'Elige el equipo que sale.';
        if (!entra) errEntra = 'Elige el equipo que entra.';
        else if (entra === sale) errEntra = 'El equipo que entra debe ser distinto del que sale.';
        else if (vigentes().some(function (l) { return l.sku === entra; })) errEntra = 'Ese equipo ya está en el pedido. Elige otro.';

        marcar(selSale, errSale);
        marcar(selEntra, errEntra);
        if (errSale) { selSale.focus(); return; }
        if (errEntra) { selEntra.focus(); return; }

        botonCargando(document.getElementById('guardar'), 'Guardando…');
        document.getElementById('volver-p2').disabled = true;
        esperar(function () {
          var lineas = estado.pedido.lineas;
          var vieja = vigentes().filter(function (l) { return l.sku === sale; })[0];
          vieja.vigente = false;
          lineas.splice(lineas.indexOf(vieja) + 1, 0, {
            sku: entra,
            resultado: 'pendiente',
            vigente: true,
            cambio: { sale: sale, id_usuario: f.id_usuario, hora: hhmm(new Date()), motivo: f.motivo }
          });
          estado.p3 = null;
          estado.aviso = 'Cambio guardado. Presiona Validar para revisar la línea nueva.';
          ir('p2');
        });
      });
    }
  };

  /* ----- P4 Guía lista (HU-05) ----- */

  function textoGuia(p, u, fecha, v) {
    var lineas = [
      'GUIA DE EJEMPLO (PROTOTIPO, SIN VALIDEZ)',
      'Orden: ' + p.id_orden,
      'Cliente: ' + cliente(p.id_cliente).razon_social,
      'Tipo de movimiento: ' + etiqueta(D.tipos_movimiento, p.tipo_movimiento),
      'Modalidad: ' + etiqueta(D.modalidades, p.modalidad),
      'Preparada por: ' + u.nombre + ' (' + u.rol + ')',
      'Fecha de emision: ' + fechaHora(fecha),
      '',
      'Productos vigentes:'
    ];
    v.forEach(function (l) { lineas.push('- ' + l.sku + ' | ' + equipo(l.sku).descripcion); });
    lineas.push('', 'Total de equipos: ' + v.length);
    return lineas.join('\r\n');
  }

  function descargar(nombre, texto) {
    var blob = new Blob([texto], { type: 'text/plain;charset=utf-8' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = nombre;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }

  VISTAS.p4 = {
    titulo: function () { return 'Guía lista'; },

    html: function () {
      var p = estado.pedido;
      if (!estado.guia) estado.guia = { id_usuario: 1, fecha: new Date() };
      var u = usuario(estado.guia.id_usuario);
      var aviso = estado.aviso;
      estado.aviso = null;

      return migas('p4') +
        '<h1 id="titulo" tabindex="-1">Guía lista · orden ' + p.id_orden + '</h1>' +
        '<p class="meta">' + esc(cliente(p.id_cliente).razon_social) + ' · ' + esc(etiqueta(D.tipos_movimiento, p.tipo_movimiento)) +
          ' · ' + esc(etiqueta(D.modalidades, p.modalidad)) + '</p>' +
        '<p><strong>Productos vigentes</strong></p>' +
        '<ul class="guia-lista" aria-label="Productos vigentes de la guía">' + vigentes().map(function (l) {
          return '<li>' + esc(l.sku) + ' · ' + esc(equipo(l.sku).descripcion) + '</li>';
        }).join('') + '</ul>' +
        '<p class="preparada">Preparada por ' + esc(u.nombre) + ' · ' + esc(fechaHora(estado.guia.fecha)) + '</p>' +
        '<div class="resumen r-ok" id="resumen" tabindex="-1" role="status" aria-live="polite">✓ Lista para pasar al ERP</div>' +
        '<div class="aviso" id="aviso" role="status" aria-live="polite">' + esc(aviso || '') + '</div>' +
        '<div class="acciones">' +
          '<button type="button" class="boton boton-primario" id="descargar">Descargar para el ERP</button>' +
          '<button type="button" class="boton boton-secundario" id="volver-p1">Volver a cargar pedido</button>' +
        '</div>';
    },

    enlazar: function () {
      document.getElementById('volver-p1').addEventListener('click', function () { ir('p1'); });

      document.getElementById('descargar').addEventListener('click', function () {
        var boton = document.getElementById('descargar');
        botonCargando(boton, 'Preparando archivo…');
        document.getElementById('volver-p1').disabled = true;
        esperar(function () {
          var p = estado.pedido;
          var nombre = 'guia_orden_' + p.id_orden + '.txt';
          descargar(nombre, textoGuia(p, usuario(estado.guia.id_usuario), estado.guia.fecha, vigentes()));
          estado.aviso = 'Archivo descargado: ' + nombre;
          if (rutaActual() === 'p4') render('aviso');
        });
      });
    }
  };

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
